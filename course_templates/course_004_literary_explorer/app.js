// ===== 古典文学探索器 · 逻辑代码 =====
// 这个文件只负责“怎么显示”，真正显示的内容都来自 data/poems.json。
// 想换内容时，只改 JSON，不需要改这里。

// 保存从 JSON 加载的全部作品
var allPoems = [];
// 保存当前被选中的作品 id
var selectedId = "";

// 页面结构加载完成后开始工作
document.addEventListener("DOMContentLoaded", function () {
  loadPoems();
});

// 第 1 步：加载 data/poems.json
function loadPoems() {
  fetch("data/poems.json")
    .then(function (response) {
      // response.ok 为 false 表示服务器返回了错误状态
      if (!response.ok) {
        throw new Error("服务器返回状态码：" + response.status);
      }
      return response.json();
    })
    .then(function (data) {
      allPoems = data;

      // 依次完成：统计 -> 朝代下拉框 -> 绑定搜索/筛选 -> 渲染列表
      renderStats(allPoems);
      fillDynastyOptions(allPoems);
      bindControls();
      renderList(getFilteredPoems());
      showDetail("");
    })
    .catch(function (error) {
      // 加载失败时给出友好提示（常见原因：直接双击打开 index.html）
      showLoadError(error);
    });
}

// 把加载失败的原因显示在页面上
function showLoadError(error) {
  var listEl = document.getElementById("poem-list");
  var detailEl = document.getElementById("poem-detail");
  var message =
    "数据加载失败，无法读取 data/poems.json。<br><br>" +
    "请通过本地服务器访问本页面，而不要直接双击打开 index.html。<br>" +
    "正确做法：在本项目目录执行 <code>python -m http.server 8000</code>，" +
    "然后访问 <code>http://127.0.0.1:8000</code>。<br><br>" +
    "错误信息：" + error.message;

  listEl.innerHTML = "";
  detailEl.innerHTML = '<p class="error-tip">' + message + "</p>";
}

// 第 6 步：计算并显示基础统计（作品总数、去重后的作者数量、朝代分布）
// 数字全部由代码从 JSON 实时算出，页面上没有写死。
function renderStats(poems) {
  var total = poems.length;

  // 用对象当作集合，统计不重复的作者
  var authorSet = {};
  // 用对象统计每个朝代出现的次数
  var dynastyCount = {};

  poems.forEach(function (poem) {
    authorSet[poem.author] = true;
    if (dynastyCount[poem.dynasty]) {
      dynastyCount[poem.dynasty] = dynastyCount[poem.dynasty] + 1;
    } else {
      dynastyCount[poem.dynasty] = 1;
    }
  });

  var authorCount = Object.keys(authorSet).length;

  // 把朝代分布拼成“唐 15 · 宋 8 ...”这样的文字
  var dynastyKeys = Object.keys(dynastyCount);
  var dynastyParts = [];
  dynastyKeys.forEach(function (dynasty) {
    dynastyParts.push(dynasty + " " + dynastyCount[dynasty]);
  });
  var dynastyText = dynastyParts.join(" · ");

  document.getElementById("stat-total").textContent = total;
  document.getElementById("stat-authors").textContent = authorCount;
  document.getElementById("stat-dynasty").textContent = dynastyText || "--";
}

// 根据数据里的朝代，自动生成下拉框选项
function fillDynastyOptions(poems) {
  var selectEl = document.getElementById("dynasty-select");

  // 收集所有出现过的朝代（去重，并按出现顺序排列）
  var dynasties = [];
  poems.forEach(function (poem) {
    if (dynasties.indexOf(poem.dynasty) === -1) {
      dynasties.push(poem.dynasty);
    }
  });

  dynasties.forEach(function (dynasty) {
    var option = document.createElement("option");
    option.value = dynasty;
    option.textContent = dynasty;
    selectEl.appendChild(option);
  });
}

