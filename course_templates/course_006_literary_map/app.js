// ===========================================================
// 文学地图 · 学生起始模板
// 本文件只负责“怎么显示”：从 data/*.json 读取数据并渲染到页面上。
// 想改变地图或故事内容，请修改 data/places.json 与 data/stories.json，
// 不要修改本文件。
// ===========================================================

// 从 JSON 读取到的数据
var places = [];   // 地点列表
var stories = [];  // 故事列表（加载后会按 order 排序）

// 当前正在浏览的故事下标（对应排序后的 stories 数组）
var currentIndex = 0;

// 保存地图上每个地点的图形元素，方便做高亮：{ placeId: { circle, text } }
var placeElements = {};

// 创建 SVG 元素时需要指定命名空间
var SVG_NS = "http://www.w3.org/2000/svg";

// 页面加载完成后启动（script 标签用了 defer，此时 DOM 已就绪）
document.addEventListener("DOMContentLoaded", init);

function init() {
  loadData();
}

// 第一步：加载两个 JSON 数据文件
function loadData() {
  Promise.all([
    fetch("data/places.json").then(function (res) {
      if (!res.ok) {
        throw new Error("places.json 读取失败");
      }
      return res.json();
    }),
    fetch("data/stories.json").then(function (res) {
      if (!res.ok) {
        throw new Error("stories.json 读取失败");
      }
      return res.json();
    })
  ])
    .then(function (result) {
      places = result[0];
      stories = result[1];

      // 按 order 从小到大排序，决定故事的先后顺序
      stories.sort(function (a, b) {
        return a.order - b.order;
      });

      // 第二步：画地图（先画路线，再画地点，保证地点显示在路线之上）
      drawRoute();
      drawPlaces();

      // 第三步：绑定“上一个 / 下一个”按钮
      bindControls();

      // 第四步：默认展示第一条故事
      if (stories.length > 0) {
        showStory(0);
      } else {
        showEmpty();
      }
    })
    .catch(function (err) {
      // fetch 失败（例如直接双击打开 index.html）时给出友好提示
      showError();
      console.error(err);
    });
}

// 画示意路线：按故事 order 的先后，把出现过的不同地点依次连起来
function drawRoute() {
  var svg = document.getElementById("map");

  // 记录地点第一次出现的先后顺序
  var orderedPlaceIds = [];
  stories.forEach(function (story) {
    if (orderedPlaceIds.indexOf(story.place_id) === -1) {
      orderedPlaceIds.push(story.place_id);
    }
  });

  // 转换成 SVG 的坐标点字符串，例如 "320,340 300,220"
  var points = [];
  orderedPlaceIds.forEach(function (id) {
    var place = getPlaceById(id);
    if (place) {
      points.push(place.x + "," + place.y);
    }
  });

  // 少于两个点就画不出线，直接返回
  if (points.length < 2) {
    return;
  }

  var polyline = document.createElementNS(SVG_NS, "polyline");
  polyline.setAttribute("points", points.join(" "));
  polyline.setAttribute("class", "route-line");
  svg.appendChild(polyline);
}

// 画地点节点：每个地点一个圆点 + 一行名称文字
function drawPlaces() {
  var svg = document.getElementById("map");

  places.forEach(function (place) {
    // 圆形节点，位置来自 JSON 里的示意坐标 x、y
    var circle = document.createElementNS(SVG_NS, "circle");
    circle.setAttribute("cx", place.x);
    circle.setAttribute("cy", place.y);
    circle.setAttribute("r", 12);
    circle.setAttribute("class", "place-node");
    // 点击地点：显示该地点对应的故事
    circle.addEventListener("click", function () {
      onPlaceClick(place.id);
    });

    // 地点名称文字，放在圆点下方
    var text = document.createElementNS(SVG_NS, "text");
    text.setAttribute("x", place.x);
    text.setAttribute("y", Number(place.y) + 30);
    text.setAttribute("class", "place-label");
    text.textContent = place.name;
    // 点击名称也能触发同样效果
    text.addEventListener("click", function () {
      onPlaceClick(place.id);
    });

    svg.appendChild(circle);
    svg.appendChild(text);

    // 记住这两个元素，方便后面高亮
    placeElements[place.id] = { circle: circle, text: text };
  });
}

