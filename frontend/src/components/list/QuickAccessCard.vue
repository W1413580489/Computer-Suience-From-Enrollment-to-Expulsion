<template>
  <button class="qa-card" @click="emit('onClick')">
    <span class="qa-card__icon-wrap">
      <NeonIcon :name="icon" :size="26" class="qa-card__icon" />
    </span>
    <span class="qa-card__text">
      <span class="qa-card__label">{{ label }}</span>
      <span class="qa-card__desc">{{ desc }}</span>
    </span>
    <NeonIcon name="arrow-right" :size="20" class="qa-card__arrow" />
  </button>
</template>

<script setup lang="ts">
import NeonIcon from '@/components/common/NeonIcon.vue';

withDefaults(defineProps<{ icon?: string; label: string; desc: string }>(), { icon: 'doc' });
const emit = defineEmits<{ onClick: [] }>();
</script>

<style scoped>
.qa-card {
  display: flex;
  align-items: center;
  gap: 14px;
  width: 100%;
  min-height: 92px;
  padding: 14px 16px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  text-align: left;
  transition: border-color 200ms, box-shadow 200ms, transform 200ms;
}

.qa-card:hover {
  border-color: var(--amber);
  box-shadow: 0 0 18px var(--amber-glow);
  transform: translateY(-2px);
}

.qa-card:active {
  transform: scale(0.98);
}

.qa-card__icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  background: var(--bg-panel-3);
  border: 1px solid var(--border-subtle);
  flex-shrink: 0;
  transition: border-color 200ms, background 200ms;
}

.qa-card:hover .qa-card__icon-wrap {
  border-color: var(--amber);
  background: rgba(255, 200, 46, 0.12);
}

.qa-card__icon {
  color: var(--amber);
}

.qa-card__text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.qa-card__label {
  font-size: 16px;
  font-weight: 600;
}

.qa-card__desc {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.qa-card__arrow {
  color: var(--text-muted);
  transition: color 200ms, transform 200ms;
}

.qa-card:hover .qa-card__arrow {
  color: var(--amber);
  transform: translateX(3px);
}
</style>