// 给搜索框和下拉框绑定事件
function bindControls() {
  var searchEl = document.getElementById("search-input");
  var selectEl = document.getElementById("dynasty-select");

  // 输入时实时筛选
  searchEl.addEventListener("input", function () {
    renderList(getFilteredPoems());
  });

  // 切换朝代时实时筛选
  selectEl.addEventListener("change", function () {
    renderList(getFilteredPoems());
  });
}

// 第 3 步：按关键词（标题或作者）和朝代筛选，两者可以叠加
function getFilteredPoems() {
  var keyword = document.getElementById("search-input").value.trim().toLowerCase();
  var dynasty = document.getElementById("dynasty-select").value;

  // filter 会保留满足条件的作品
  return allPoems.filter(function (poem) {
    // 关键词筛选：标题或作者命中即可（忽略大小写）
    var matchKeyword = false;
    if (keyword === "") {
      matchKeyword = true;
    } else {
      var title = poem.title.toLowerCase();
      var author = poem.author.toLowerCase();
      if (title.indexOf(keyword) !== -1 || author.indexOf(keyword) !== -1) {
        matchKeyword = true;
      }
    }

    // 朝代筛选：下拉框选“全部朝代”时 value 为空
    var matchDynasty = false;
    if (dynasty === "") {
      matchDynasty = true;
    } else if (poem.dynasty === dynasty) {
      matchDynasty = true;
    }

    return matchKeyword && matchDynasty;
  });
}

// 第 2 步：把作品渲染成列表
function renderList(poems) {
  var listEl = document.getElementById("poem-list");

  // 没有结果时给出提示，不报错、不白屏
  if (poems.length === 0) {
    listEl.innerHTML = '<li class="empty-tip">没有找到相关作品</li>';
    return;
  }

  var html = "";
  poems.forEach(function (poem) {
    var activeClass = "";
    if (poem.id === selectedId) {
      activeClass = " is-active";
    }
    html += '<li class="poem-item' + activeClass + '" data-id="' + poem.id + '">';
    html += '<span class="poem-item-title">' + escapeHtml(poem.title) + "</span>";
    html +=
      '<span class="poem-item-meta">' +
      escapeHtml(poem.dynasty) +
      " · " +
      escapeHtml(poem.author) +
      "</span>";
    html += "</li>";
  });

  listEl.innerHTML = html;

  // 第 4 步：给每个列表项绑定点击事件
  var items = listEl.querySelectorAll(".poem-item");
  items.forEach(function (item) {
    item.addEventListener("click", function () {
      var id = item.getAttribute("data-id");
      showDetail(id);
      renderList(getFilteredPoems());
    });
  });
}

// 第 5 步：在详情区显示某首作品的信息
function showDetail(id) {
  var detailEl = document.getElementById("poem-detail");

  // id 为空（刚打开页面或点击了空白）时显示提示
  if (!id) {
    selectedId = "";
    detailEl.innerHTML = '<p class="placeholder">请从左侧列表中点击一首作品。</p>';
    return;
  }

  // 按 id 在全部数据里找出这首作品
  var poem = null;
  allPoems.forEach(function (item) {
    if (item.id === id) {
      poem = item;
    }
  });

  if (!poem) {
    return;
  }

  selectedId = id;

  // 正文按“行”拼接，每行后面换行
  var contentLines = poem.content.join("\n");

  // 标签
  var tagsHtml = "";
  poem.tags.forEach(function (tag) {
    tagsHtml += '<span class="tag">' + escapeHtml(tag) + "</span>";
  });

  var html = "";
  html += "<h3>" + escapeHtml(poem.title) + "</h3>";
  html +=
    '<p class="detail-meta">' +
    escapeHtml(poem.dynasty) +
    " · " +
    escapeHtml(poem.author) +
    "</p>";
  html += '<div class="detail-content">' + escapeHtml(contentLines) + "</div>";
  html += '<div class="detail-tags">' + tagsHtml + "</div>";

  detailEl.innerHTML = html;
}

// 小工具：把特殊字符转义，避免内容破坏页面结构
function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}