// roadmapData：计算机四年路线图的数据源。
// 结构：目标（就业/考研/保研/创业）→ 学年时间线（大一~大四）→ 节点。
// 节点点击 → 弹窗摘要 + 跳转飞书原文；skillTree 节点可进入项目实战技能树。
// 映射关系与文档：tralis/docs/roadmap-plan.md

import goalCareerImage from '@/assets/images/goal-career.png';
import goalKaoyanImage from '@/assets/images/goal-kaoyan.jpg';

export interface RoadmapNode {
  id: string;
  title: string;
  en: string;
  /** 弹窗摘要 */
  desc: string;
  /** 来源章节名（展示用） */
  source: string;
  /** 飞书原文链接 */
  url: string;
  /** 是否可跳转项目实战技能树 */
  skillTree?: boolean;
}

export interface YearStage {
  year: string;
  num: string;
  en: string;
  nodes: RoadmapNode[];
}

export interface RoadmapGoal {
  id: string;
  num: string;
  title: string;
  en: string;
  desc: string;
  /** 主视觉图（后续提供，空则渲染几何占位） */
  image?: string;
  stages: YearStage[];
}

/* ---- 飞书链接（与 nav_config.json 保持一致） ---- */
const FEISHU = {
  freshman: 'https://tralis2671.feishu.cn/wiki/DYhvw9owZivrJskU5LicGl06nAg', // 新生指南补缺
  policy: 'https://bcnjr89bg80t.feishu.cn/wiki/HgtnwqvJUiKv58k7j3jcN0s4npg', // 大学政策简解
  academic: 'https://bcnjr89bg80t.feishu.cn/wiki/GF54wCHgUiOSmdkYSTIcVSWwncb', // 学术发展规划
  career: 'https://bcnjr89bg80t.feishu.cn/wiki/D17ewTvi8iImXbkBxS0cVt0un0O', // 就业发展规划
  contest: 'https://bcnjr89bg80t.feishu.cn/wiki/NCo9wYAxJilSEVki0e8cBWBInfb', // 竞赛指导
  tools: 'https://tralis2671.feishu.cn/wiki/ZATTw8ddKiJwD7k4OLicQGswnad', // 效率工具推荐
  git: 'https://tralis2671.feishu.cn/wiki/PZfdwamzGirDqOkrIIwcFIzbnlh', // Git 使用指南
  heretic: 'https://tralis2671.feishu.cn/wiki/FCATwwKbziiC7zkAL64cl3EXnCf', // 邪修学习指南
  fenjue: 'https://tralis2671.feishu.cn/wiki/ZnF4wWRGRi4Rk0kqTo4c6zz4n0b', // 焚决
  laptop: 'https://tralis2671.feishu.cn/wiki/Y9OIw8JXKiGsdtkP5RCcDxc3nge', // 笔记本电脑推荐
  antifraud: 'https://tralis2671.feishu.cn/wiki/Pl6jwyfb0iDe4LkuJtXcpiZBnjg', // 大学反诈篇
  research: 'https://tralis2671.feishu.cn/wiki/NKEVwGinTi5NOhkPEpLcnZoqnTd', // 从入门到入狱的科研全流程
};

/* ---- 公共节点 ---- */
const nodeAntifraud: RoadmapNode = {
  id: 'antifraud',
  title: '反诈骗篇',
  en: 'ANTI-FRAUD',
  desc: '校内英语角传销、社会调研偷拍、假官方群、兼职刷单……新生是被诈骗的重灾区。记住三条铁律：不请自来的"指导"要多方求证；零基础高薪必是诈骗；暨大官方群（有老师）必是禁水群。',
  source: '大学反诈篇',
  url: FEISHU.antifraud,
};

const nodePolicy: RoadmapNode = {
  id: 'policy',
  title: '学分与毕业要求',
  en: 'CREDIT POLICY',
  desc: '毕业需要修满多少学分、绩点怎么算、学位证条件、最长学习年限（8年）——这些政策决定了你能做什么、不能做什么。退学警告线：连续两学期学分不足 10 分。早知道早避坑。',
  source: '大学政策简解',
  url: FEISHU.policy,
};

