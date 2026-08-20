// 年级里程碑勾选进度 —— localStorage 持久化，零后端
// 结构：Record<grade, string[]>（年级 → 已勾选里程碑 item id 数组）
export type MilestoneProgress = Record<number, string[]>;

const STORAGE_KEY = 'xkz_milestones';

export function loadMilestones(): MilestoneProgress {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    /* corrupted, rebuild */
  }
  return {};
}

export function saveMilestones(p: MilestoneProgress) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(p));
}

/** 勾选/取消某项，返回更新后的完整进度 */
export function toggleMilestone(
  p: MilestoneProgress,
  grade: number,
  itemId: string,
): MilestoneProgress {
  const checked = p[grade] ?? [];
  const idx = checked.indexOf(itemId);
  const next = idx >= 0 ? checked.filter((id) => id !== itemId) : [...checked, itemId];
  const updated = { ...p, [grade]: next };
  saveMilestones(updated);
  return updated;
}

/** 某年级某项是否已勾选 */
export function isChecked(p: MilestoneProgress, grade: number, itemId: string): boolean {
  return (p[grade] ?? []).includes(itemId);
}
