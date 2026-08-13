<template>
  <header class="section-header">
    <span class="section-header__num">// {{ num }}</span>
    <h2 class="section-header__title">{{ title }}</h2>
    <span class="section-header__en">{{ en }}</span>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  num: string;
  title: string;
  en: string;
}>();
</script>

<style scoped>
/* 参考绝区零设计指南 .section-header：编号 + 大标题 + 英文辅助 */
.section-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 48px;
}

.section-header__num {
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--amber);
}

.section-header__title {
  font-family: var(--font-display);
  font-size: clamp(32px, 5vw, 48px);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: 0.05em;
  color: var(--text-primary);
}

.section-header__en {
  font-family: var(--font-mono);
  font-size: 13px;
  letter-spacing: 5px;
  color: var(--text-secondary);
  text-transform: uppercase;
}

@media (max-width: 767px) {
  .section-header {
    gap: 6px;
    margin-bottom: 32px;
  }

  .section-header__title {
    font-size: 28px;
  }

  .section-header__en {
    font-size: 11px;
    letter-spacing: 4px;
  }
}
</style>
