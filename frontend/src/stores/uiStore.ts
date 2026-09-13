// uiStore：全局 UI 抽屉开关状态。
// 背景：导航菜单「API 配置」与各页面（首页/问答/导师）都能打开同一个设置抽屉，
// 放在 store 里避免每个页面各自维护一份开关，也便于「AI 导师」页引导用户去配置。
import { defineStore } from 'pinia';

export const useUiStore = defineStore('ui', {
  state: () => ({
    settingsOpen: false,
  }),
  actions: {
    openSettings() {
      this.settingsOpen = true;
    },
    closeSettings() {
      this.settingsOpen = false;
    },
  },
});
