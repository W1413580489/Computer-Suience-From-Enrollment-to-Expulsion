// 新手任务进度 —— localStorage 持久化，零后端
export interface QuestProgress {
  /** 勾选的装备清单项 ID 集合 */
  equipment: string[];
  /** 已分配技能点 (skill_id -> points) */
  skills: Record<string, number>;
  /** 当前消耗技能点 */
  skillPointsSpent: number;
  /** 主线任务完成索引 */
  mainComplete: number[];
  /** 地图探索地点 */
  explored: string[];
  /** 是否已完成首次引导 */
  hasSeenIntro: boolean;
}

const STORAGE_KEY = 'xkz_quest';
const MAX_SKILL_POINTS = 6;

export function loadProgress(): QuestProgress {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* corrupted, rebuild */ }
  return {
    equipment: [],
    skills: {},
    skillPointsSpent: 0,
    mainComplete: [],
    explored: [],
    hasSeenIntro: false,
  };
}

export function saveProgress(p: QuestProgress) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(p));
}

export function canAllocateSkill(p: QuestProgress): boolean {
  return p.skillPointsSpent < MAX_SKILL_POINTS;
}

export { MAX_SKILL_POINTS };
