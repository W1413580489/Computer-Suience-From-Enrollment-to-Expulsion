<template>
  <nav class="footer-tools" aria-label="常用工具">
    <button
      v-for="(item, i) in items"
      :key="item.label"
      class="footer-tools__item"
      @click="emit('onItemClick', item)"
    >
      <NeonIcon :name="icons[i % icons.length]" :size="20" />
      <span class="footer-tools__label">{{ item.label }}</span>
    </button>
  </nav>
</template>

<script setup lang="ts">
import NeonIcon from '@/components/common/NeonIcon.vue';
import type { FooterToolItem } from '@/types/nav';

defineProps<{ items: FooterToolItem[] }>();
const emit = defineEmits<{ onItemClick: [item: FooterToolItem] }>();

// 图标按顺序循环（装饰性），数据全部来自 nav_config.json → footerTools
const icons = ['doc', 'mail', 'guide', 'globe', 'settings', 'home'];
</script>

<style scoped>
.footer-tools {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  height: var(--footer-h);
  background: var(--bg-panel);
  border-top: 1px solid var(--border-subtle);
  position: relative;
  z-index: 1;
  overflow-x: auto;
  padding: 0 16px;
}

.footer-tools__item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  white-space: nowrap;
  transition: color 200ms;
  min-height: 52px;
}

.footer-tools__item:hover {
  color: var(--accent-bright);
  text-decoration: underline;
}

@media (max-width: 767px) {
  .footer-tools {
    justify-content: flex-start;
    gap: 18px;
    height: 52px;
  }
}
</style>