// 绑定“上一个 / 下一个”按钮
function bindControls() {
  document.getElementById("prev-btn").addEventListener("click", function () {
    goToStory(currentIndex - 1);
  });
  document.getElementById("next-btn").addEventListener("click", function () {
    goToStory(currentIndex + 1);
  });
}

// 按顺序切换故事，并做好边界处理（不越界、不报错）
function goToStory(index) {
  if (stories.length === 0) {
    return;
  }
  // 第一个再往前，停在第一个
  if (index < 0) {
    index = 0;
  }
  // 最后一个再往后，停在最后一个
  if (index > stories.length - 1) {
    index = stories.length - 1;
  }
  showStory(index);
}

// 点击某个地点时：显示该地点的第一条故事（stories 已按 order 排序）
function onPlaceClick(placeId) {
  var index = -1;
  for (var i = 0; i < stories.length; i++) {
    if (stories[i].place_id === placeId) {
      index = i;
      break;
    }
  }

  // 该地点暂时没有故事时的友好处理
  if (index === -1) {
    highlightPlace(placeId);
    var place = getPlaceById(placeId);
    document.getElementById("current-place").textContent = place ? place.name : "未知地点";
    document.getElementById("story-time").textContent = "—";
    document.getElementById("story-title").textContent = "暂无故事";
    document.getElementById("story-body").textContent =
      "该地点在 stories.json 中还没有对应的故事。";
    return;
  }

  showStory(index);
}

// 显示指定下标的故事情息，并同步高亮地图上的地点
function showStory(index) {
  if (stories.length === 0) {
    return;
  }
  currentIndex = index;
  var story = stories[index];
  var place = getPlaceById(story.place_id);

  // 更新故事面板：时间 / 标题 / 正文 / 当前地点，全部来自 JSON
  document.getElementById("current-place").textContent = place ? place.name : "未知地点";
  document.getElementById("story-time").textContent = story.time;
  document.getElementById("story-title").textContent = story.title;
  document.getElementById("story-body").textContent = story.body;
  document.getElementById("story-progress").textContent =
    "第 " + (index + 1) + " / " + stories.length + " 条";

  // 同步高亮地图上对应的地点
  highlightPlace(story.place_id);

  // 到达两端时把对应按钮禁用，给用户直观反馈
  document.getElementById("prev-btn").disabled = (index === 0);
  document.getElementById("next-btn").disabled = (index === stories.length - 1);
}

// 高亮某个地点：先清掉所有高亮，再给目标地点加上高亮样式
function highlightPlace(placeId) {
  Object.keys(placeElements).forEach(function (id) {
    placeElements[id].circle.classList.remove("place-active");
    placeElements[id].text.classList.remove("place-label-active");
  });

  if (placeElements[placeId]) {
    placeElements[placeId].circle.classList.add("place-active");
    placeElements[placeId].text.classList.add("place-label-active");
  }
}

// 根据 id 找到对应的地点
function getPlaceById(id) {
  for (var i = 0; i < places.length; i++) {
    if (places[i].id === id) {
      return places[i];
    }
  }
  return null;
}

// 数据为空时的显示
function showEmpty() {
  document.getElementById("current-place").textContent = "—";
  document.getElementById("story-time").textContent = "—";
  document.getElementById("story-title").textContent = "暂无数据";
  document.getElementById("story-body").textContent = "请先在 data 文件夹中填写地点与故事。";
}

// 加载失败时的友好提示
function showError() {
  var svg = document.getElementById("map");
  svg.innerHTML = "";

  var text = document.createElementNS(SVG_NS, "text");
  text.setAttribute("x", 30);
  text.setAttribute("y", 60);
  text.setAttribute("class", "map-error");
  text.textContent = "数据加载失败：请通过本地服务器访问本页，不要直接双击 index.html。";
  svg.appendChild(text);

  document.getElementById("current-place").textContent = "—";
  document.getElementById("story-time").textContent = "—";
  document.getElementById("story-title").textContent = "无法加载数据";
  document.getElementById("story-body").textContent =
    "请在项目目录运行 python -m http.server 8000，然后访问 http://127.0.0.1:8000";
}