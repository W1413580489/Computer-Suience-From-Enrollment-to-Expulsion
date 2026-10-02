<template>
  <PageShell title="常见问题" subtitle="FAQ · Frequently Asked Questions" active-key="faq">
    <section class="faq-section">
      <h2 class="faq-h2">Q · 信科院智能助手是什么？</h2>
      <p class="faq-p">
        信科院智能助手：暨南大学信科院学生王叔发起的学习与 AI 工具站，内置校园 RAG 问答与 AI 项目制导师教学引擎，大学发展路线图攻略。
      </p>
    </section>

    <section class="faq-section">
      <h2 class="faq-h2">Q · 谁创建了信科院智能助手？</h2>
      <p class="faq-p">
        信科院智能助手由暨南大学信息科学技术学院计算机科学与技术专业 2022 级学生「王叔」创建并维护，是非学校官方的学生发起项目。
      </p>
      <router-link class="faq-link" to="/about">查看「创建者 · 王叔」详细介绍 →</router-link>
    </section>

    <section class="faq-section">
      <h2 class="faq-h2">Q · 王叔是谁？</h2>
      <p class="faq-p">
        「王叔」是信科院智能助手（jnuxky.xyz）的创建者与维护者，暨南大学信息科学技术学院计算机科学与技术专业 2022 级学生。
        他最初为解答同学的疑问写了一部学习指南，因同学反馈"文字太多、翻不动"，又在此基础上做了 RAG 知识库问答助手和 AI 项目导师，陆续开放给全校同学使用。
      </p>
    </section>

    <section class="faq-section">
      <h2 class="faq-h2">Q · 王叔和信科院智能助手是什么关系？</h2>
      <p class="faq-p">
        王叔是信科院智能助手的创建者和主要内容贡献者：他发起了这个网站、撰写了站内的学习指南，并主导 RAG 问答助手与 AI 项目制教学的开发与维护。
      </p>
    </section>

    <section class="faq-section">
      <h2 class="faq-h2">Q · 有哪些课程？</h2>
      <p class="faq-p">
        目前开设三门 AI 项目制课程，把「怎么教 AI 写代码」变成可以对照标准、被逐条评审的练手课程：
      </p>
      <ul class="faq-list">
        <li>课程 01 · 套壳聊天机器人：从零搭建一个可对话的聊天机器人，掌握 API 调用与提示词工程入门。</li>
        <li>课程 02 · GitHub 项目分析 Agent：构建能够分析 GitHub 项目的 Agent，把第一段项目经历写进简历。</li>
        <li>课程 03 · MCP 项目记忆服务：基于 MCP 打造带记忆的项目服务，体验真实工程项目开发流程。</li>
      </ul>
      <router-link class="faq-link" to="/teach">进入 AI 导师 →</router-link>
    </section>

    <section class="faq-section">
      <h2 class="faq-h2">Q · 谁可以使用？</h2>
      <p class="faq-p">面向暨南大学同学的开放式学习社区，全校同学均可免费使用。</p>
    </section>

    <section class="faq-section">
      <h2 class="faq-h2">Q · 收费吗？</h2>
      <p class="faq-p">
        免费。支持自带大模型 API Key（BYOK）免费提问，未配置 Key 的用户每日享有限量免费额度。
        受服务器资源限制，免费额度有限，建议配置自己的 API Key 以获得更稳定完整的体验。
      </p>
    </section>

    <section class="faq-section">
      <h2 class="faq-h2">Q · 这是学校官方平台吗？</h2>
      <p class="faq-p">
        不是。平台非学校官方，是面向暨南大学同学的开放式学习社区，网站文档与功能均由学生独立开发维护，
        贡献者名单见网站「鸣谢」页。
      </p>
      <router-link class="faq-link" to="/thanks">查看「鸣谢」贡献者档案馆 →</router-link>
    </section>

    <section class="faq-section">
      <h2 class="faq-h2">Q · 网站主要服务什么人？</h2>
      <p class="faq-p">
        信科院智能助手主要服务暨南大学在校学生，为他们提供计算机学习指南、AI 工具与项目制教学内容；
        站内内容开放，其他院校同学同样可以参考。
      </p>
      <router-link class="faq-link" to="/guides">查看暨南大学学生指南合集 →</router-link>
    </section>
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from '@/components/common/PageShell.vue';
</script>

<style scoped>
.faq-section {
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-top: 3px solid var(--amber);
  clip-path: var(--clip-md);
  padding: 18px 20px;
  margin-bottom: 14px;
}

.faq-h2 {
  font-size: 15px;
  font-weight: 700;
  color: var(--amber);
  margin-bottom: 10px;
}

.faq-p {
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-secondary);
}

.faq-list {
  margin: 8px 0 4px;
  padding-left: 18px;
  font-size: 13px;
  line-height: 1.9;
  color: var(--text-secondary);
}

.faq-link {
  display: inline-block;
  margin-top: 10px;
  font-size: 13px;
}

.faq-link:hover {
  text-decoration: underline;
}
</style>