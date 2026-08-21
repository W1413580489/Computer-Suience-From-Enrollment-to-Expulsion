// 成就系统 — 数据定义 + localStorage 存储管理
// 清除浏览器缓存后成就数据会消失

export interface AchievementDef {
  id: string;
  title: string;
  desc: string;
  badge: string;        // 票据上的标签文字（如 FIRE / ICE / SSR）
  badgeColor: 'yellow' | 'cyan' | 'magenta' | 'dark';
  stubLabel: string;    // 票根竖排文字
}

export const ACHIEVEMENTS: AchievementDef[] = [
  {
    id: 'id_card',
    title: '身份证',
    desc: '你已完成了账号的建立',
    badge: 'ID',
    badgeColor: 'yellow',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'quest_clear',
    title: '新手任务通关中',
    desc: '其实并没有什么关卡，我还没闲到把这个做成游戏',
    badge: 'QUEST',
    badgeColor: 'cyan',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'api_key',
    title: '我有的是钱！',
    desc: '正常来说，一个问答系统是可以直接使用的，只是我不舍得掏这笔钱',
    badge: 'BYOK',
    badgeColor: 'magenta',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'area_explore',
    title: '诶？云朵',
    desc: '你要好好长大，不要输给风，不要输给雨，不要输冬雪，也不要输炎夏',
    badge: 'AREA',
    badgeColor: 'cyan',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'rail_mode',
    title: '愿此行终抵群星',
    desc: '所谓开拓，就是沿着前人未尽的道路，走出更遥远的距离',
    badge: 'RAIL',
    badgeColor: 'magenta',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'welcome_new_eridu',
    title: '欢迎来到新艾利都',
    desc: 'Fairy，等下要是有人电我，你就偷偷给自己充电',
    badge: 'ZZZ',
    badgeColor: 'yellow',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'token_enough',
    title: '你token真的够吗？',
    desc: 'Coding发动前的41秒内，机房再次响起了codex用户的吟唱',
    badge: 'AI',
    badgeColor: 'cyan',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'see_you_tomorrow',
    title: '明天见',
    desc: '白昼与黑夜相等吗？义人与罪人相等吗？',
    badge: 'MODE',
    badgeColor: 'yellow',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'control_you',
    title: '我真得控制你了',
    desc: '你就这么热爱于获得彩蛋吗',
    badge: 'MOD',
    badgeColor: 'magenta',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'open_settings',
    title: '打开设置',
    desc: '这只是个网站，哪有设置功能？',
    badge: 'SYS',
    badgeColor: 'dark',
    stubLabel: 'ADMIT ONE',
  },
];

export interface AchievementRecord {
  id: string;
  unlocked: boolean;
  unlockedAt: string | null; // ISO 时间戳
}

const STORAGE_KEY = 'xkz_achievements';

type Store = Record<string, AchievementRecord>;

function load(): Store {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      return JSON.parse(raw);
    }
  } catch {
    // ignore
  }
  return {};
}

function save(store: Store) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  } catch {
    // ignore
  }
}

/** 获取所有已解锁成就（按解锁时间倒序） */
export function getUnlockedAchievements(): AchievementDef[] {
  const store = load();
  const unlocked = ACHIEVEMENTS.filter((a) => store[a.id]?.unlocked);
  return unlocked.sort((a, b) => {
    const ta = store[a.id]?.unlockedAt ? new Date(store[a.id]!.unlockedAt!).getTime() : 0;
    const tb = store[b.id]?.unlockedAt ? new Date(store[b.id]!.unlockedAt!).getTime() : 0;
    return tb - ta;
  });
}

/** 解锁成就（已解锁则跳过，不重复记录） */
export function unlockAchievement(id: string): boolean {
  const store = load();
  if (store[id]?.unlocked) return false;
  store[id] = {
    id,
    unlocked: true,
    unlockedAt: new Date().toISOString(),
  };
  save(store);
  return true;
}

/** 检查成就是否已解锁 */
export function isAchievementUnlocked(id: string): boolean {
  const store = load();
  return !!store[id]?.unlocked;
}

/** 监听成就变化（localStorage 跨标签页同步） */
export function subscribeAchievements(callback: () => void): () => void {
  const handler = (e: StorageEvent) => {
    if (e.key === STORAGE_KEY) callback();
  };
  window.addEventListener('storage', handler);
  return () => window.removeEventListener('storage', handler);
}
