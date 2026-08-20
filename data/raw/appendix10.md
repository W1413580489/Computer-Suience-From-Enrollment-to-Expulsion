<title>AntX6快速上手</title>

# 官方链接

[快速上手 | X6 图编辑引擎 (antgroup.com)](https://x6.antv.antgroup.com/tutorial/getting-started)

# 使用vh vw不要用100%避免布局错乱

# 函数命名规范 动词 + 事件名 + 事件触发动词：

handle **+** DrawRect **+** Click

# 初始化new Graph

## 创建dom容器并获取

初始值为null，在元素挂载后，生命周期mounted中才能获取元素



```HTML
  <div class="outside-container" ref="outsideContainer">
    <div class="graph-canvas-container" ref="graphCanvasContainer"></div>
  </div>
```

```JavaScript
const graphCanvasContainer = ref<HTMLDivElement>(); // 获取dom节点，将他作为new Graph的参数
let graph: Graph | null = null; // 作为存储 new Graph返回的实例的变量

//创建一个initGraph函数
function initGraph(): void {
  graph = new Graph({
    container: graphCanvasContainer.value,
    width: getOutsideContainerWidth() / 2,// 以父节点宽度的一半作为画布的宽度，多余操作可以根据需求修改
    height: getOutsideContainerHeight() * 0.8,// 以父节点高度的80%作为画布的宽度，多余操作可以根据需求修改
    background: {
      color: "#f5f5f5",
    },
    // 网格配置
    grid: { size: 10, visible: true, type: "dot" },
    // 拖动配置，开启拖动功能需要按住空格键
    panning: { enabled: true, modifiers: ["space"] },
    // 鼠标滚轮配置，开启缩放功能，必须按住ctrl键
    mousewheel: {
      enabled: true,
      zoomAtMousePosition: true,
      modifiers: ["ctrl"],
    },
  });
```

```TypeScript
    // 拖动配置，开启拖动功能需要按住空格键
    panning: { enabled: true, modifiers: ["space"] },
```

可以限制拖拽画布的条件，必须按住space

类似的限制缩放，通过ctrl

## 初始化配置

鼠标滚动mousewheel

Enaled: boolean 开启/关闭

zoomAtMousePosition:boolean 是否根据鼠标位置缩放（推荐为true）

```TypeScript
    // 鼠标滚轮配置，开启缩放功能，必须按住ctrl键
    mousewheel: {
      enabled: true,
      zoomAtMousePosition: true,
      modifiers: ["ctrl"],
    },
```

# 添加Node节点addNode

通过this.graph拿到对象实例。调用addNode方法，生成固定位置的节点node

```JavaScript
const rect = this.graph.addNode({
          id: "node-1", // 手动指定 id，方便后面引用
          shape: "rect",// 矩形
          x: 100,// 左上角坐标写死
          y: 100,
          width: 120,
          height: 60,
          attrs: {
            body: {
              fill: "#E6F7FF", // 填充色：浅蓝
              stroke: "#1890FF", // 边框色：蓝色
              rx: 4,
              ry: 4, // 圆角
            },
            label: {
              text: "开始节点",
              fill: "#1890FF",
              fontSize: 14,
            },
          },
        });

```

## 节点初始化的坐标会被缩放改变

<grid>
<column width-ratio="0.366627">
![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MTVlZDhlMTVhYTg0YTNjZjdhNTU5OGZkNDRkMmZjM2VfYjczYjliOTAwNWE2NTdjZGExZjk4ZTBiZjg5OTIwZmFfSUQ6NzY2OTczNjk5ODcwNjE4NzIwOV8xNzg2ODgzMDk4OjE3ODY4ODY2OThfVjM)
</column>
<column width-ratio="0.633373">
![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OGExMjBhMzc3MWY4YmZjOTk1ZTg5ODAzY2Y1ZDIwMjRfOTZkMzkxZDc5ZjVlNjhmOTkyZmVkYWY4NDFiOTE3OWFfSUQ6NzY2OTczNzE4NzcxMzQ4NTc3N18xNzg2ODgzMDk4OjE3ODY4ODY2OThfVjM)
</column>
</grid>

# 通过交互逻辑的方式添加节点

## 监听鼠标事件：整体是个三段式状态机：按下 → 拖动 → 松开。

```TypeScript
// 当前选中的绘制工具
drawMode: null | 'rect' | 'circle'
/** 是否正在绘制节点 true: 正在绘制节点 false: 未绘制节点状态 */
let isDrawing: boolean = false;
// tempNode的leftTop坐标，会因为事件blank:move 
// 重新设置调用tempNode.setPosition(LeftTopX, LeftTopY); // 设置节点位置
let startPoint: { x: number; y: number }; 
// 拖拽过程中实时变化的预览图形
let tempNode: ReturnType<typeof Graph.prototype.addNode> | null = null; 
```

### 1. blank:mousedown —— 落笔

```TypeScript
  // 绑定空白处点击事件
  graph.on("blank:mousedown", ({ e, x, y }) => {
    console.log("点击了画布空白处");
    console.log("坐标:", x, y); // 画布坐标系中的位置
    console.log("原生事件:", e); // 原生 MouseEvent
    isDrawing = true;
    startPoint = { x, y };

    // 示例：在点击位置添加一个节点
    tempNode = graph!.addNode({
      x: x, // 左上角坐标x
      y: y, // 左上角坐标y
      width: 0,
      height: 0,
      shape: "rect",
      label: "新节点",
      attrs: {
        body: {
          fill: "#E6F7FF",
          stroke: "#1890FF",
          rx: 4,
          ry: 4,
          strokeWidth: 2,
          strokeDasharray: "5 2",
        },
        label: { fill: "#1890FF", fontSize: 14 },
      },
    });
  });
```

首先让graph的坐标根据当前鼠标坐标，内部通过计算返回新的坐标

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MDBiOTk2Y2E1MTFhMmM3YzI4NmM2ZmZhNjRmZGMyN2RfMzdiMzMxZWVkODg4YTc3ZmI2NTYwOTYzYjQzNzBiY2NfSUQ6NzY3MDA5NDgxMzAyMjk5NzQ1NF8xNzg2ODgzMDk4OjE3ODY4ODY2OThfVjM)