const nodeGraduate: RoadmapNode = {
  id: 'graduate-audit',
  title: '毕业审核',
  en: 'GRADUATION AUDIT',
  desc: '大四最重要的收尾流程：毕业资格审查、论文答辩、离校手续、档案去向。每年都有人因为漏修学分延毕，对照培养方案逐项自查。',
  source: '大学政策简解',
  url: FEISHU.policy,
};

const nodeGpa: RoadmapNode = {
  id: 'gpa',
  title: '绩点与综测',
  en: 'GPA & EVALUATION',
  desc: '绩点是保研/留学/部分就业的硬通货，综测决定奖学金。大一不搞懂绩点规则（哪些课算加权、挂科怎么重修覆盖），大二大三会付出双倍代价。',
  source: '新生指南补缺',
  url: FEISHU.freshman,
};

const nodeFreshman: RoadmapNode = {
  id: 'freshman',
  title: '新手生存指南',
  en: 'FRESHMAN GUIDE',
  desc: '从入学报到、JNUID 激活、选课系统到宿舍生活的全流程新手攻略。用"角色背包/主线任务/支线剧情"的游戏化视角把入学第一周安排明白。',
  source: '新生指南补缺',
  url: FEISHU.freshman,
};

const nodeLaptop: RoadmapNode = {
  id: 'laptop',
  title: '电脑与工具准备',
  en: 'GEAR UP',
  desc: '大一就该买好电脑：按专业需求与预算选型（品牌梯度 T0~T3），配合效率工具（开发工具包、校园工具）搭建自己的生产环境。',
  source: '笔记本电脑推荐 / 效率工具推荐',
  url: FEISHU.laptop,
};

const nodeProjectIntro: RoadmapNode = {
  id: 'project-intro',
  title: '项目实战入门',
  en: 'PROJECT INITIATION',
  desc: '大一就能做项目：从克隆复现别人的开源项目开始，到重建项目、再从 0 开发自己的作品。这是邪修路线的起点，也是简历的第一块砖。',
  source: '邪修学习指南',
  url: FEISHU.heretic,
  skillTree: true,
};

const nodeGit: RoadmapNode = {
  id: 'git',
  title: 'Git 与开发工具入门',
  en: 'GIT & TOOLCHAIN',
  desc: '零基础到协作进阶：commit/branch/merge/rebase 的工作流，配合 GitHub 做版本管理与团队协作。写代码不版本控制等于裸奔。',
  source: 'Git 使用指南',
  url: FEISHU.git,
};

const nodeProjectBasic: RoadmapNode = {
  id: 'project-basic',
  title: '项目实战进阶',
  en: 'PROJECT ADVANCED',
  desc: '完整走一遍邪修基础篇：克隆复现 → 重建项目 → 从 0 开发。验收标准全部打勾后，你就有了独立完成一个项目的底气。',
  source: '邪修学习指南',
  url: FEISHU.heretic,
  skillTree: true,
};

const nodeProjectFull: RoadmapNode = {
  id: 'project-full',
  title: '项目积累',
  en: 'PROJECT PORTFOLIO',
  desc: '用项目实战篇的方法论打磨作品：写需求文档、做视觉交互方案、Vibe Coding 前端美化、修 Bug、部署上线。一个能跑的完整项目 > 十个半成品。',
  source: '邪修学习指南',
  url: FEISHU.heretic,
  skillTree: true,
};

const nodeInternship: RoadmapNode = {
  id: 'internship',
  title: '实习准备',
  en: 'INTERNSHIP',
  desc: '大三暑期实习是秋招的预演：简历怎么写、日常实习与暑期实习的区别、大厂投递节奏。信科学生找实习的正确姿势是直接投，而不是等"准备好了"。',
  source: '就业发展规划 / 焚决',
  url: FEISHU.career,
};

