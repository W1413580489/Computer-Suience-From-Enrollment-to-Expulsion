// 成就系统 — 数据定义 + localStorage 持久化层
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
  {
    id: 'understand_all',
    title: '我逐渐理解一切',
    desc: '你居然把整个网站都探索了一遍',
    badge: 'ALL',
    badgeColor: 'magenta',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'view_changelog',
    title: '打开设置',
    desc: '真的有人会看更新日志',
    badge: 'LOG',
    badgeColor: 'dark',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'passing_rider',
    title: '帝骑',
    desc: '我只是一个路过的假面骑士，给我记住了',
    badge: 'GUEST',
    badgeColor: 'yellow',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'reverse_clock',
    title: '反方向的钟',
    desc: '重复打开校历又怎么样？你永远回不到假期前',
    badge: 'TIME',
    badgeColor: 'cyan',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'meaningless_night',
    title: '虽然那是个无所谓的夜晚',
    desc: 'どうでもいいような夜だけど~~',
    badge: 'NIGHT',
    badgeColor: 'dark',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'who_am_i',
    title: '我，是我？',
    desc: '今日方知我是我！',
    badge: 'ME',
    badgeColor: 'magenta',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'twenty_years',
    title: '二十年重过南楼',
    desc: '欲买桂花同载酒，终不是，少年游',
    badge: 'SR',
    badgeColor: 'yellow',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'youth_spring',
    title: '年少掷春光',
    desc: '少年恃险若平地，独倚长剑凌清秋',
    badge: 'FR',
    badgeColor: 'cyan',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'what_is_this',
    title: '啥呀',
    desc: '生活一圈圈日子一年年，总是这样重复一遍又一遍，忙碌庸碌没有人挂念',
    badge: 'HMM',
    badgeColor: 'dark',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'ending',
    title: '结局？',
    desc: '当终焉的陨星在白垩纪降下，唯有自由的鸟儿才能跳出既定的灭亡',
    badge: 'END',
    badgeColor: 'magenta',
    stubLabel: 'ADMIT ONE',
  },
  // ---- 新成就2：背景设置 / 路线图 / AI导师 ----
  {
    id: 'one_last_kiss',
    title: 'One Last Kiss',
    desc: '第一次去卢浮宫时，没什么特别的感觉，因为独属于我的蒙娜丽莎，我早已遇见',
    badge: 'BG',
    badgeColor: 'magenta',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'cant_say_goodbye',
    title: '讲不出再见',
    desc: '我最不忍看你 背向我转面，要走一刻请不必诸多眷恋',
    badge: 'BG',
    badgeColor: 'dark',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'poincare_return',
    title: '庞加莱回归',
    desc: '已有的事，后必再有；已行的事，后必在行',
    badge: 'BG',
    badgeColor: 'cyan',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'where_wander',
    title: '我将在何处游荡？',
    desc: '......',
    badge: 'MAP',
    badgeColor: 'cyan',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'homepage_has_entry',
    title: '主页明明有入口',
    desc: '你就非要在这里点吗？',
    badge: 'NAV',
    badgeColor: 'dark',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'love_working',
    title: '真的很喜欢上班啊',
    desc: '这种又累又没钱的生活，真让人上瘾啊',
    badge: 'WORK',
    badgeColor: 'yellow',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'study_spring',
    title: '白鹿洞二首·其一',
    desc: '读书不觉已春深，一寸光阴一寸金',
    badge: 'STUDY',
    badgeColor: 'magenta',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'poetry_zhang',
    title: '题张司业诗',
    desc: '看似寻常最奇崛，成如容易却艰辛。',
    badge: 'POEM',
    badgeColor: 'cyan',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'mountain_pressure',
    title: '势利压山岳?',
    desc: '月缺不改光，剑折不改刚。月缺魄易满，剑折铸复良',
    badge: 'BIZ',
    badgeColor: 'yellow',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'green_fruit_1',
    title: '青涩的果实Ⅰ',
    desc: '今天就从今天开始，明天就从明天开始！',
    badge: 'AI',
    badgeColor: 'cyan',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'green_fruit_2',
    title: '青涩的果实Ⅱ',
    desc: 'Can you please give some more power to me，',
    badge: 'KEY',
    badgeColor: 'magenta',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'green_fruit_3',
    title: '青涩的果实Ⅲ',
    desc: '青涩的果实啊  还不曾变得甘甜。',
    badge: 'CHAT',
    badgeColor: 'dark',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'trust_me',
    title: 'Trust me',
    desc: "I'll be the one，Who fight for you when things go wrong，",
    badge: 'COACH',
    badgeColor: 'yellow',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'power_home_ideal',
    title: '力量，归宿，理想',
    desc: '才是我自己的力量，我自己的归宿，我自己的理想，这！才是真正的我！',
    badge: 'BUG',
    badgeColor: 'magenta',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'why_birds_fly',
    title: '鸟为什么会飞',
    desc: '你，你们，必须飞到比我更高的地方',
    badge: 'REV',
    badgeColor: 'cyan',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'great_discipline_officer',
    title: '大风纪官',
    desc: '以此身，肃正万象！',
    badge: 'RESET',
    badgeColor: 'dark',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'traveler',
    title: '旅者',
    desc: '旅途总有一天会迎来终点，不必匆忙',
    badge: 'CLR',
    badgeColor: 'yellow',
    stubLabel: 'ADMIT ONE',
  },
  {
    id: 'all_achievements',
    title: '全成就达成Ⅰ',
    desc: '这只是第一阶段的完成',
    badge: 'SSR',
    badgeColor: 'yellow',
    stubLabel: 'ADMIT ONE',
  },
];

export interface AchievementRecord {
  id: string;
  unlocked: boolean;
  unlockedAt: string | null; // ISO 时间戳
}

export const STORAGE_KEY = 'xkz_achievements';

export type AchievementData = Record<string, AchievementRecord>;

/** 读取 localStorage 持久化数据 */
export function loadStore(): AchievementData {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      return JSON.parse(raw) as AchievementData;
    }
  } catch {
    // ignore
  }
  return {};
}

/** 写入 localStorage 持久化数据 */
export function saveStore(store: AchievementData) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  } catch {
    // ignore
  }
}