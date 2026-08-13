<template>
  <button class="qa-card" @click="emit('onClick')">
    <!-- 票据主体 -->
    <span class="qa-card__main">
      <span class="qa-card__icon-wrap">
        <NeonIcon :name="icon" :size="26" class="qa-card__icon" />
      </span>
      <span class="qa-card__text">
        <span class="qa-card__label">{{ label }}</span>
        <span class="qa-card__desc">{{ desc }}</span>
      </span>
    </span>
    <!-- 票根存根 -->
    <span class="qa-card__stub">
      <span class="qa-card__stub-label">ACCESS</span>
      <NeonIcon name="arrow-right" :size="16" class="qa-card__arrow" />
    </span>
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
  align-items: stretch;
  width: 100%;
  min-height: 92px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-md);
  color: var(--text-primary);
  text-align: left;
  transition: border-color 200ms, box-shadow 200ms, transform 200ms;
  overflow: hidden;
}

.qa-card:hover {
  border-color: var(--amber);
  box-shadow: 0 0 18px var(--amber-glow);
  transform: translateY(-2px);
}

.qa-card:active {
  transform: scale(0.98);
}

/* 票据主体 */
.qa-card__main {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  padding: 14px 16px;
  min-width: 0;
}

.qa-card__icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  clip-path: var(--clip-sm);
  background: var(--bg-panel-3);
  border: 1px solid var(--border-subtle);
  flex-shrink: 0;
  transition: border-color 200ms, background 200ms;
}

.qa-card:hover .qa-card__icon-wrap {
  border-color: var(--amber);
  background: var(--amber-soft);
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

/* 票根存根 — 右侧撕扯条 */
.qa-card__stub {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 56px;
  padding: 14px 8px;
  background: var(--bg-panel-2);
  border-left: 2px dashed var(--border-subtle);
  flex-shrink: 0;
  transition: border-color 200ms, background 200ms;
}

.qa-card:hover .qa-card__stub {
  border-left-color: var(--amber);
  background: var(--amber-deep-soft);
}

.qa-card__stub-label {
  font-family: var(--font-mono);
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 3px;
  color: var(--text-muted);
  writing-mode: vertical-rl;
  text-orientation: mixed;
  text-transform: uppercase;
  transition: color 200ms;
}

.qa-card:hover .qa-card__stub-label {
  color: var(--amber);
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
