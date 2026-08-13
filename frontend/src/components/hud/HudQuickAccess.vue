<template>
  <section class="quick-access">
    <header class="quick-access__header">
      <span class="quick-access__num">// 01</span>
      <h2 class="quick-access__title">快捷入口</h2>
      <span class="quick-access__subtitle">QUICK ACCESS</span>
    </header>
    <div class="quick-access__list">
      <QuickAccessCard
        v-for="(item, i) in items"
        :key="item.label"
        :icon="icons[i % icons.length]"
        :label="item.label"
        :desc="item.desc"
        @on-click="emit('onItemClick', item)"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import QuickAccessCard from '@/components/list/QuickAccessCard.vue';
import type { QuickAccessItem } from '@/types/nav';

defineProps<{ items: QuickAccessItem[] }>();
const emit = defineEmits<{ onItemClick: [item: QuickAccessItem] }>();

// 图标按卡片顺序循环（图标为装饰，数据全部来自 nav_config.json）
const icons = ['guide', 'academics', 'globe', 'user'];
</script>

<style scoped>
.quick-access__header {
  display: flex;
  align-items: baseline;
  gap: 10px;
  padding: 0 4px 14px;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: 4px;
}

.quick-access__num {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  color: var(--amber);
  letter-spacing: 1px;
}

.quick-access__title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
}

.quick-access__subtitle {
  font-family: var(--font-display);
  font-size: 11px;
  letter-spacing: 2px;
  color: var(--text-muted);
}

.quick-access__list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

@media (max-width: 767px) {
  .quick-access__list {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .quick-access__list :deep(.qa-card) {
    flex-direction: column;
    min-height: 0;
    text-align: center;
  }

  .quick-access__list :deep(.qa-card__main) {
    flex-direction: column;
    gap: 8px;
    padding: 14px 10px;
  }

  .quick-access__list :deep(.qa-card__stub) {
    display: none;
  }

  .quick-access__list :deep(.qa-card__icon-wrap) {
    width: 48px;
    height: 48px;
  }

  .quick-access__list :deep(.qa-card__desc) {
    display: none;
  }

  .quick-access__list :deep(.qa-card__label) {
    font-size: 14px;
  }
}
</style>