以这个画布坐标为图形的起始坐标，宽度高度初始化为0

其他的配置config根据常量中当前shape的配置获取默认值

```JavaScript
  // 绑定空白处点击事件
  graph.on("blank:mousedown", ({ e, x, y }) => {
    console.log("点击了画布空白处");
    console.log("坐标:", x, y); // 画布坐标系中的位置
    console.log("原生事件:", e); // 原生 MouseEvent
    isDrawing = true;
    startPoint = { x, y };

    // 示例：在点击位置添加一个节点
    tempNode = graph!.addNode({
      x: x, // 左上角坐标x
      y: y, // 左上角坐标y
      width: 0,
      height: 0,
      shape: "rect",
      label: "新节点",
      attrs: {
        body: {
          fill: "#E6F7FF",
          stroke: "#1890FF",
          rx: 4,
          ry: 4,
          strokeWidth: 2,
          strokeDasharray: "5 2",
        },
        label: { fill: "#1890FF", fontSize: 14 },
      },
    });
  });
```

### blank:mousemove——移动

```TypeScript
  // 2. 全局 mousemove：不管鼠标在空白处还是节点上，都能触发
  graph.on("blank:mousemove", ({ e, x, y }) => {
    if (!isDrawing || !tempNode) return;

    const dx = x - startPoint.x;
    const dy = y - startPoint.y;

    let LeftTopX = startPoint.x;
    let LeftTopY = startPoint.y;
    let realW = dx;
    let realH = dy;

    // 处理向左/向上拖拽
    if (dx < 0) {
      LeftTopX = x;
      realW = -dx;
    }
    if (dy < 0) {
      LeftTopY = y;
      realH = -dy;
    }

    // 最小尺寸限制，避免太小看不见
    if (realW < 10) realW = 10;
    if (realH < 10) realH = 10;

    tempNode.setPosition(LeftTopX, LeftTopY); // 设置节点位置
    tempNode.setSize(realW, realH); // 设置节点尺寸
  });
```

### blank:mouseup ——松开鼠标

```JavaScript
  // 3. 全局 mouseup：松开鼠标后触发
  graph.on("blank:mouseup", () => {
    if (!isDrawing || !tempNode) return;

    const { width, height } = tempNode.size();

    // 如果尺寸太小，直接删除（视为误触）
    if (width < 20 || height < 20) {
      tempNode.remove();
      tempNode = null;
      isDrawing = false;
      return;
    }

    // 完成创建：去掉虚线，加上文字
    tempNode.setAttrs({
      body: {
        fill: "#E6F7FF",
        stroke: "#1890FF",
        strokeWidth: 1,
        strokeDasharray: "0", // 去掉虚线
      },
      label: {
        text: "新节点",
        fill: "#1890FF",
        fontSize: 14,
      },
    });

    tempNode = null; // 清空临时节点引用，避免内存泄漏
    isDrawing = false;
  });
```

#### 快速体验一下https://graph-canvas-antx6.netlify.app/



## 通过拖拽交互：插件dnd + mousedown

### 初始化dnd实例

getDragNode：拖动的时候node的样式

getDropNode：放置后node的样式

```JavaScript
  /** 初始化拖动实例 */
  function initDnd() {
    dnd.value = new Dnd({
      target: graphInstance.value!,
      // 拖拽过程中的节点样式（虚线预览）
      getDragNode(sourceNode) {...},
      // 放置到画布上的最终节点样式（实线正式节点）
      getDropNode(draggingNode) {...}
    });
  }
```

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OGU1Zjc1MmNmYTAxMDc0NjQ1MDc2YjZhYTU4NmY3OTdfZGZmODJiZTAwYzJjYWRlNTliMDkzMjQzNmMyYzZkNTlfSUQ6NzY3MDU3Njc1MzM3NDQxNTg2MF8xNzg2ODgzMDk4OjE3ODY4ODY2OThfVjM)

拖拽官方链接：http://x6.antv.antgroup.com/tutorial/plugins/dnd
