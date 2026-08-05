<template>
  <aside class="sidenav">
    <button
      v-for="item in items"
      :key="item.key"
      class="sidenav__item"
      :class="{ 'sidenav__item--active': activeKey === item.key }"
      @click="emit('onItemClick', item.route)"
    >
      <NeonIcon :name="item.icon" :size="24" class="sidenav__icon" />
      <span class="sidenav__text">
        <span class="sidenav__label">{{ item.label }}</span>
        <span class="sidenav__sublabel">{{ item.subLabel }}</span>
      </span>
      <span class="sidenav__number">{{ item.number }}</span>
    </button>
  </aside>
</template>

<script setup lang="ts">
import NeonIcon from '@/components/common/NeonIcon.vue';
import type { SideMenuItem } from '@/types/nav';

defineProps<{ items: SideMenuItem[]; activeKey: string }>();
const emit = defineEmits<{ onItemClick: [route: string] }>();
</script>

<style scoped>
.sidenav {
  width: var(--sidenav-w);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 20px 14px;
  overflow-y: auto;
}

.sidenav__item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 64px;
  padding: 10px 14px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-subtle);
  background: var(--bg-panel);
  color: var(--text-secondary);
  text-align: left;
  transition: background 200ms, border-color 200ms, color 200ms, transform 200ms;
}

.sidenav__item:hover {
  border-color: var(--amber);
  color: var(--amber);
  transform: translateX(4px);
}

.sidenav__item--active {
  background: linear-gradient(135deg, var(--amber) 0%, var(--amber-deep) 100%);
  border-color: var(--amber);
  color: var(--on-amber);
  box-shadow: 0 4px 20px var(--amber-glow);
}

.sidenav__icon {
  flex-shrink: 0;
}

.sidenav__text {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
  min-width: 0;
  flex: 1;
}

.sidenav__label {
  font-size: 15px;
  font-weight: 600;
}

.sidenav__sublabel {
  font-family: var(--font-display);
  font-size: 11px;
  letter-spacing: 2px;
  color: var(--text-muted);
}

.sidenav__item--active .sidenav__sublabel {
  color: var(--on-amber-muted);
}

.sidenav__number {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
}

.sidenav__item--active .sidenav__number {
  color: var(--on-amber-faint);
}

/* 平板折叠态：仅图标 */
@media (min-width: 768px) and (max-width: 1279px) {
  .sidenav {
    padding: 16px 8px;
  }
  .sidenav__text,
  .sidenav__number {
    display: none;
  }
  .sidenav__item {
    justify-content: center;
    min-height: 64px;
    padding: 8px;
  }
}
</style>
