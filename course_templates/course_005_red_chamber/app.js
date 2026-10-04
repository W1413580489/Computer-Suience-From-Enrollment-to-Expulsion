// ============================================================
// 红楼梦人物关系探索器 —— 交互脚本
// 本文件只负责「怎么显示」；「显示什么」全部来自 data 目录下的 JSON 文件。
// 想改变图上的人物或关系，只需要修改 JSON，不需要改动本文件。
// ============================================================

// SVG 命名空间（创建 SVG 元素时必须使用）
var SVG_NS = "http://www.w3.org/2000/svg";

// 画布尺寸与节点半径（这些属于布局参数，不是数据）
var CANVAS_WIDTH = 900;
var CANVAS_HEIGHT = 620;
var NODE_RADIUS = 18;

// 全局状态
var state = {
  characters: [],      // 人物数组（来自 characters.json）
  relations: [],       // 关系数组（来自 relations.json）
  layout: {},          // 人物 id -> { x, y } 坐标
  selectedId: null,    // 当前选中的人物 id
  selectedType: "all"  // 当前筛选的关系类型，"all" 表示全部
};

// 常用 DOM 元素
var svg = document.getElementById("graph");
var infoContent = document.getElementById("info-content");
var messageBox = document.getElementById("message");
var searchInput = document.getElementById("search-input");
var typeFilter = document.getElementById("type-filter");

// ------------------------------------------------------------
// 一、启动：加载两个 JSON 文件
// ------------------------------------------------------------
function loadData() {
  Promise.all([
    fetch("data/characters.json").then(function (res) { return res.json(); }),
    fetch("data/relations.json").then(function (res) { return res.json(); })
  ])
    .then(function (result) {
      state.characters = result[0];
      state.relations = result[1];
      state.layout = computeLayout(state.characters);
      buildTypeFilter(state.relations); // 用数据里真实出现的类型生成下拉选项
      render();
    })
    .catch(function (error) {
      // fetch 失败时给出友好提示（最常见原因：直接双击打开了 index.html）
      showMessage(
        "数据加载失败：" + error.message +
        "。请在本项目目录下执行 python -m http.server 8000，" +
        "然后通过 http://127.0.0.1:8000 访问页面，而不要直接双击 index.html。"
      );
    });
}

// ------------------------------------------------------------
// 二、布局：按数组顺序把人物均匀分布在一个圆周上
// （学生不需要理解坐标算法，想改位置只需调整 JSON 中人物的先后顺序）
// ------------------------------------------------------------
function computeLayout(characters) {
  var layout = {};
  var count = characters.length;
  var centerX = CANVAS_WIDTH / 2;
  var centerY = CANVAS_HEIGHT / 2;
  var radiusX = CANVAS_WIDTH / 2 - 60;
  var radiusY = CANVAS_HEIGHT / 2 - 50;

  for (var i = 0; i < count; i++) {
    // 从正上方开始，顺时针均匀分布
    var angle = (2 * Math.PI * i) / count - Math.PI / 2;
    layout[characters[i].id] = {
      x: centerX + radiusX * Math.cos(angle),
      y: centerY + radiusY * Math.sin(angle)
    };
  }
  return layout;
}

// ------------------------------------------------------------
// 三、关系类型筛选下拉框：选项来自 relations.json 中真实出现的 type
// ------------------------------------------------------------
var TYPE_NAMES = {
  family: "亲属",
  friend: "朋友",
  love: "情爱",
  conflict: "冲突",
  other: "其他"
};

function buildTypeFilter(relations) {
  var seen = {};
  var order = [];
  relations.forEach(function (rel) {
    if (!seen[rel.type]) {
      seen[rel.type] = true;
      order.push(rel.type);
    }
  });

  // 保留第一个「全部」选项，再追加真实类型
  order.forEach(function (type) {
    var option = document.createElement("option");
    option.value = type;
    option.textContent = (TYPE_NAMES[type] || type) + "（" + type + "）";
    typeFilter.appendChild(option);
  });
}

