<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="visible" class="drawer-mask" @click.self="emit('onClose')">
        <div class="drawer" role="dialog" aria-label="导航菜单">
          <div class="drawer__handle" />
          <button
            v-for="item in items"
            :key="item.key"
            class="drawer__item"
            :class="{ 'drawer__item--active': activeKey === item.key }"
            @click="emit('onItemClick', item.route)"
          >
            <span class="drawer__number">{{ item.number }}</span>
            <NeonIcon :name="item.icon" :size="20" />
            <span class="drawer__text">
              <span class="drawer__label">{{ item.label }}</span>
              <span class="drawer__sublabel">{{ item.subLabel }}</span>
            </span>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import NeonIcon from '@/components/common/NeonIcon.vue';
import type { SideMenuItem } from '@/types/nav';

defineProps<{ visible: boolean; items: SideMenuItem[]; activeKey: string }>();
const emit = defineEmits<{ onItemClick: [route: string]; onClose: [] }>();
</script>

<style scoped>
.drawer-mask {
  position: fixed;
  inset: 0;
  background: var(--mask-overlay);
  z-index: 100;
  display: flex;
  align-items: flex-end;
}

.drawer {
  width: 100%;
  background: var(--bg-panel);
  border-top: 2px solid var(--amber);
  clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%);
  padding: 12px 16px calc(16px + env(safe-area-inset-bottom));
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.drawer__handle {
  width: 40px;
  height: 4px;
  border-radius: 2px;
  background: var(--border-subtle);
  margin: 0 auto 10px;
}

.drawer__item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 14px;
  clip-path: var(--clip-sm);
  color: var(--text-secondary);
  text-align: left;
  min-height: 60px;
}

.drawer__item:active {
  background: var(--bg-panel-2);
}

.drawer__item--active {
  color: var(--amber);
  background: var(--bg-panel-2);
}

.drawer__number {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
}

.drawer__text {
  display: flex;
  flex-direction: column;
}

.drawer__label {
  font-size: 17px;
  font-weight: 500;
}

.drawer__sublabel {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 2px;
  color: var(--text-muted);
}

.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 300ms;
}
.drawer-enter-active .drawer,
.drawer-leave-active .drawer {
  transition: transform 300ms cubic-bezier(0.32, 0.72, 0, 1);
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}
.drawer-enter-from .drawer,
.drawer-leave-to .drawer {
  transform: translateY(100%);
}
</style>
