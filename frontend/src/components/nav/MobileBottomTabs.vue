<template>
  <nav class="bottom-tabs" aria-label="底部导航">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      class="bottom-tabs__tab"
      :class="{
        'bottom-tabs__tab--active': isActive(tab.route),
        'bottom-tabs__tab--core': tab.key === 'chat',
      }"
      @click="emit('onTabClick', tab)"
    >
      <span class="bottom-tabs__icon-wrap">
        <NeonIcon :name="tab.icon" :size="26" />
      </span>
      <span class="bottom-tabs__label">{{ tab.label }}</span>
    </button>
  </nav>
</template>

<script setup lang="ts">
import NeonIcon from '@/components/common/NeonIcon.vue';
import type { MobileTab } from '@/types/nav';

const props = defineProps<{ currentRoute: string; tabs: MobileTab[] }>();
const emit = defineEmits<{ onTabClick: [tab: MobileTab] }>();

function isActive(route: string): boolean {
  if (route === '/') return props.currentRoute === '/';
  return props.currentRoute.startsWith(route);
}
</script>

<style scoped>
.bottom-tabs {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: var(--bottomtabs-h);
  display: flex;
  background: rgba(10, 10, 10, 0.92);
  backdrop-filter: blur(12px);
  border-top: 2px solid var(--amber);
  z-index: 50;
  padding-bottom: env(safe-area-inset-bottom);
}

.bottom-tabs__tab {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  color: var(--text-muted);
  transition: color 200ms;
}

.bottom-tabs__tab::before {
  content: '';
  position: absolute;
  top: 0;
  left: 25%;
  width: 50%;
  height: 2px;
  background: var(--amber);
  transform: scaleX(0);
  transition: transform 200ms;
}

.bottom-tabs__tab--active {
  color: var(--amber);
}

.bottom-tabs__tab--active::before {
  transform: scaleX(1);
}

.bottom-tabs__tab--core .bottom-tabs__icon-wrap {
  transform: translateY(-8px);
  background: var(--amber);
  border: 1px solid var(--amber);
  border-radius: 50%;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 12px var(--amber-glow);
}

.bottom-tabs__label {
  font-size: 12px;
  font-weight: 500;
}
</style>
