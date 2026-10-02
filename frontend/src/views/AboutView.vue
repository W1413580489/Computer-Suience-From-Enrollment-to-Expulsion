<template>
  <PageShell title="关于信科院智能助手" subtitle="ABOUT · 创建者与项目说明" active-key="about">
    <section class="about-section">
      <h2 class="about-h2">本站身份卡</h2>
      <p class="about-p">
        信科院智能助手是由暨南大学信科院学生王叔发起的学习与 AI 工具站，非学校官方平台。
      </p>
      <dl class="about-card">
        <dt>站名</dt>
        <dd>信科院智能助手（项目代号 XKZ-Agent）</dd>
        <dt>创建者</dt>
        <dd>王叔 · 暨南大学信息科学技术学院计算机科学与技术专业 2022 级学生</dd>
        <dt>网站性质</dt>
        <dd>由学生发起并独立维护的非官方学习与 AI 工具站</dd>
        <dt>主要内容</dt>
        <dd>学生指南、校园 RAG 问答、AI 工具、AI 项目制教学与项目实践</dd>
        <dt>服务对象</dt>
        <dd>暨南大学在校同学（信科院为主）</dd>
        <dt>官网</dt>
        <dd><a class="about-link" href="https://jnuxky.xyz/">https://jnuxky.xyz/</a></dd>
        <dt>开源仓库</dt>
        <dd>
          <a
            class="about-link"
            href="https://github.com/W1413580489/Computer-Suience-From-Enrollment-to-Expulsion"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub · 信科院智能助手源码与文档 →
          </a>
        </dd>
      </dl>
    </section>

    <section class="about-section">
      <h2 class="about-h2">创建者 · 王叔</h2>
      <p class="about-p">
        王叔，暨南大学信息科学技术学院计算机科学与技术专业 2022 级学生，信科院智能助手（jnuxky.xyz）的创建者与维护者。
      </p>
      <p class="about-p">
        最初只想把同学们高频问过的问题整理成文字指南——累计约 15 万字、20 篇主题，覆盖新生选课、学术规划、就业竞赛、反诈与生活等。后来同学们反映"文字太多、翻不动"，他便把指南接入 RAG 知识库，做成校园问答机器人回答同学疑问。
      </p>
      <p class="about-p">
        与此同时，同学反馈学校里缺少合适的 AI 编程教育与 AI 使用入门，也缺少真正的项目经历，而第一段项目经历往往是写简历、进课题组、拿第一份实习的关键起点。为此他开发了 AI 导师（目前课程为：课程 01 套壳聊天机器人、课程 02 GitHub 项目分析 Agent、课程 03 MCP 项目记忆服务），把「怎么教 AI 写代码」变成可以对照标准、被逐条评审的练手课程。
      </p>
      <p class="about-p">
        网站文档与功能均由学生独立开发维护，贡献者名单见网站「鸣谢」页。平台非学校官方，是面向暨南大学同学的开放式学习社区。
      </p>
      <p class="about-link-row">
        <router-link class="about-link" to="/teach">进入 AI 项目导师 →</router-link>
        <router-link class="about-link" to="/faq">常见问题 →</router-link>
        <router-link class="about-link" to="/thanks">查看「鸣谢」贡献者档案馆 →</router-link>
      </p>
    </section>

    <section class="about-section">
      <h2 class="about-h2">项目说明</h2>
      <p class="about-p">
        信科院智能助手（XKZ-Agent）是面向暨南大学信息科学技术学院学生的校园知识问答机器人。
        问答内容基于指南《信科院-从入学到被开除》（文档11章节11子文档，共8.1万余字），
        支持自带大模型 API Key（BYOK）免费提问，未配置 Key 的用户每日享有限量免费额度。
        受服务器资源限制，免费额度有限，建议配置自己的 API Key 以获得更稳定完整的体验。
      </p>
    </section>

    <section class="about-section">
      <h2 class="about-h2">内容来源与署名</h2>
      <p class="about-p">
        本站全部问答内容来自《信科院-从入学到被开除》共创文档的作者，
        本站仅做检索与问答引用，原文版权归创作者所有。
      </p>
      <a
        class="about-link"
        href="https://tralis2671.feishu.cn/wiki/VvKVwsHo2iIIC4ko0PmcKs4lnKd"
        target="_blank"
        rel="noopener noreferrer"
      >
        《信科院-从入学到被开除》主页 →
      </a>
    </section>

    <section class="about-section">
      <h2 class="about-h2">免责声明</h2>
      <p class="about-p about-p--warn">
        内容共创，政策以学校最新通知为准。
      </p>
    </section>

    <section class="about-section">
      <h2 class="about-h2">隐私说明</h2>
      <p class="about-p">
        你的 API Key 仅保存在本浏览器本地存储中，后端只用于单次请求转发，不记录、不保存；
        问答日志仅记录脱敏信息（问题哈希、耗时、命中文档），不保存对话原文。
      </p>
    </section>

    <section class="about-section">
      <h2 class="about-h2">反馈</h2>
      <p class="about-p">
        回答页每条回答下有点赞 / 点踩按钮，你的反馈会用于改进检索与内容质量。
        内容勘误请直接到飞书原文档评论区留言。
      </p>
    </section>
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from '@/components/common/PageShell.vue';
</script>

<style scoped>
.about-section {
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-top: 3px solid var(--amber);
  clip-path: var(--clip-md);
  padding: 18px 20px;
  margin-bottom: 14px;
}

.about-h2 {
  font-size: 15px;
  font-weight: 700;
  color: var(--amber);
  margin-bottom: 10px;
}

.about-p {
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-secondary);
}

.about-p--warn {
  color: var(--warning);
}

/* 身份卡：机器可解析的「键 - 值」结构（也便于 AI 直接提取事实） */
.about-card {
  margin-top: 12px;
  display: grid;
  grid-template-columns: 76px 1fr;
  gap: 8px 14px;
  font-size: 13px;
  line-height: 1.8;
}

.about-card dt {
  color: var(--amber);
  font-weight: 700;
}

.about-card dd {
  margin: 0;
  color: var(--text-secondary);
}

.about-card .about-link {
  margin-top: 0;
}

.about-link-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 18px;
  margin-top: 10px;
}

.about-link-row .about-link {
  margin-top: 0;
}

@media (max-width: 640px) {
  .about-card {
    grid-template-columns: 1fr;
    gap: 0;
  }

  .about-card dd {
    margin-bottom: 8px;
  }
}

.about-link {
  display: inline-block;
  margin-top: 10px;
  font-size: 13px;
}

.about-link:hover {
  text-decoration: underline;
}
</style>
