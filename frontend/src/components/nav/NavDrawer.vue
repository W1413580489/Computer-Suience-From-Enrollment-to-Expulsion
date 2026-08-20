<template>
  <!-- 夜间 zzz：zenless-ui 抽屉 + 菜单。Teleport 到 body，避免父级 .hud-fade-in 的 transform 破坏 z-modal 的 position:fixed 上下文 -->
  <Teleport v-if="theme.isZzz" to="body">
    <z-modal
      :model-value="visible"
      mode="drawer"
      title="导航菜单"
      :show-footer="false"
      @close="emit('onClose')"
    >
      <z-menu :model-value="activeKey" @change="onZzzNav">
        <z-menu-item v-for="item in items" :key="item.key" :name="item.key">
          <span class="zzz-item">
            <span class="zzz-item__num">{{ item.number }}</span>
            <span class="zzz-item__label">{{ item.label }}</span>
            <span class="zzz-item__sub">{{ item.subLabel }}</span>
          </span>
        </z-menu-item>
      </z-menu>
    </z-modal>
  </Teleport>

  <!-- 日间 ak：原版底部抽屉 -->
  <Teleport v-else to="body">
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
import { useThemeStore } from '@/stores/themeStore';
import type { SideMenuItem } from '@/types/nav';

const props = defineProps<{ visible: boolean; items: SideMenuItem[]; activeKey: string }>();
const emit = defineEmits<{ onItemClick: [route: string]; onClose: [] }>();
const theme = useThemeStore();

/** z-menu change 事件：按 key 找到对应路由并跳转 */
function onZzzNav(key: string | number) {
  const item = props.items.find((i) => i.key === key);
  if (item) emit('onItemClick', item.route);
}
</script>

<style scoped>
/* zzz 菜单项排版 */
.zzz-item {
  display: flex;
  align-items: baseline;
  gap: 10px;
  width: 100%;
}
.zzz-item__num {
  font-family: var(--font-mono);
  font-size: 11px;
  opacity: 0.55;
}
.zzz-item__label {
  font-size: 15px;
}
.zzz-item__sub {
  margin-left: auto;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 2px;
  opacity: 0.45;
}
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
