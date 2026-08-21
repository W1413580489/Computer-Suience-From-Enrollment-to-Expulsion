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

  <!-- 日间 ak：桌面端居中弹窗 / 手机端底部抽屉 -->
  <Teleport v-else to="body">
    <!-- 桌面端居中弹窗 -->
    <Transition name="ak-fade" v-if="visible && !isMobile">
      <div class="ak-mask" @click.self="emit('onClose')">
        <div class="ak-panel" role="dialog" aria-label="导航菜单">
          <div class="ak-panel__header">
            <span class="ak-panel__title">导航菜单</span>
            <span class="ak-panel__en">NAVIGATION</span>
            <button class="ak-panel__close" aria-label="关闭" @click="emit('onClose')">
              <NeonIcon name="close" :size="16" />
            </button>
          </div>
          <div class="ak-panel__body">
            <button
              v-for="item in items"
              :key="item.key"
              class="ak-panel__item"
              :class="{ 'ak-panel__item--active': activeKey === item.key, 'ak-panel__item--external': item.route.startsWith('http') }"
              @click="onAkNav(item.route)"
            >
              <span class="ak-panel__number">{{ item.number }}</span>
              <NeonIcon :name="item.icon" :size="24" />
              <span class="ak-panel__text">
                <span class="ak-panel__label">{{ item.label }}</span>
                <span class="ak-panel__sublabel">{{ item.subLabel }}</span>
              </span>
              <NeonIcon :name="item.route.startsWith('http') ? 'external' : 'arrow-right'" :size="16" class="ak-panel__arrow" />
            </button>
          </div>
          <div class="ak-panel__footer">
            <span class="ak-panel__footer-text">INFO SYSTEM · NAVIGATION</span>
          </div>
        </div>
      </div>
    </Transition>
    <!-- 手机端底部抽屉 -->
    <Transition name="drawer">
      <div v-if="visible && isMobile" class="drawer-mask" @click.self="emit('onClose')">
        <div class="drawer" role="dialog" aria-label="导航菜单">
          <div class="drawer__handle" />
          <button
            v-for="item in items"
            :key="item.key"
            class="drawer__item"
            :class="{ 'drawer__item--active': activeKey === item.key, 'drawer__item--external': item.route.startsWith('http') }"
            @click="onAkNav(item.route)"
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
import { useViewport, openExternal } from '@/composables/useViewport';
import type { SideMenuItem } from '@/types/nav';

const props = defineProps<{ visible: boolean; items: SideMenuItem[]; activeKey: string }>();
const emit = defineEmits<{ onItemClick: [route: string]; onClose: [] }>();
const theme = useThemeStore();
const { isMobile } = useViewport();

/** z-menu change 事件：外链直接打开，内链交由父组件路由跳转 */
function onZzzNav(key: string | number) {
  const item = props.items.find((i) => i.key === key);
  if (!item) return;
  if (item.route.startsWith('http')) {
    openExternal(item.route);
    emit('onClose');
  } else {
    emit('onItemClick', item.route);
  }
}

/** AK 模式点击：外链直接打开，内链交由父组件路由跳转 */
function onAkNav(route: string) {
  if (route.startsWith('http')) {
    openExternal(route);
    emit('onClose');
  } else {
    emit('onItemClick', route);
  }
}
</script>

<style scoped>
/* zzz 菜单项排版 */
.zzz-item {
  display: flex;
  align-items: baseline;
  gap: 12px;
  width: 100%;
}
.zzz-item__num {
  font-family: var(--font-mono);
  font-size: 13px;
  opacity: 0.55;
}
.zzz-item__label {
  font-size: 17px;
  font-weight: 500;
}
.zzz-item__sub {
  margin-left: auto;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 2px;
  opacity: 0.45;
}

/* ZZZ 抽屉：桌面端更宽，手机端全宽 */
:deep(.z-modal__wrap) {
  height: 100dvh;
  max-height: 100dvh;
}

