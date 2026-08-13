import{d as U,o as i,c as l,a as e,e as H,_ as V,i as ee,j as I,b as se,m as te,t as o,F as J,r as Q,l as N,g as k,f as j,v as ne,u as ae,n as S,x as ie}from"./index-BICq-X-A.js";import{N as oe}from"./NeonIcon-CQbDrVt5.js";import{r as le}from"./useMarkdown-ZOlDXMz4.js";const re={class:"splash-root"},ce={class:"splash-center"},de={class:"splash-content"},_e=U({__name:"QuestLogin",emits:["done"],setup(u){return(m,t)=>(i(),l("div",re,[e("div",ce,[t[4]||(t[4]=e("div",{class:"splash-rings"},[e("div",{class:"splash-ring splash-ring--outer"}),e("div",{class:"splash-ring splash-ring--mid"}),e("div",{class:"splash-ring splash-ring--inner"})],-1)),e("div",de,[t[2]||(t[2]=H('<span class="splash-badge" data-v-07381412>XKZ · AGENT SYSTEM</span><h1 class="splash-title" data-v-07381412>暨南大学番禺校区</h1><p class="splash-sub" data-v-07381412>新生入学攻略指南</p><div class="splash-divider" data-v-07381412><span class="splash-divider__line" data-v-07381412></span><span class="splash-divider__dot" data-v-07381412></span><span class="splash-divider__line" data-v-07381412></span></div><p class="splash-desc" data-v-07381412> 装备清单 · 技能加点 · NPC 任务 · 主线攻略 · 大地图探索 · 道具采购 </p>',5)),e("button",{class:"splash-btn",onClick:t[0]||(t[0]=c=>m.$emit("done"))},[...t[1]||(t[1]=[e("span",{class:"splash-btn__text"},"≡ 进入新手村 ≡",-1),e("span",{class:"splash-btn__glow"},null,-1)])]),t[3]||(t[3]=e("p",{class:"splash-ver"},"v2.0 · 新生入学攻略指南",-1))])]),t[5]||(t[5]=e("div",{class:"splash-corner splash-corner--tl"},null,-1)),t[6]||(t[6]=e("div",{class:"splash-corner splash-corner--tr"},null,-1)),t[7]||(t[7]=e("div",{class:"splash-corner splash-corner--bl"},null,-1)),t[8]||(t[8]=e("div",{class:"splash-corner splash-corner--br"},null,-1))]))}}),ue=V(_e,[["__scopeId","data-v-07381412"]]),W="xkz_quest";function pe(){try{const u=localStorage.getItem(W);if(u)return JSON.parse(u)}catch{}return{equipment:[],skills:{},skillPointsSpent:0,mainComplete:[],explored:[],hasSeenIntro:!1}}function q(u){localStorage.setItem(W,JSON.stringify(u))}const ge="/assets/0b915def6e8c03c43f51302509365af7-1o2qseo4.jpg",ve="/assets/2be295576003104ef4a1bbfc694eeedb-CGB6Ws2e.jpg",me="/assets/35351c9d9cb246db924eb30eb341b6d2-BPcSUnIB.jpeg",be="/assets/562c89db2002fd42ecc10baf5027d7d4-Dki17p66.jpg",fe="/assets/6a5dee60141194371ee6cda667cb9c2e-C_yAPkmD.jpg",he="/assets/Picture_xinke_transparent-B4GfPugk.png",ke="/assets/cc9531ba5fcb1657c36d009373110fad-BX_Cf58B.jpg",Ce="/assets/image-BUIQz-ur.png",je="/assets/image_1-CqyqXqlj.png",ye="/assets/image_2-BNn_GYzc.png",$e="/assets/image_3-xkKz1vrr.png",Ne="/assets/image_4-SZXhyQWi.png",xe="/assets/songhao_screenshot-DRu1bde3.png",Pe=Object.assign({"/src/assets/images/guide01/0b915def6e8c03c43f51302509365af7.jpg":ge,"/src/assets/images/guide01/2be295576003104ef4a1bbfc694eeedb.jpg":ve,"/src/assets/images/guide01/35351c9d9cb246db924eb30eb341b6d2.jpeg":me,"/src/assets/images/guide01/562c89db2002fd42ecc10baf5027d7d4.jpg":be,"/src/assets/images/guide01/6a5dee60141194371ee6cda667cb9c2e.jpg":fe,"/src/assets/images/guide01/Picture_xinke_transparent.png":he,"/src/assets/images/guide01/cc9531ba5fcb1657c36d009373110fad.jpg":ke,"/src/assets/images/guide01/image.png":Ce,"/src/assets/images/guide01/image_1.png":je,"/src/assets/images/guide01/image_2.png":ye,"/src/assets/images/guide01/image_3.png":$e,"/src/assets/images/guide01/image_4.png":Ne,"/src/assets/images/guide01/songhao_screenshot.png":xe}),d=u=>{for(const[m,t]of Object.entries(Pe))if(m.endsWith("/"+u)||m.endsWith(u))return t;return console.warn(`Image not found: ${u}`),""},_={pig:d("562c89db2002fd42ecc10baf5027d4d4.jpg"),deadpool:d("6a5dee60141194371ee6cda667cb9c2e.jpg"),memory:d("2be295576003104ef4a1bbfc694eeedb.jpg"),kuangkuang:d("image.png"),monkey:d("image_1.png"),sucai:d("image_2.png"),songhao:d("songhao_screenshot.png"),genius:d("cc9531ba5fcb1657c36d009373110fad.jpg"),score:d("image_3.png"),xinke:d("0b915def6e8c03c43f51302509365af7.jpg"),campus:d("35351c9d9cb246db924eb30eb341b6d2.jpeg")},Ie=[{id:"login",title:"新玩家账号登录",icon:"👤",sections:[{id:"login_equip",title:"角色装备清单",content:`入学前请打开你的「角色背包」，检查以下装备是否齐全：

| 名称 | 获取方式 | 备注 |
|------|---------|------|
| 录取通知书 | 内招学生学校发放，外教学生可能需要自行打印 | 全文复印1份备用，以备不时之需；外招凭打印版报到后，将来会补发实物 |
| 身份证件 | 角色出生自带 | 将身份证件正反面打印在同一面，外招同学报考/入学使用注册的同一张证件，后续学校内的各种注册事务都要使用相同证件，避免麻烦 |
| 证件照 | 照相馆掉落 | 入学的要求中已经具体标注证件照的规格，在此不多做解释 |
| 团组织档案 | 高中副本结算 | 按入学要求准备 |
| JNUID账号 | 线上提前激活 | 8月下旬关注「暨南大学官方服务号」（微信号：JinanUniversity）→ 菜单栏「欢迎新生-新生服务」→ 设置密码 → 完成激活 |

> **JNUID 是最重要的通行证**——它同时是教务系统、校园网、图书馆、选课系统、体测查询等所有校内功能的登录钥匙。`},{id:"login_skills",title:"技能预加点",content:`在正式开学前，建议你学习好以下的一些技能：

### ① 「信息检索」Lv.1

- 关注暨南大学官方微信公众号并完成 JNUID 绑定
- 提前截图或保存好查看入学事项公告、报到信息、缴费信息——有需要的公告、信息、教程。由于开学人数过多，有概率网络较差，人群密集处，网络或流量都难以幸免

:::callout emoji="🌐"
[新生登录说明](https://netc.jnu.edu.cn/2023/0814/c10374a760871/page.htm)
:::

### ② 「行李收纳」Lv.Max

- 快递大件行李到学校：地址「广东省广州市番禺区南村镇兴业大道东855号暨南大学番禺校区菜鸟驿站」→ 快递中心在 T11 架空层
- **大件请全部走快递，到了再取！** 开学时学长学姐真的搬不动你的行李箱。如果自己不想太累，可以联系你认识的在校/可提供帮助的学长学姐，提前帮你取好行李并寄存，避免快递站爆满导致挤不进去

### ③ 「防诈骗」Lv.1

- 凡是**学院专业官方群**以外的任何通知都不保证真实！
- 所有涉及金钱的通知，只会通过**官方群聊**下达！
- 任何通过诱骗、恐吓等手段以报班学习为目的的机构均不真实！`},{id:"login_npc",title:"NPC 任务",content:`### 任务一：引路学长/学姐（面向全体新生）

- 微信小程序搜索「暨大迎新」→ 登录查询你的对点引路学长/学姐
- 加上微信后可以进行学生事务的询问，或者聊天。在你的引路学长有空的情况下，可以申请帮助，商量报道当天碰头，带你行走校园
- 由于学校的装修扩建，旧的地图可能有一定变化，加上开学人数众多，老生带路比地图效率更高
- **但不可以强制，避免掉 NPC 好感度**

### 任务二：加入班级微信群（面向全体新生）

- 按照你的专业加入对应的班级群（26+专业+名字实名），群聊会由你的引路学长拉你进群
- **禁水群用来接收重要通知，不要在里面发消息**
- 有问题可在水群提问，或者自行私聊

### 任务三：确认电脑配置（面向理工科）

- 尽量买 Windows 游戏本（已购买不必观看，还未购买的同学注意）
- iPad 自愿选购，iPadOS 写不了很多作业，仅能代替纸质笔记本
- **五人寝**桌子比较小，可以放 24 寸 16:9 显示器，台式机慎重
- **四人寝**的空间极为足够，可以随意配置`},{id:"login_transport",title:'前往"新手村"',content:`### 地铁+公交

地铁 4 号线 → **新造站** A1 出口 → 搭乘番87路公交 → 金光西大道站（暨南大学南校区）下车 → 步行约 800 米到达暨南大学番禺校区南门

### 各大交通枢纽出发

| 出发地 | 推荐路线 |
|--------|---------|
| **白云机场** | 3号线 → 体育西路转 3 号线 → 客村转 8 号线 → 万胜围转 4 号线 → 新造站 |
| **广州南站** | 7 号线 → 大学城南转 4 号线 → 新造站 |
| **广州火车站** | 5 号线 → 车陂南转 4 号线 → 新造站 |
| **广州火车东站** | 1 号线 → 杨箕转 5 号线 → 车陂南转 4 号线 → 新造站 |

### 自驾/打车

导航搜索"暨南大学番禺校区"（广州市番禺区兴业大道东855号）。迎新报到当天，社会车辆禁止入校，需在南门下车，换乘校内接驳车。由于东门车道狭窄，容易堵塞，**强烈不建议在东门下车**。`}]},{id:"mainline",title:"新生主线任务篇",icon:"⚔️",sections:[{id:"main_wall",title:"1. 新生四道坎",content:`> 新生学习的第一课，就是先把各篇章都看了！想读研，论文文献比这更晦涩；想工作，工作文档比这更复杂。如果你连这点文档都没有耐心阅读，期末周你只会比阅读文档更痛苦。

入学流程概览：

1. **抵达南门/东门** → 新生及家长从步行入校（迎新期间机动车不进校）
2. **换乘接驳车** → 有迎新大巴接驳前往宿舍区和报到点，你走也行，走几步就到了
3. **办理入住** → 先到宿舍放行李，领取宿舍钥匙/门禁卡
4. **学院报到** → 前往所在学院迎新点，提交材料、领取新生资料袋
5. **体检** → 按安排参加新生入学体检（早晨空腹）
6. **校园卡激活** → 激活校园卡，充值开通使用
7. **班会/新生见面会** → 这玩意可能有可能没有，总之先去**拿快递**吧

鉴于广东天气原因，建议提前带上降温工具。完成一系列手续后，开始取回快递和宿舍打理。大一作为整个大学最轻松的阶段，有充足的时间进行自己的个人活动。

---

> **第一道坎**：学长上门哄你办校园卡。平心而论，校园卡其实性价比不错，给的流量也很多，不过自己去办可能还能再省一点。

> **第二道坎**：宿舍到底要不要买洗衣机和冰箱。洗衣机的 100% 要买了，在广东没有洗衣机很难受的。但冰箱价格不菲，且搬运麻烦，需要和室友沟通 AA。

> **第三道坎**：扪心自问——你是一个爱干净的人吗？你们宿舍需要打扫吗？趁着大家还没有熟起来，做好宿舍值日的规划。一个干净舒适的宿舍环境，能给大学带来极不一样的体验。建议购买浴室前的地毯，拖把 1~2 个，扫把 1 个，抹布，马桶刷。

![卡通猪清洁插图](${_.pig})

> **第四道坎**：最重要的一道——这完全取决了你的大学作息安排。宿舍几点关灯？几点静音？务必要提前交流敲定！等你明天还有早八，然后现在是凌晨 2:30，你的舍友还在开着台灯打游戏，大声敲键盘，以及大吼大叫的时候，你将知道什么叫绝望。

![死侍搏击插图](${_.deadpool})

> 如果不想演化成校园自由搏击，请注意沟通。`},{id:"main_course",title:"2. 新生选课",content:`军训开始之后，中间还会遇到选课。由于学生培养方案的不同，学生需要根据本届的需求进行选课。大一新生由于课程固定，只需要在选课网站点击"方案内"，然后选择所有的必修课即可，选择的空间仅有不同老师以及不同的体育课。

我们点击：

→ 教务系统网上办事服务大厅：jw.jnu.edu.cn

→ "学业完成查询"，可以看到当前学业的完成情况，方便你未来的选课。

想要知道更具体的方案：

→ "全校方案查询"，点击你目前的年级，选择本学院，即可看到你的专业必修课、选修课具体都有些什么。

:::callout emoji="🌐"
选课，当然要买一部好电脑了！分享由 **23网安梵某学长** 编撰的电脑选购指南。
:::`},{id:"main_class",title:"3. 新生上课",content:`军训和选课都完成之后，就是上课的开始。

网页版点击教务系统，再选择"我的课表"，可以看到课程的上课时间、任课老师、上课地点（上课地点有可能会改变，请详细查看群聊的通知）。

手机版可以搜索暨南大学公众号，选择服务，点击本科教务，则会出现移动端的本科教务系统，不过功能较少，仅可以查看课表、考试安排和成绩。

> ⚠️ **必须谨记**：当缺勤率达到 1/3（不同老师有不同的标准），你会被取消考试资格！注意出勤率的问题。

成绩构成：
- **60% 考试卷面分 + 40% 平时分**
- 或 **70% 考试卷面分 + 30% 平时分**

具体的分数构成老师会在课上公布。`},{id:"main_exam",title:"4. 新生考试",content:`> 本章主要面向理工科。根据不同的时间安排，学校会公布 1~2 周的复习周（注意，新生可能没有复习周！），复习周通常已经结课，由学生自行复习。

![考试记忆力矛盾](${_.memory})

来不及哀悼高考的结束了，接下来奔赴战场的是高数、线代、C语言三幻神。

:::callout emoji="⚔️"
我说白了，现实里谁不想跑去急头白脸地打一场期末考试，一边跟三个考试一起喊"领域展开"一边给自己脑放一首 AIZO 激情拼手速，然后苟到期末评教，被成绩抽死前嘴一句绞尽脑汁想出来的抽象梗当遗言。
:::

当然大一可以说是最简单的考试了，正常 2-3 天**高强度复习**可以让一门课速成到及格。如果想要及格以上的分数，那请好好学习。可以参考：

![框框老师](${_.kuangkuang})

![猴博士](${_.monkey})

![期末速成课程](${_.sucai})

![宋浩高等数学](${_.songhao})`},{id:"main_after",title:"5. 新生模型后训练",content:`考试结束后，你可能会陷入一个贤者状态，开始思考：上课是为了什么？成绩怎么计算？我读大学是为了什么？

读书必须明确一点：**大学仅仅是提供一个平台以及学历证明。** 目前就业市场跟学校培养是失衡的，市场需求技术飞速发展，但大学课程的培养方案需要时间规划。我们必须善用学校平台以及自学，尽量在大二之前确定自己的发展路线规划——是准备直接就业，还是继续提升学历？

![天才在左疯子在右](${_.genius})

> 你已经过 18 了，错过了觉醒异能的最佳年龄，不可能是埋没的天才电竞少年，不可能作为高中生拯救世界了，不可能因为转学坐到美少女旁边开始一段青春恋爱，也不可能穿越到异世界成为勇者打败魔王，不可能加入濒临倒闭的社团，和一群奇怪的人在毕业前完成最后一次乐队演出。

如果准备就业：大一到大二积累基础技术，增加项目，大三/大二进行实习。

如果准备提升学历：研究自己的升学方法。`},{id:"main_gpa",title:"6. 新生绩点综测",content:`你可以通过点击网页版教务系统 → 成绩查询 → 全部 → 最好成绩，导出完整成绩单并计算总绩点。

![教务系统成绩查询](${_.score})

综测方面，学代团收到通知，今年会更新综测规则，在此不做介绍。综测主要作用于奖学金等，请点击常用链接查看学生工作管理系统。`}]},{id:"sidequest",title:"新生支线剧情篇",icon:"🗺️",sections:[{id:"side_title",title:"1. 称号与加入势力",content:`入学开始，学校各学院会有班委竞选以及学生组织扫楼或者是社团之夜等活动。各位同学可以考虑是否要获取"称号"（班委）或"加入势力"（学生组织/社团）。

称号中，班长、团支书、学委、学代属于特殊称号——前三者对比其他班委有更大概率获得信息差资讯、综测加分、学生干部活动优先、学生干部奖学金等，但是事务繁忙。第四个称号"学生代表"，将自动加入势力"学生代表团"。

![加入信科院势力](${_.xinke})

> 本院玩家创立的势力包括：暨大 PTCG 战队、暨大机器人 SSR 战队、无限战队`},{id:"side_map",title:"2. 大地图探索",content:`### 2.1 图书馆北侧

常刷新资讯的点位。正门北侧有一片空地，经常刷新摊位、海报。摊位大多数由各学院的学生组织举办活动而起；海报作为公告栏，可能随机刷新比赛、活动等信息，也有概率公布本服优秀玩家（优秀学生），此时有概率开启支线任务剧情——竞赛章。

### 2.2 快递站

位于 T12 后方、T11 楼侧。内部包括菜鸟驿站、京东快递、顺丰快递，同时有一间驾校报名点。面向快递站右侧楼梯下去是学生活动中心 W2，是部分学生组织势力驻点与学生处驻点。

### 2.3 校友会

该组织不存在于现实地图上。在微信搜索暨南大学校友会公众号，点击校友卡并登记资料注册，将获得校友福利——顺丰快递会员、华住会会员、南方航空会员等。

### 2.4 知识产权大楼

1313 是我们学院辅导员所在的办公室，正对面阳台是沙发休息空间。如果需要拜访 NPC（导员），请提前微信互通，避免 NPC 刷新在其他地方。

### 2.5 实验室

实验室机房分布于两个地方：教学楼 113 等机房（通常在实验课使用），南门实验楼（机房和物理实验室）。机房内部电脑可能有损坏或配置不足情况，在情况许可下可自行携带电脑。

### 2.6 镜湖

位于南门与图书馆正中间，范围极大，有两座桥横跨镜湖。该地图存在特殊生物：鹅、鱼、蚊子。会随机刷新 NPC：保安、情侣。其边缘较危险，需要避免靠近落水。

### 2.7 教学楼

位于食堂侧面，为主线剧情地图。课室两侧均匀分布少量的插口可以充电。入夏未达到温度标准时，有概率不开放空调，请自行带备降温物品。

### 2.8 图书馆

探索支线剧情的重要地图，其中还有地图建筑自修室。夏天空调极冷，非夏季可能无空调。图书馆需要刷校园卡/登记/扫码进入。开馆时间：周一至周日 7:00~22:00；周五 7:00~17:00。自修室没有时间限制，但座位有限，每周五上午清理无人座位。

### 2.9 操场

东门侧面有东操场，兴安后方有西操场与游泳馆。操场全日开放供学生使用，游泳馆需查看开放通知。支线任务"体测章"将于东操场开展。

![校园规划效果图](${_.campus})`},{id:"side_branches",title:"3. 支线剧情攻略",content:`### 3.1 竞赛章

该支线任务可能会在公众号、班级禁水群聊、或学长邀请下触发。通常技术类竞赛往往具有一些门槛，难以在大一上参与。建议先增加个人项目积累和技术学习，把前期点数点到智慧上，同时进行技能学习，避免接取支线任务后无法完成，导致拖慢前期主线剧情进度。

### 3.2 体测章

该支线任务全称"国家学生体质健康标准测试"，分数将与体育课分数挂钩。重点得分项目：BMI、肺活量、50m跑、800/1000m跑。男生会有较高难度的引体向上项目。该支线任务必须接取——想要完成必须开启空闲时候的锻炼，定期前往操场跑步，增加多余点数到体质上。

### 3.3 恋爱章

该支线任务有概率成为终身任务，但在本学院任务接取难度较大。由于学院序列途径的污染，容易长期无法触发任务。可以尝试在其他支线任务上触发，或者联络其他学院玩家，绕开污染。

### 3.4 学生组织/社团章

该支线任务可以通过刷取熟练度、参与势力内部势力任务，触发特殊玩法和隐藏结局——"思政保研"。但隐藏结局通关难度较大。称号分为系→院→校三级，仅院/校级优秀学生干部可能触发，而社团势力无法触发，仅为休闲玩法。

### 3.5 勤工俭学章

该支线任务适合家庭有需要的同学。加入学院官方勤工俭学组织需要审核，非有需要的同学可能无法加入。需要刷取金币的玩家可以尝试加入外部任务——代拿、跑腿、家教、兼职等，或通过主线/支线任务奖励获取金币：奖学金、比赛奖金、课程助教劳务费等。

### 3.6 NPC/玩家攻略章

通过 NPC 交互也有概率触发特殊剧情和人物，包括但不限于加入玩家势力、赠送礼物给高年级玩家、请教老师、协助老师工作等。

:::callout emoji="🤬"
★☆☆☆☆

谁给我下了项羽 mod，四面楚歌，周围全是楚声。根本没人攻略我，一直在攻击我，嘎拉 game 不是这样的！
:::`}]},{id:"items",title:"道具攻略",icon:"🎒",sections:[{id:"items_all",title:"新手装备采购清单",content:["| 类别 | 物品 | 备注 |","|------|------|------|","| **床上用品** | 床垫、被子、枕头、床单、枕套、床帘 | 宿舍床铺尺寸 1.9m × 0.9m。番禺校区蚊虫极多，床帘建议选择全包。全包坏处是稍微有点热，可备一小风扇在床上 |","| **洗漱用品** | 牙刷、牙膏、毛巾、漱口杯、洗发水、沐浴露、洗面奶、脸盆、水桶 | 可到校后超市购买，但是超市价格真的偏贵 |","| **衣物类** | 衣物、**拖鞋**、运动鞋、晾衣杆、衣架、夹子 | 广州夏天长，冬天非常短，多备夏装。基本 12 月中下旬才会转寒 |","| **清洁用品** | **洗衣液/洗衣粉**、垃圾桶、垃圾袋、拖把、扫把、抹布 | 宿舍公共用品可 AA 合买。岭南恶劣之地，勤扔垃圾，免招广东双马尾 |","| **电子设备** | 手机+充电器、电脑+充电器、充电宝、排插（多口）、耳机、网线 | 排插还是挺有用的。如果需要电池之类的小东西，直接去兴安买就行 |","| **医药用品** | **驱蚊水**、感冒药、肠胃药、创可贴、退烧药、风油精、防晒霜 | 广东蚊虫非常多！宿舍并没有安装网纱，通风时会导致蚊子入侵，驱蚊药或蚊香很需要。药品可以直接在校医室买，有医保更便宜。**不要相信天气预报**，莫名其妙就会来一场过云雨 |","| **其他** | **雨伞**、水杯、指甲剪套装、台灯、小风扇 | 广州多雨，伞必备 |"].join(`
`)}]}],Se={class:"quest-root"},qe={class:"quest-topbar"},Te={key:1,class:"levels-root"},Be={class:"levels-header"},we={class:"levels-grid"},De=["disabled","onClick"],Le={class:"level-card__inner"},Ae={class:"level-card__icon"},Me={class:"level-card__num"},Oe={class:"level-card__title"},ze={class:"level-card__progress"},Ee={class:"level-card__bar"},Ge={key:0,class:"level-card__lock"},Je={key:1,class:"level-card__done"},Qe={key:2,class:"reader-root"},Ue={class:"reader-top"},Ve={class:"reader-top__meta"},We={class:"reader-top__icon"},Re={class:"reader-top__title"},Xe={key:0,class:"reader-top__progress"},Ke={class:"reader-section__header"},Ye={class:"reader-section__num"},Ze={class:"reader-section__title"},Fe=["innerHTML"],He={key:0,class:"reader-section__footer"},es=["onClick"],ss={class:"reader-section__check-icon"},ts={key:0,class:"reader-next-chapter"},ns={key:1,class:"reader-next-chapter"},as={key:2,class:"reader-done"},is=U({__name:"QuestView",setup(u){const m=ae(),t=Ie,c=ee(pe()),C=I(c.hasSeenIntro?"levels":"login"),b=I(0),x=I(null),r=j(()=>t.every(n=>p(n.id)===100)),y=j(()=>{for(let n=0;n<t.length;n++)if(p(t[n].id)<100)return n;return Math.min(t.length-1,3)}),R=j(()=>p("login")<100?1:p("mainline")<100?2:4),T=j(()=>b.value>=t.length-1),g=j(()=>t[b.value]??null);function p(n){const s=t.find(h=>h.id===n);if(!s||s.sections.length===0)return 0;const $=s.sections.filter(h=>f(h.id)).length;return Math.round($/s.sections.length*100)}function f(n){return c.mainComplete.includes(n)}function X(n){const s=c.mainComplete.indexOf(n);s>=0?c.mainComplete.splice(s,1):c.mainComplete.push(n),q({...c})}function K(){c.hasSeenIntro=!0,q({...c}),C.value="levels"}function Y(n){b.value=n,C.value="reading",w()}function Z(){C.value="levels"}function B(){b.value<t.length-1&&(b.value++,w())}function F(){for(const n of t)for(const s of n.sections)f(s.id)||c.mainComplete.push(s.id);q({...c}),m.push("/")}function w(){ne(()=>{x.value&&(x.value.scrollTop=0)})}return(n,s)=>{var $,h,D,L,A,M,O,z,E,G;return i(),l("div",Se,[e("header",qe,[e("button",{class:"quest-topbar__back",onClick:s[0]||(s[0]=a=>n.$router.push("/"))},[se(oe,{name:"back",size:20}),s[3]||(s[3]=e("span",{class:"quest-topbar__back-label"},"返回",-1))]),s[4]||(s[4]=e("span",{class:"quest-topbar__title"},"🎮 新手任务",-1)),s[5]||(s[5]=e("span",{class:"quest-topbar__ver"},"v2.0",-1))]),C.value==="login"?(i(),te(ue,{key:0,onDone:K})):C.value==="levels"?(i(),l("div",Te,[e("div",Be,[e("h2",null,o(r.value?"全部通关！":"选择关卡"),1),e("p",null,o(r.value?"可随意翻阅任意章节":"完成当前关卡以解锁下一关"),1)]),e("div",we,[(i(!0),l(J,null,Q(N(t),(a,v)=>(i(),l("button",{key:a.id,class:S(["level-card",{"level-card--unlocked":r.value||v<R.value,"level-card--current":!r.value&&v===y.value,"level-card--locked":!r.value&&v>y.value,"level-card--done":p(a.id)===100}]),disabled:!r.value&&v>y.value,onClick:P=>Y(v)},[e("div",Le,[e("span",Ae,o(a.icon),1),e("span",Me,"关卡 "+o(v+1),1),e("span",Oe,o(a.title),1),e("div",ze,[e("div",Ee,[e("div",{class:"level-card__fill",style:ie({width:p(a.id)+"%"})},null,4)]),e("span",null,o(p(a.id))+"%",1)]),!r.value&&v>y.value?(i(),l("span",Ge,"🔒")):p(a.id)===100?(i(),l("span",Je,"✅")):k("",!0)])],10,De))),128))])])):(i(),l("div",Qe,[e("div",Ue,[e("button",{class:"reader-top__back",onClick:Z},[...s[6]||(s[6]=[e("span",null,"← 返回关卡选择",-1)])]),e("div",Ve,[e("span",We,o(($=g.value)==null?void 0:$.icon),1),e("span",Re,o((h=g.value)==null?void 0:h.title),1)]),!r.value&&((D=g.value)==null?void 0:D.id)==="login"?(i(),l("div",Xe," 已完成 "+o(p(((L=g.value)==null?void 0:L.id)??""))+"% ",1)):k("",!0)]),e("div",{class:"reader-sections",ref_key:"sectionsEl",ref:x},[(i(!0),l(J,null,Q(((A=g.value)==null?void 0:A.sections)??[],(a,v)=>{var P;return i(),l("div",{key:a.id,class:S(["reader-section",{"reader-section--done":f(a.id)}])},[e("div",Ke,[e("span",Ye,o(v+1),1),e("h3",Ze,o(a.title),1)]),e("div",{class:"reader-section__body",innerHTML:N(le)(a.content)},null,8,Fe),!r.value&&((P=g.value)==null?void 0:P.id)==="login"?(i(),l("div",He,[e("button",{class:S(["reader-section__check",{done:f(a.id)}]),onClick:os=>X(a.id)},[s[7]||(s[7]=e("span",{class:"reader-section__glow"},null,-1)),e("span",ss,o(f(a.id)?"✓":"○"),1),e("span",null,o(f(a.id)?"已完成":"标记完成"),1)],10,es)])):k("",!0)],2)}),128)),!r.value&&((M=g.value)==null?void 0:M.id)!=="login"&&!T.value?(i(),l("div",ts,[e("button",{class:"reader-next-chapter__btn",onClick:s[1]||(s[1]=a=>B())},[e("span",null,"进入下一关："+o((O=N(t)[b.value+1])==null?void 0:O.title),1),s[8]||(s[8]=e("span",{class:"reader-next-chapter__arrow"},"→",-1))])])):k("",!0),!r.value&&((z=g.value)==null?void 0:z.id)!=="login"&&T.value?(i(),l("div",ns,[e("button",{class:"reader-next-chapter__btn reader-next-chapter__btn--home",onClick:F},[...s[9]||(s[9]=[e("span",null,"🎉 全部通关！返回首页",-1)])])])):k("",!0),!r.value&&((E=g.value)==null?void 0:E.id)==="login"&&p("login")===100?(i(),l("div",as,[s[10]||(s[10]=e("span",{class:"reader-done__icon"},"🎊",-1)),s[11]||(s[11]=e("p",null,"第一章全部完成！",-1)),e("button",{class:"reader-done__next",onClick:s[2]||(s[2]=a=>B())}," 进入下一关："+o((G=N(t)[1])==null?void 0:G.title)+" → ",1)])):k("",!0)],512)]))])}}}),ds=V(is,[["__scopeId","data-v-6f0581f7"]]);export{ds as default};
