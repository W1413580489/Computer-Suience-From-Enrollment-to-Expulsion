export interface GradeCardContent {
  title: string;
  en: string;
  desc: string;
  url: string;
}

export const gradeCardContent: Record<number, GradeCardContent> = {
  1: {
    title: '新生指南补缺',
    en: 'FRESHMAN GUIDE',
    desc: '入学前准备与新生常见问题',
    url: 'https://tralis2671.feishu.cn/wiki/DYhvw9owZivrJskU5LicGl06nAg',
  },
  2: {
    title: '学术发展规划',
    en: 'ACADEMIC PLAN',
    desc: '课程规划 · 科研入门 · 竞赛参与',
    url: 'https://tralis2671.feishu.cn/wiki/FCATwwKbziiC7zkAL64cl3EXnCf',
  },
  3: {
    title: '邪修学习指南',
    en: 'HERETIC GUIDE',
    desc: '非常规学习路径 · 效率方法论',
    url: 'https://tralis2671.feishu.cn/wiki/FCATwwKbziiC7zkAL64cl3EXnCf',
  },
  4: {
    title: '就业发展规划',
    en: 'CAREER PLAN',
    desc: '实习 · 简历 · 面试 · 行业分析',
    url: 'https://tralis2671.feishu.cn/wiki/FCATwwKbziiC7zkAL64cl3EXnCf',
  },
};

export const heroSubtitles: Record<number, string> = {
  1: '新生指南 · 开启你的大学之旅',
  2: '学术规划 · 夯实专业基础',
  3: '邪修学习 · 另辟蹊径',
  4: '职涯启航 · 迈向职场第一步',
};

// ---- 情绪标签（BADGES）：每年级 4 个，zzz 中文 + ak 英文 sub ----
export interface GradeBadge {
  text: string;
  en: string;
}

export const gradeBadges: Record<number, GradeBadge[]> = {
  1: [
    { text: '想放假', en: 'WANT HOLIDAY' },
    { text: '求停课', en: 'NO CLASS PLS' },
    { text: '续火花', en: 'KEEP STREAK' },
    { text: '扩列dd', en: 'ADD FRIENDS' },
  ],
  2: [
    { text: '成绩出没', en: 'GRADES OUT' },
    { text: '几号考试', en: 'EXAM WHEN?' },
    { text: '想死...', en: 'KMS...' },
    { text: '实验报告借我抄一下', en: 'BORROW REPORT' },
  ],
  3: [
    { text: '我外卖呢？', en: 'WHERE FOOD' },
    { text: 'v我50', en: 'VENMO 50' },
    { text: '是啊吃什么', en: 'WHAT TO EAT' },
    { text: '谁偷了我的外卖', en: 'FOOD THIEF' },
  ],
  4: [
    { text: '我对象呢？', en: 'WHERE BOO' },
    { text: '我工作呢？', en: 'WHERE JOB' },
    { text: '秋招中', en: 'AUTUMN HIRE' },
    { text: '毕业快乐', en: 'GRAD CHEERS' },
  ],
};

// ---- 进度条（PROGRESS BARS）：每年级 3 个（标题 + 数值 + 色系）----
export interface GradeBar {
  label: string;
  value: number;
  tone?: 'default' | 'red' | 'green';
}

export const gradeBars: Record<number, GradeBar[]> = {
  1: [
    { label: 'Patience', value: 90 },
    { label: 'Curiosity', value: 80 },
    { label: 'cache', value: 21, tone: 'red' },
  ],
  2: [
    { label: 'timeout', value: 99, tone: 'red' },
    { label: 'abandon', value: 100, tone: 'red' },
    { label: 'exception', value: 98, tone: 'green' },
  ],
  3: [
    { label: 'blocked', value: 55 },
    { label: 'abandon', value: 32, tone: 'green' },
    { label: 'latency', value: 85, tone: 'red' },
  ],
  4: [
    { label: 'bug', value: 99, tone: 'red' },
    { label: 'bald', value: 75 },
    { label: 'deadline', value: 1, tone: 'green' },
  ],
};