const nodeAutumnRecruit: RoadmapNode = {
  id: 'autumn-recruit',
  title: '秋招 / 春招',
  en: 'JOB HUNTING',
  desc: '秋招提前批 7 月就开始了：网申节奏、笔试八股、面试拷打、Offer 比较与签约。焚决里有前人被面试官拷打的真实实录，建议提前服用。',
  source: '就业发展规划 / 焚决',
  url: FEISHU.career,
};

/* ---- 考研路线节点 ---- */
const nodeDirection: RoadmapNode = {
  id: 'kaoyan-direction',
  title: '考研方向了解',
  en: 'DIRECTION',
  desc: '先想清楚三件事：考本校还是外校？学硕还是专硕？跨考还是本专业？内招与外招的政策差异、分数线与报录比，决定了你接下来两年的努力方向。',
  source: '学术发展规划',
  url: FEISHU.academic,
};

const nodeAcademicTools: RoadmapNode = {
  id: 'academic-tools',
  title: '学术工具准备',
  en: 'ACADEMIC TOOLKIT',
  desc: '文献管理（Zotero）、论文阅读、学术检索、笔记系统——这些工具在大二配好，考研收集资料与复试读论文时直接起飞。',
  source: '效率工具推荐',
  url: FEISHU.tools,
};

const nodeResearchIntro: RoadmapNode = {
  id: 'research-intro',
  title: '科研入门',
  en: 'RESEARCH 101',
  desc: '从入门到入狱的科研全流程：AI/NLP/CV/数据科学方向怎么选，导师怎么联系（吴文泰/孙玉霞老师风格对比），PyTorch 自学路线，以及"不要投中文刊"的血泪忠告。大二开始了解，大三进组正好。',
  source: '从入门到入狱的科研全流程',
  url: FEISHU.research,
};

const nodeKaoyanFormal: RoadmapNode = {
  id: 'kaoyan-formal',
  title: '考研正式准备',
  en: 'FORMAL PREP',
  desc: '大三下确定目标院校 → 数学/英语/政治/专业课四线推进。焚决里有外招上岸同学的时间线与踩坑记录，抄作业就行。',
  source: '学术发展规划 / 焚决',
  url: FEISHU.fenjue,
};

const nodeKaoyanSprint: RoadmapNode = {
  id: 'kaoyan-sprint',
  title: '考研冲刺',
  en: 'FINAL SPRINT',
  desc: '大四上：真题模拟 → 报名确认 → 初试（12月底）→ 复试准备 → 调剂。初试结束后立刻准备复试项目介绍，不要等出分。',
  source: '焚决',
  url: FEISHU.fenjue,
};

/* ---- 保研路线节点 ---- */
const nodeBaoyanCondition: RoadmapNode = {
  id: 'baoyan-condition',
  title: '保研条件了解',
  en: 'QUALIFICATION',
  desc: '绩点排名 + 综测加分 + 竞赛/科研加分构成保研综合评价。大二前搞清楚本院保研率、加分细则，才知道每学期该把力气花在哪。',
  source: '学术发展规划',
  url: FEISHU.academic,
};

const nodeContestStart: RoadmapNode = {
  id: 'contest-start',
  title: '竞赛加分起步',
  en: 'CONTEST START',
  desc: 'A 类竞赛（挑战杯、互联网+、数模）是保研加分的硬通货。大二选定 1~2 个主攻赛事，从院赛/校赛打起积累经验。',
  source: '竞赛指导',
  url: FEISHU.contest,
  skillTree: true,
};

const nodeBaoyanFormal: RoadmapNode = {
  id: 'baoyan-formal',
  title: '保研正式准备',
  en: 'FORMAL PREP',
  desc: '大三：夏令营材料（个人陈述、推荐信、成绩排名）、预推免与九推的时间线。焚决里有前人套磁与面试的完整复盘。',
  source: '学术发展规划 / 焚决',
  url: FEISHU.academic,
};

