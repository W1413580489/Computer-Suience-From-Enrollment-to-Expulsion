# 假登录系统 + 年级驱动个性化 — 实现方案

## 一、整体访问流程

```
访问 jnuxky.xyz
    │
    ├── localStorage 有用户记录 → 直接进入已登录主页
    │
    └── 无记录 → 显示登录界面
                   │
                   ├── [游客模式] → 进入当前主页（无个性化，无推荐区域）
                   │
                   └── 填写信息 → 点击「进入」
                                    ├── 软件类 → 个性化主页（年级驱动目的地卡片01）
                                    ├── 硬件类 → 当前主页 + 顶部黄色提示条
                                    └── 其他类 → 当前主页 + 顶部黄色提示条
```

## 二、登录界面（LoginView.vue）

- **布局**：全屏居中卡片，背景沿用双主题（zzz 深色 / ak 浅色）
- **昵称**：输入框，placeholder="输入你的昵称"
- **专业类别**：三张卡片横排（软件类 / 硬件类 / 其他类），点击选中高亮
- **年级**：四张卡片横排（大一 / 大二 / 大三 / 大四），点击选中高亮
- **进入按钮**：三个字段都填完才亮起，否则置灰
- **游客模式**：底部链接「游客模式浏览 →」，点击跳过登录
- **底部提示**：「数据仅保存在本浏览器，不会上传」

## 三、数据存储（userStore.ts）

```typescript
// localStorage key: "xkz_user"
interface UserProfile {
  nickname: string;
  grade: 1 | 2 | 3 | 4;
  major: 'software' | 'hardware' | 'other';
}
```

## 四、主页变化

### 4.1 Hero 区域（HomeView.vue）
保持现有 JNU Logo + "INFO SYSTEM 信息学院指南系统" 不变，下方增加一行年级副标题：
- 大一 → 新生指南 · 开启你的大学之旅
- 大二 → 学术规划 · 夯实专业基础
- 大三 → 项目实战 · 从理论到实践
- 大四 → 职涯启航 · 迈向职场第一步

### 4.2 目的地卡片（DestinationGrid.vue）
卡片01 根据年级变化，内容为年级对应的指南卡片（标题+描述+图片+链接），其余三张卡片不变：
- 大一 → 新生指南补缺
- 大二 → 学术发展规划
- 大三 → 邪修学习指南
- 大四 → 就业发展规划

### 4.3 硬件类/其他类
登录后显示当前主页全部内容 + 顶部黄色提示条「你选择的专业内容正在开发中，敬请期待」

### 4.4 游客模式
显示当前主页（无个性化内容，无目的地卡片01变化）

## 五、退出/切换入口

- **顶部导航栏右上角**：显示「昵称 · 大三 · 软件类」标签，点击弹出下拉菜单（切换身份 / 退出登录）
- **个人配置面板**：增加「切换身份」按钮 / 游客模式显示「登录以获取个性化推荐」

## 六、文件变更清单

| 操作 | 文件 |
|------|------|
| 新建 | `src/stores/userStore.ts` |
| 新建 | `src/views/LoginView.vue` |
| 新建 | `src/data/gradeContent.ts` |
| 修改 | `src/router/index.ts` |
| 修改 | `src/App.vue` |
| 修改 | `src/components/home/DestinationGrid.vue` |
| 修改 | `src/components/hud/HudTopBar.vue` |
| 修改 | `src/components/home/PersonalConfig.vue` |
| 修改 | `src/components/home/HomeView.vue` |