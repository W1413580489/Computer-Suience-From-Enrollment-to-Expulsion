<template>
  <div class="appendix-list">
    <button
      v-for="item in items"
      :key="item.label"
      class="appendix-list__item"
      @click="emit('onItemClick', item)"
    >
      <NeonIcon :name="item.restricted ? 'lock' : (item.icon ?? 'doc')" :size="20" class="appendix-list__icon" />
      <span class="appendix-list__text">
        <span class="appendix-list__label">
          {{ item.label }}
          <span v-if="item.restricted" class="appendix-list__restricted">需验证</span>
        </span>
        <span v-if="item.desc" class="appendix-list__desc">{{ item.desc }}</span>
      </span>
      <NeonIcon name="external" :size="15" class="appendix-list__arrow" />
    </button>
  </div>
</template>

<script setup lang="ts">
import NeonIcon from '@/components/common/NeonIcon.vue';
import type { AppendixItem } from '@/types/nav';

defineProps<{ items: AppendixItem[] }>();
const emit = defineEmits<{ onItemClick: [item: AppendixItem] }>();
</script>

<style scoped>
.appendix-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 10px;
}

.appendix-list__item {
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 80px;
  padding: 14px 16px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  text-align: left;
  transition: border-color 200ms, box-shadow 200ms, transform 200ms;
}

.appendix-list__item:hover {
  border-color: var(--accent-primary);
  box-shadow: var(--shadow-glow);
  transform: translateY(-1px);
}

.appendix-list__item:active {
  transform: scale(0.98);
}

.appendix-list__icon {
  color: var(--accent-primary);
  flex-shrink: 0;
}

.appendix-list__text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.appendix-list__label {
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.appendix-list__restricted {
  font-size: 10px;
  color: var(--accent-warn);
  border: 1px solid var(--accent-warn);
  border-radius: var(--radius-sm);
  padding: 1px 5px;
  flex-shrink: 0;
}

.appendix-list__desc {
  font-size: 12px;
  color: var(--text-secondary);
}

.appendix-list__arrow {
  color: var(--text-muted);
  flex-shrink: 0;
}

@media (max-width: 767px) {
  .appendix-list {
    grid-template-columns: 1fr;
  }
}
</style>