const nodeResearchOutput: RoadmapNode = {
  id: 'research-output',
  title: '科研产出',
  en: 'RESEARCH OUTPUT',
  desc: '保研的差异化筹码：跟着导师做出一篇论文或一个可展示的科研成果。科研全流程指南里有从选方向到投稿的完整路径与导师推荐。',
  source: '从入门到入狱的科研全流程',
  url: FEISHU.research,
};

const nodeProjectContest: RoadmapNode = {
  id: 'project-contest',
  title: '项目 / 竞赛经历',
  en: 'PROJECT & CONTEST',
  desc: '把邪修项目实战的成果拿去打竞赛：一个完整部署的项目是竞赛答辩的核心弹药。项目经历 + 竞赛奖项 = 保研面试的双保险。',
  source: '邪修学习指南 / 竞赛指导',
  url: FEISHU.heretic,
  skillTree: true,
};

/* ---- 四个目标 ---- */
export const roadmapGoals: RoadmapGoal[] = [
  {
    id: 'career',
    num: '01',
    title: '就业',
    en: 'CAREER',
    desc: '互联网 / 国企 / 考公 / 选调，用项目与实习铺路',
    image: goalCareerImage,
    stages: [
      {
        year: '大一', num: '01', en: 'FRESHMAN',
        nodes: [nodeFreshman, nodeAntifraud, nodePolicy, nodeLaptop, nodeProjectIntro],
      },
      {
        year: '大二', num: '02', en: 'SOPHOMORE',
        nodes: [nodeGit, nodeProjectBasic],
      },
      {
        year: '大三', num: '03', en: 'JUNIOR',
        nodes: [nodeInternship, nodeProjectFull],
      },
      {
        year: '大四', num: '04', en: 'SENIOR',
        nodes: [nodeAutumnRecruit, nodeGraduate],
      },
    ],
  },
  {
    id: 'kaoyan',
    num: '02',
    title: '考研',
    en: 'POSTGRADUATE',
    desc: '内招 / 外招 / 港澳台，绩点与初试双线作战',
    image: goalKaoyanImage,
    stages: [
      {
        year: '大一', num: '01', en: 'FRESHMAN',
        nodes: [nodeFreshman, nodeAntifraud, nodeGpa],
      },
      {
        year: '大二', num: '02', en: 'SOPHOMORE',
        nodes: [nodeDirection, nodeAcademicTools, nodeResearchIntro],
      },
      {
        year: '大三', num: '03', en: 'JUNIOR',
        nodes: [nodeKaoyanFormal],
      },
      {
        year: '大四', num: '04', en: 'SENIOR',
        nodes: [nodeKaoyanSprint, nodeGraduate],
      },
    ],
  },
  {
    id: 'baoyan',
    num: '03',
    title: '保研',
    en: 'RECOMMENDATION',
    desc: '绩点为王，竞赛与科研是差异化筹码',
    stages: [
      {
        year: '大一', num: '01', en: 'FRESHMAN',
        nodes: [nodeGpa, nodeAntifraud, nodePolicy],
      },
      {
        year: '大二', num: '02', en: 'SOPHOMORE',
        nodes: [nodeBaoyanCondition, nodeContestStart],
      },
      {
        year: '大三', num: '03', en: 'JUNIOR',
        nodes: [nodeBaoyanFormal, nodeResearchOutput, nodeProjectContest],
      },
      {
        year: '大四', num: '04', en: 'SENIOR',
        nodes: [nodeGraduate],
      },
    ],
  },
  {
    id: 'startup',
    num: '04',
    title: '创业',
    en: 'STARTUP',
    desc: '内容待补充',
    stages: [
      {
        year: '大一', num: '01', en: 'FRESHMAN',
        nodes: [nodeAntifraud, nodeFreshman],
      },
      {
        year: '大二', num: '02', en: 'SOPHOMORE',
        nodes: [],
      },
      {
        year: '大三', num: '03', en: 'JUNIOR',
        nodes: [],
      },
      {
        year: '大四', num: '04', en: 'SENIOR',
        nodes: [],
      },
    ],
  },
];