:deep(.z-modal__body) {
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

:deep(.z-modal__body .z-scrollbar__view) {
  padding: 16px 20px;
}

/* ============================================
   AK 桌面端居中弹窗
   ============================================ */
.ak-mask {
  position: fixed;
  inset: 0;
  background: var(--mask-overlay);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ak-panel {
  width: 540px;
  max-width: calc(100vw - 48px);
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-left: 4px solid var(--amber);
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.25);
}

.ak-panel__header {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 32px 36px 20px;
  border-bottom: 1px solid var(--border-subtle);
}

.ak-panel__title {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  letter-spacing: 3px;
  color: var(--amber);
  text-transform: uppercase;
}

.ak-panel__en {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 4px;
  color: var(--text-muted);
}

.ak-panel__close {
  position: absolute;
  top: 24px;
  right: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-sm);
  transition: color 200ms, border-color 200ms, background 200ms;
}

.ak-panel__close:hover {
  color: var(--amber);
  border-color: var(--amber);
  background: var(--amber-soft);
}

.ak-panel__body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ak-panel__item {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 18px 20px;
  clip-path: var(--clip-sm);
  color: var(--text-secondary);
  text-align: left;
  transition: color 200ms, background 200ms;
}

.ak-panel__item:hover {
  color: var(--amber);
  background: var(--amber-soft);
}

.ak-panel__item--active {
  color: var(--amber);
  background: var(--amber-soft);
  border-left: 3px solid var(--amber);
}

.ak-panel__item--external .ak-panel__sublabel::after {
  content: ' · 外链';
  opacity: 0.6;
}

.ak-panel__number {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--text-muted);
  width: 28px;
  text-align: right;
  flex-shrink: 0;
}

.ak-panel__text {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 2px;
}

.ak-panel__label {
  font-size: 19px;
  font-weight: 600;
}

.ak-panel__sublabel {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 2px;
  color: var(--text-muted);
}

.ak-panel__arrow {
  color: var(--amber);
  opacity: 0;
  transform: translateX(-4px);
  transition: opacity 200ms, transform 200ms;
}

.ak-panel__item:hover .ak-panel__arrow {
  opacity: 1;
  transform: translateX(0);
}

.ak-panel__item--active .ak-panel__arrow {
  opacity: 1;
  transform: translateX(0);
}

.ak-panel__footer {
  padding: 16px 36px;
  border-top: 1px solid var(--border-subtle);
  text-align: center;
}

.ak-panel__footer-text {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 4px;
  color: var(--text-muted);
  text-transform: uppercase;
}

/* AK 桌面弹窗动画 */
.ak-fade-enter-active,
.ak-fade-leave-active {
  transition: opacity 200ms;
}
.ak-fade-enter-active .ak-panel,
.ak-fade-leave-active .ak-panel {
  transition: transform 200ms cubic-bezier(0.32, 0.72, 0, 1), opacity 200ms;
}
.ak-fade-enter-from,
.ak-fade-leave-to {
  opacity: 0;
}
.ak-fade-enter-from .ak-panel,
.ak-fade-leave-to .ak-panel {
  transform: scale(0.95);
  opacity: 0;
}

/* ============================================
   AK 手机端底部抽屉
   ============================================ */
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
  max-height: 70vh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
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

/* ============================================
   响应式
   ============================================ */
@media (min-width: 768px) {
  /* ZZZ 桌面端抽屉加宽 */
  :deep(.z-modal__wrap) {
    width: 480px !important;
    max-width: 480px !important;
  }

  :deep(.z-modal__body .z-scrollbar__view) {
    padding: 24px 32px;
  }

  /* 放大 z-menu 菜单项 */
  :deep(.z-menu-item) {
    padding: 16px 20px !important;
    min-height: 56px;
  }
}

@media (max-width: 767px) {
  /* ZZZ 手机端抽屉全宽 */
  :deep(.z-modal__wrap) {
    width: 100% !important;
    max-width: 100% !important;
  }

  :deep(.z-modal__body .z-scrollbar__view) {
    padding: 12px 16px;
  }
}
</style>