// ------------------------------------------------------------
// 四、渲染：根据当前状态绘制关系线与人物节点
// ------------------------------------------------------------
function render() {
  // 清空画布，重新绘制
  while (svg.firstChild) {
    svg.removeChild(svg.firstChild);
  }

  var visibleRelations = getVisibleRelations();
  var visibleIds = getVisibleCharacterIds(visibleRelations);

  // 1) 先画关系线（在节点下方，避免遮挡）
  visibleRelations.forEach(function (rel) {
    drawLine(rel);
  });

  // 2) 再画人物节点与名称
  state.characters.forEach(function (person) {
    if (!visibleIds[person.id]) {
      return; // 被筛选隐藏的人物
    }
    drawNode(person);
  });
}

// 当前应当显示的关系（受类型筛选影响）
function getVisibleRelations() {
  if (state.selectedType === "all") {
    return state.relations;
  }
  return state.relations.filter(function (rel) {
    return rel.type === state.selectedType;
  });
}

// 当前应当显示的人物 id 集合（筛选后只保留参与了可见关系的人物）
function getVisibleCharacterIds(visibleRelations) {
  var ids = {};
  if (state.selectedType === "all") {
    // 全部模式下显示所有人物
    state.characters.forEach(function (person) {
      ids[person.id] = true;
    });
    return ids;
  }
  visibleRelations.forEach(function (rel) {
    ids[rel.source] = true;
    ids[rel.target] = true;
  });
  return ids;
}

// 绘制一条关系线
function drawLine(rel) {
  var start = state.layout[rel.source];
  var end = state.layout[rel.target];
  if (!start || !end) {
    return; // 数据引用不到坐标时安全跳过
  }

  var line = document.createElementNS(SVG_NS, "line");
  line.setAttribute("x1", start.x);
  line.setAttribute("y1", start.y);
  line.setAttribute("x2", end.x);
  line.setAttribute("y2", end.y);
  line.setAttribute("class", "relation-line");
  line.setAttribute("data-source", rel.source);
  line.setAttribute("data-target", rel.target);

  // 若该关系与当前选中人物相关，则高亮
  if (isRelationHighlighted(rel)) {
    line.classList.add("highlight");
  }
  svg.appendChild(line);

  // 在线中点显示简短的关系说明
  var label = document.createElementNS(SVG_NS, "text");
  label.setAttribute("x", (start.x + end.x) / 2);
  label.setAttribute("y", (start.y + end.y) / 2);
  label.setAttribute("class", "relation-label");
  label.textContent = rel.label || "";
  svg.appendChild(label);
}

// 绘制一个人物节点与名称
function drawNode(person) {
  var pos = state.layout[person.id];

  var circle = document.createElementNS(SVG_NS, "circle");
  circle.setAttribute("cx", pos.x);
  circle.setAttribute("cy", pos.y);
  circle.setAttribute("r", NODE_RADIUS);
  circle.setAttribute("class", "person-node");
  circle.setAttribute("data-id", person.id);

  if (person.id === state.selectedId) {
    circle.classList.add("highlight"); // 选中的人物
  } else if (state.selectedId && isNeighbor(person.id, state.selectedId)) {
    circle.classList.add("neighbor");  // 与选中人物直接相关的人物
  }

  // 点击人物：高亮并显示信息
  circle.addEventListener("click", function (event) {
    event.stopPropagation(); // 阻止冒泡，避免触发"点击空白清除"
    selectPerson(person.id);
  });

  svg.appendChild(circle);

  // 人物名称文字
  var text = document.createElementNS(SVG_NS, "text");
  text.setAttribute("x", pos.x);
  text.setAttribute("y", pos.y + NODE_RADIUS + 14);
  text.setAttribute("class", "person-label");
  if (person.id === state.selectedId) {
    text.classList.add("highlight");
  }
  text.textContent = person.name;
  svg.appendChild(text);
}

