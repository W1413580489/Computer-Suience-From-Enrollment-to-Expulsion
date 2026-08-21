// themeStore：日夜间模式切换。
// 夜间 zzz = 绝区零风格（默认），日间 ak = 明日方舟风格。
// 通过 <html data-theme="zzz|ak"> 切换 CSS 变量，持久化到 localStorage。
import { defineStore } from 'pinia';
import { unlockAchievement } from '@/data/achievements';

export type ThemeMode = 'zzz' | 'ak';

const LS_KEY = 'xkz_theme_v1';

function loadFromLocal(): ThemeMode {
  try {
    const v = localStorage.getItem(LS_KEY);
    if (v === 'ak' || v === 'zzz') return v;
  } catch {
    /* localStorage 不可用时忽略 */
  }
  return 'zzz';
}

/** 将主题写入 <html data-theme="...">，供 CSS 变量切换使用 */
export function applyThemeAttr(mode: ThemeMode) {
  document.documentElement.setAttribute('data-theme', mode);
}

export const useThemeStore = defineStore('theme', {
  state: (): { mode: ThemeMode } => ({ mode: loadFromLocal() }),
  getters: {
    isAk: (s) => s.mode === 'ak',
    isZzz: (s) => s.mode === 'zzz',
  },
  actions: {
    /** 应用当前 mode 到 DOM（初始化与切换后调用） */
    apply() {
      applyThemeAttr(this.mode);
    },
    toggle() {
      this.mode = this.mode === 'zzz' ? 'ak' : 'zzz';
      this.persist();
      this.apply();
      // 成就：切换日夜间主题
      unlockAchievement('see_you_tomorrow');
      if (this.mode === 'zzz') unlockAchievement('welcome_new_eridu');
    },
    set(mode: ThemeMode) {
      this.mode = mode;
      this.persist();
      this.apply();
      // 成就：进入夜间 zzz 模式
      if (mode === 'zzz') unlockAchievement('welcome_new_eridu');
    },
    persist() {
      try {
        localStorage.setItem(LS_KEY, this.mode);
      } catch {
        /* 忽略 */
      }
    },
  },
});
