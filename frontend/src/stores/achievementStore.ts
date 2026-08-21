// achievementStore：成就系统的响应式单一数据源。
// 所有解锁动作通过本 store 触发，实时同步到票据展示与解锁提示，无需刷新。
import { defineStore } from 'pinia';
import {
  ACHIEVEMENTS,
  loadStore,
  saveStore,
  STORAGE_KEY,
  type AchievementDef,
} from '@/data/achievements';

export const useAchievementStore = defineStore('achievement', {
  state: () => {
    const data = loadStore();
    return {
      // id -> 解锁 ISO 时间戳（'' 表示未解锁）
      unlockedAtMap: Object.fromEntries(
        Object.entries(data).map(([k, v]) => [k, v.unlockedAt ?? '']),
      ) as Record<string, string>,
      // 待提示的解锁队列（票据式提示消费后移出）
      toastQueue: [] as AchievementDef[],
    };
  },
  getters: {
    /** 已解锁成就，按解锁时间倒序 */
    unlocked(state): AchievementDef[] {
      return ACHIEVEMENTS.filter((a) => state.unlockedAtMap[a.id])
        .slice()
        .sort((x, y) => (state.unlockedAtMap[y.id] ?? '').localeCompare(state.unlockedAtMap[x.id] ?? ''));
    },
    unlockedCount(state): number {
      return ACHIEVEMENTS.filter((a) => state.unlockedAtMap[a.id]).length;
    },
  },
  actions: {
    /** 解锁成就：持久化 + 更新响应式状态 + 入队解锁提示。已解锁返回 false。 */
    unlock(id: string): boolean {
      if (this.unlockedAtMap[id]) return false;
      const now = new Date().toISOString();
      this.unlockedAtMap[id] = now;
      const data = loadStore();
      data[id] = { id, unlocked: true, unlockedAt: now };
      saveStore(data);
      const def = ACHIEVEMENTS.find((a) => a.id === id);
      if (def) this.toastQueue.push(def);
      return true;
    },
    /** 查询是否已解锁 */
    isUnlocked(id: string): boolean {
      return !!this.unlockedAtMap[id];
    },
    /** 从 localStorage 重新同步（跨标签页 / storage 事件） */
    reload() {
      const data = loadStore();
      this.unlockedAtMap = Object.fromEntries(
        Object.entries(data).map(([k, v]) => [k, v.unlockedAt ?? '']),
      );
    },
    /** 消费队列头部提示 */
    shiftToast(): AchievementDef | undefined {
      return this.toastQueue.shift();
    },
  },
});

/** 监听成就存储变化（跨标签页同步） */
export function subscribeAchievementStaleness(callback: () => void): () => void {
  const handler = (e: StorageEvent) => {
    if (e.key === STORAGE_KEY) callback();
  };
  window.addEventListener('storage', handler);
  return () => window.removeEventListener('storage', handler);
}