// ------------------------------------------------------------
// 五、高亮判断与选中逻辑
// ------------------------------------------------------------
// 该关系是否与当前选中人物直接相关（source 或 target 都可以）
function isRelationHighlighted(rel) {
  if (!state.selectedId) {
    return false;
  }
  return rel.source === state.selectedId || rel.target === state.selectedId;
}

// 判断某个 id 是否是选中人物的邻接人物
function isNeighbor(id, selectedId) {
  if (id === selectedId) {
    return false;
  }
  return state.relations.some(function (rel) {
    return (rel.source === selectedId && rel.target === id) ||
           (rel.target === selectedId && rel.source === id);
  });
}

// 选中某个人物
function selectPerson(id) {
  state.selectedId = id;
  render();
  showPersonInfo(id);
}

// 清除选中状态
function clearSelection() {
  state.selectedId = null;
  render();
  infoContent.innerHTML = '<p class="placeholder">点击图中任意人物查看详情。</p>';
}

// ------------------------------------------------------------
// 六、信息面板
// ------------------------------------------------------------
function showPersonInfo(id) {
  var person = findCharacter(id);
  if (!person) {
    return;
  }

  // 找出与该人物直接相关的所有关系（source 与 target 两种情况都匹配）
  var related = state.relations.filter(function (rel) {
    return rel.source === id || rel.target === id;
  });

  var html = "";
  html += '<p class="info-name">' + person.name + "</p>";
  html += '<span class="info-family">' + person.family + "</span>";
  html += '<p class="info-desc">' + person.description + "</p>";

  html += '<p class="info-relations-title">直接关系（' + related.length + "）</p>";
  if (related.length === 0) {
    html += '<p class="placeholder">暂无直接关系。</p>';
  } else {
    html += '<ul class="info-relations">';
    related.forEach(function (rel) {
      // 找出关系另一头的人物
      var otherId = rel.source === id ? rel.target : rel.source;
      var other = findCharacter(otherId);
      var otherName = other ? other.name : otherId;
      html += "<li>" + otherName + "（" + (rel.label || "") + "）</li>";
    });
    html += "</ul>";
  }

  infoContent.innerHTML = html;
}

// 根据 id 查找人物
function findCharacter(id) {
  for (var i = 0; i < state.characters.length; i++) {
    if (state.characters[i].id === id) {
      return state.characters[i];
    }
  }
  return null;
}

// ------------------------------------------------------------
// 七、搜索
// ------------------------------------------------------------
function handleSearch() {
  var keyword = searchInput.value.trim();
  if (keyword === "") {
    clearSelection();
    hideMessage();
    return;
  }

  // 找出第一个名称包含关键字的（或 id 完全匹配的）人物
  var matched = null;
  for (var i = 0; i < state.characters.length; i++) {
    var person = state.characters[i];
    if (person.name.indexOf(keyword) !== -1 || person.id === keyword) {
      matched = person;
      break;
    }
  }

  if (matched) {
    // 若有类型筛选，先切回"全部"以便看到该人物
    hideMessage();
    selectPerson(matched.id);
  } else {
    // 没有找到：给出提示但不崩溃
    state.selectedId = null;
    render();
    showMessage('没有找到名字包含“' + keyword + '”的人物，请换个关键字试试。');
  }
}

// ------------------------------------------------------------
// 八、事件绑定
// ------------------------------------------------------------
// 搜索框实时搜索
searchInput.addEventListener("input", handleSearch);

// 关系类型筛选
typeFilter.addEventListener("change", function () {
  state.selectedType = typeFilter.value;
  render();
});

// 点击空白处（背景）清除上一次高亮
svg.addEventListener("click", function () {
  clearSelection();
});

// ------------------------------------------------------------
// 九、提示信息
// ------------------------------------------------------------
function showMessage(text) {
  messageBox.textContent = text;
  messageBox.hidden = false;
}

function hideMessage() {
  messageBox.textContent = "";
  messageBox.hidden = true;
}

// ------------------------------------------------------------
// 启动应用
// ------------------------------------------------------------
loadData();