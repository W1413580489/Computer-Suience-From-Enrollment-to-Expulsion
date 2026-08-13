<template>
  <nav class="ext-system" aria-label="外部系统">
    <span class="ext-system__label">EXTERNAL SYSTEM</span>
    <div class="ext-system__list">
      <button
        v-for="item in items"
        :key="item.label"
        class="ext-system__item"
        @click="emit('onItemClick', item)"
      >
        <span class="ext-system__dot" />
        <span>{{ item.label }}</span>
      </button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import type { FooterToolItem } from '@/types/nav';

defineProps<{ items: FooterToolItem[] }>();
const emit = defineEmits<{ onItemClick: [item: FooterToolItem] }>();
</script>

<style scoped>
.ext-system {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px 24px;
  background: var(--bg-panel);
  border-top: 1px solid var(--border-subtle);
}

.ext-system__label {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 3px;
  color: var(--text-muted);
  text-transform: uppercase;
}

.ext-system__list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 24px;
}

.ext-system__item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 15.6px;
  color: var(--text-secondary);
  white-space: nowrap;
  transition: color 200ms;
}

.ext-system__item:hover {
  color: var(--amber);
}

.ext-system__dot {
  width: 5px;
  height: 5px;
  background: currentColor;
  opacity: 0.6;
  transition: opacity 200ms;
}

.ext-system__item:hover .ext-system__dot {
  opacity: 1;
}

@media (max-width: 767px) {
  .ext-system {
    padding: 12px 16px;
    gap: 8px;
  }

  .ext-system__list {
    gap: 16px;
  }

  .ext-system__item {
    font-size: 14.4px;
  }
}
</style>
