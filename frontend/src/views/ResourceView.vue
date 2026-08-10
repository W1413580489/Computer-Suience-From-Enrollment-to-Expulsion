<template>
  <div class="res-root">
    <header class="res-topbar">
      <button class="res-topbar__back" @click="$router.push('/')">
        <NeonIcon name="back" :size="20" />
        <span class="res-topbar__back-label">返回</span>
      </button>
      <span class="res-topbar__title">🔗 资源中心</span>
    </header>

    <div class="res-body">
      <div class="res-content" v-html="contentHtml" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import { renderMarkdown } from '@/composables/useMarkdown';

const rawContent = `# 🔗 常用链接

:::callout emoji="📚"
计算机学习路线 https://github.com/kamranahmedse/developer-roadmap

港澳台考研资料（由本院高少洋主任整理）：http://gatsexam.cc.cd/
:::

学生工作管理系统（包括综测，奖助学金，成绩管理等相关申请查询）https://stuit.jnu.edu.cn/

财务管理信息系统 https://cw.jnu.edu.cn/CASLogin.aspx

本科教务系统（教务系统网上办事服务大厅）https://jw.jnu.edu.cn/

暨南大学图书馆（可查阅全国各期刊论文）https://lib.jnu.edu.cn/

宿舍水电查询（需连校园网使用）https://pynhcx.jnu.edu.cn/ibsjnuweb/

校园网维修入口 https://mynet.jnu.edu.cn/app/#modules/customer/myHome.html

一键生成 EVA 风格的图片 https://lab.magiconch.com/eva-title/

---

**一些神奇妙妙小工具，需要一些神奇魔法：**

https://gemini.google.com/
https://chatgpt.com/
https://openai.com/

下载就对了，这是计算机学生的必经之路 https://www.yuanshen.com/`;

const contentHtml = computed(() => renderMarkdown(rawContent));
</script>

<style scoped>
.res-root {
  height: 100vh;
  height: 100dvh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  overflow: hidden;
}

.res-topbar {
  display: flex; align-items: center; gap: 12px;
  padding: 0 clamp(12px, 2vw, 16px);
  height: var(--topbar-h);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}
.res-topbar__back {
  display: flex; align-items: center; gap: 6px;
  font-size: clamp(13px, 2vw, 14px); color: var(--text-secondary);
  cursor: pointer; transition: color 150ms;
}
.res-topbar__back:hover { color: var(--text-primary); }
.res-topbar__title {
  flex: 1; font-size: clamp(15px, 2.5vw, 17px); font-weight: 600; color: var(--amber);
}

.res-body {
  flex: 1; overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.res-content {
  max-width: 680px;
  margin: 0 auto;
  padding: clamp(24px, 4vw, 36px) clamp(16px, 3vw, 24px);
  font-size: clamp(13px, 2vw, 15px);
  line-height: 1.9;
  color: var(--text-secondary);
}

/* Markdown styles (shared with quest reader) */
.res-content :deep(h1) { font-size: clamp(20px, 3.5vw, 26px); color: var(--amber); margin-bottom: .6em; }
.res-content :deep(h2) { font-size: clamp(16px, 2.5vw, 19px); color: var(--text-primary); border-bottom: 1px solid var(--border-subtle); padding-bottom: 6px; margin: 1.2em 0 .5em; }
.res-content :deep(h3) { font-size: clamp(14px, 2.2vw, 16px); color: var(--amber); margin: 1em 0 .4em; }
.res-content :deep(p) { margin-bottom: .8em; }
.res-content :deep(strong) { color: var(--text-primary); font-weight: 600; }
.res-content :deep(a) { color: var(--text-link); text-decoration: underline; text-underline-offset: 2px; word-break: break-all; }
.res-content :deep(a:hover) { color: var(--accent-bright); }
.res-content :deep(hr) { border: none; border-top: 1px solid var(--border-subtle); margin: 1.5em 0; }
.res-content :deep(blockquote) {
  border-left: 3px solid var(--amber);
  padding: clamp(8px, 1.5vw, 12px) clamp(12px, 2vw, 16px);
  margin: .8em 0; background: var(--amber-soft);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-size: .95em; color: var(--text-secondary);
}
.res-content :deep(blockquote strong) { color: var(--amber); }
.res-content :deep(ul) { padding-left: clamp(16px, 3vw, 22px); margin: .6em 0; }
.res-content :deep(li) { margin-bottom: .4em; line-height: 1.7; }

/* Callout blocks */
.res-content :deep(.quest-callout) {
  display: flex; gap: clamp(10px, 2vw, 14px);
  background: var(--bg-panel-3);
  border: 1px solid var(--border-subtle);
  border-left: 3px solid var(--amber);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  padding: clamp(12px, 2vw, 16px) clamp(14px, 2vw, 18px);
  margin: 1em 0;
}
.res-content :deep(.quest-callout__avatar) {
  font-size: clamp(22px, 3vw, 28px); flex-shrink: 0; line-height: 1;
  filter: drop-shadow(0 0 4px var(--amber-glow));
}
.res-content :deep(.quest-callout__body) { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.res-content :deep(.quest-callout__tag) {
  display: inline-block; font-family: var(--font-display);
  font-size: clamp(9px, 1.3vw, 10px); color: var(--amber); letter-spacing: 1px;
  border: 1px solid var(--amber-glow); border-radius: var(--radius-sm); padding: 2px 8px; opacity: .8;
  align-self: flex-start;
}
.res-content :deep(.quest-callout__body p) { font-size: clamp(12px, 1.8vw, 14px); line-height: 1.7; font-style: italic; margin: 0; }

@media (max-width: 640px) {
  .res-topbar__back-label { display: none; }
}
</style>
