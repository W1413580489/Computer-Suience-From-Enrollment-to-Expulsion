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

// ---- 里程碑（MILESTONES）：每年级三列分组（必做事项 / 选做成就 / 隐藏彩蛋）----
export interface MilestoneItem {
  id: string;
  text: string;
}

export interface MilestoneColumn {
  key: string;
  title: string;
  en: string;
  items: MilestoneItem[];
}

export interface GradeMilestone {
  columns: MilestoneColumn[];
}

export const gradeMilestones: Record<number, GradeMilestone> = {
  1: {
    columns: [
      {
        key: 'must',
        title: '必做事项',
        en: 'MUST DO',
        items: [
          { id: 'g1_m1', text: '激活 JNUID 账号' },
          { id: 'g1_m2', text: '完成线上报到 + 缴费' },
          { id: 'g1_m3', text: '准备好证件照与身份证复印件' },
          { id: 'g1_m4', text: '办理校园卡/宿舍入住' },
        ],
      },
      {
        key: 'achieve',
        title: '选做成就',
        en: 'ACHIEVEMENT',
        items: [
          { id: 'g1_a1', text: '加入一个新生群/社团' },
          { id: 'g1_a2', text: '完成新生选课' },
          { id: 'g1_a3', text: '军训撑到最后一刻' },
        ],
      },
      {
        key: 'hidden',
        title: '隐藏彩蛋',
        en: 'HIDDEN',
        items: [
          { id: 'g1_h1', text: '读完全部新生主线任务' },
          { id: 'g1_h2', text: '找到校园卡隐藏折扣' },
        ],
      },
    ],
  },
  2: {
    columns: [
      {
        key: 'must',
        title: '必做事项',
        en: 'MUST DO',
        items: [
          { id: 'g2_m1', text: '稳住绩点，避免挂科' },
          { id: 'g2_m2', text: '确定保研/考研/就业大方向' },
          { id: 'g2_m3', text: '关注竞赛报名时间' },
        ],
      },
      {
        key: 'achieve',
        title: '选做成就',
        en: 'ACHIEVEMENT',
        items: [
          { id: 'g2_a1', text: '参加一次学科竞赛' },
          { id: 'g2_a2', text: '尝试科研/大创项目入门' },
          { id: 'g2_a3', text: '考过四六级' },
        ],
      },
      {
        key: 'hidden',
        title: '隐藏彩蛋',
        en: 'HIDDEN',
        items: [
          { id: 'g2_h1', text: '摸清内/外招生保研要求差异' },
          { id: 'g2_h2', text: '找到适合的竞赛搭子' },
        ],
      },
    ],
  },
  3: {
    columns: [
      {
        key: 'must',
        title: '必做事项',
        en: 'MUST DO',
        items: [
          { id: 'g3_m1', text: '从零开始复现一个开源项目' },
          { id: 'g3_m2', text: '重建项目并加入自己的功能' },
          { id: 'g3_m3', text: '完成一段独立项目开发' },
          { id: 'g3_m4', text: '简历更新：写入项目经历' },
        ],
      },
      {
        key: 'achieve',
        title: '选做成就',
        en: 'ACHIEVEMENT',
        items: [
          { id: 'g3_a1', text: '投递一份实习' },
          { id: 'g3_a2', text: '把项目部署上线/开源' },
          { id: 'g3_a3', text: '学论文怎么写/文献检索' },
        ],
      },
      {
        key: 'hidden',
        title: '隐藏彩蛋',
        en: 'HIDDEN',
        items: [
          { id: 'g3_h1', text: '让项目经得住“乱点五分钟”' },
          { id: 'g3_h2', text: '找到一起肝项目的队友' },
        ],
      },
    ],
  },
  4: {
    columns: [
      {
        key: 'must',
        title: '必做事项',
        en: 'MUST DO',
        items: [
          { id: 'g4_m1', text: '简历定稿（排版+项目+实习）' },
          { id: 'g4_m2', text: '秋招/春招海投开始' },
          { id: 'g4_m3', text: '梳理目标：民企/国企/考公/创业' },
          { id: 'g4_m4', text: '完成毕业论文/毕设' },
        ],
      },
      {
        key: 'achieve',
        title: '选做成就',
        en: 'ACHIEVEMENT',
        items: [
          { id: 'g4_a1', text: '拿到第一份面试' },
          { id: 'g4_a2', text: '斩获 Offer' },
          { id: 'g4_a3', text: '参加一次校招宣讲会' },
        ],
      },
      {
        key: 'hidden',
        title: '隐藏彩蛋',
        en: 'HIDDEN',
        items: [
          { id: 'g4_h1', text: '毕业前吃遍暨大食堂' },
          { id: 'g4_h2', text: '和大学四年的人好好告别' },
        ],
      },
    ],
  },
};