/* ---- 项目实战技能树（邪修学习指南：基础篇 + 项目实战篇合并） ---- */
export interface SkillNode {
  id: string;
  num: string;
  title: string;
  en: string;
  desc: string;
  /** 验收标准（打勾项） */
  checks: string[];
  url: string;
}

export const skillTree: SkillNode[] = [
  {
    id: 'clone',
    num: '01',
    title: '克隆复现',
    en: 'CLONE & REPRODUCE',
    desc: '找一个喜欢的开源项目，把它完整跑起来。改几个参数看看会发生什么，理解每一行配置的作用。',
    checks: [
      '选一个开源项目并成功在本地运行',
      '理解项目的目录结构与入口文件',
      '修改至少一处配置/代码并观察效果',
    ],
    url: FEISHU.heretic,
  },
  {
    id: 'rebuild',
    num: '02',
    title: '重建项目',
    en: 'REBUILD',
    desc: '不看原代码，凭理解把项目的核心功能重新实现一遍。卡住了再回去看，这才是真的学会了。',
    checks: [
      '不看原码复现核心功能',
      '遇到卡点能定位到原项目对应实现',
      '能向别人解释项目的技术选型',
    ],
    url: FEISHU.heretic,
  },
  {
    id: 'from-zero',
    num: '03',
    title: '从 0 开发',
    en: 'FROM ZERO',
    desc: '自己想一个需求，从空文件夹开始建项目：初始化、架构、功能、README 全部自己来。',
    checks: [
      '独立完成一个有真实需求的小项目',
      '项目有 README 与基本文档',
      '代码纳入 Git 版本管理',
    ],
    url: FEISHU.heretic,
  },
  {
    id: 'prd',
    num: '04',
    title: '需求文档',
    en: 'PRD',
    desc: '动工前先写需求文档：目标用户、核心功能、优先级、验收标准。文档写清楚了，开发就不容易跑偏。',
    checks: [
      '为目标项目撰写需求文档',
      '明确功能优先级（P0/P1/P2）',
      '文档包含验收标准',
    ],
    url: FEISHU.heretic,
  },
  {
    id: 'visual',
    num: '05',
    title: '视觉交互方案',
    en: 'VISUAL DESIGN',
    desc: '画界面原型：布局、配色、交互流程。可以是 Figma 也可以是纸笔，重点是先想清楚再动手。',
    checks: [
      '完成主要页面的原型图',
      '确定视觉风格与配色方案',
      '梳理核心交互流程',
    ],
    url: FEISHU.heretic,
  },
  {
    id: 'vibe-coding',
    num: '06',
    title: 'Vibe Coding 前端美化',
    en: 'VIBE CODING',
    desc: '用 AI 辅助把界面从"能用"打磨到"好看"：布局细节、动效、响应式。善用 AI 但保持自己的审美判断。',
    checks: [
      '完成前端界面美化',
      '适配移动端 / 多分辨率',
      'AI 生成的内容能看懂并调整',
    ],
    url: FEISHU.heretic,
  },
  {
    id: 'debug',
    num: '07',
    title: '改 Bug',
    en: 'DEBUG',
    desc: '修 Bug 是常态：学会看报错栈、打日志、二分定位。修完写复盘，下次同类问题 5 分钟解决。',
    checks: [
      '修复项目中的全部已知 Bug',
      '记录至少 3 个典型 Bug 的排查过程',
      '建立自己的调试方法（日志/断点/二分）',
    ],
    url: FEISHU.heretic,
  },
  {
    id: 'deploy',
    num: '08',
    title: '部署上线',
    en: 'DEPLOY',
    desc: '让项目在公网可访问：服务器、域名、HTTPS、Nginx 反代、进程守护。部署完才算闭环，简历上也才有链接可放。',
    checks: [
      '项目部署到服务器并公网可访问',
      '配置域名与 HTTPS',
      '写一篇部署复盘文档',
    ],
    url: FEISHU.heretic,
  },
];
