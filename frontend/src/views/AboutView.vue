<template>
  <PageShell title="关于我" subtitle="ABOUT · 开发者与网站说明" active-key="about">
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
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  margin-bottom: 14px;
}

.about-h2 {
  font-size: 15px;
  font-weight: 600;
  color: var(--accent-bright);
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

.about-link {
  display: inline-block;
  margin-top: 10px;
  font-size: 13px;
}

.about-link:hover {
  text-decoration: underline;
}
</style>
