<template>
  <div class="guides-list">
    <button
      v-for="item in items"
      :key="item.label"
      class="guides-list__item"
      @click="emit('onItemClick', item)"
    >
      <NeonIcon :name="item.icon ?? 'doc'" :size="20" class="guides-list__icon" />
      <span class="guides-list__text">
        <span class="guides-list__label">{{ item.label }}</span>
        <span v-if="item.desc" class="guides-list__desc">{{ item.desc }}</span>
      </span>
      <NeonIcon name="external" :size="15" class="guides-list__arrow" />
    </button>
  </div>
</template>

<script setup lang="ts">
import NeonIcon from '@/components/common/NeonIcon.vue';
import type { GuideItem } from '@/types/nav';

defineProps<{ items: GuideItem[] }>();
const emit = defineEmits<{ onItemClick: [item: GuideItem] }>();
</script>

<style scoped>
.guides-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 10px;
}

.guides-list__item {
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

.guides-list__item:hover {
  border-color: var(--accent-primary);
  box-shadow: var(--shadow-glow);
  transform: translateY(-1px);
}

.guides-list__item:active {
  transform: scale(0.98);
}

.guides-list__icon {
  color: var(--accent-primary);
  flex-shrink: 0;
}

.guides-list__text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.guides-list__label {
  font-size: 16px;
  font-weight: 600;
}

.guides-list__desc {
  font-size: 13px;
  color: var(--text-secondary);
}

.guides-list__arrow {
  color: var(--text-muted);
  flex-shrink: 0;
}

@media (max-width: 767px) {
  .guides-list {
    grid-template-columns: 1fr;
  }
}
</style>
