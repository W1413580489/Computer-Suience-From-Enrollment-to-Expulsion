<template>
  <Teleport to="body">
    <TransitionGroup
      name="ach-toast"
      tag="div"
      class="ach-toasts"
      :style="{ '--bg-softer': theme.isZzz && zzzBg ? zzzBg : undefined }"
    >
      <div
        v-for="t in active"
        :key="t.uid"
        class="ach-toast"
        :class="`ach-toast--${theme.isZzz ? 'zzz' : 'ak'}`"
        @click="dismiss(t.uid)"
      >
        <span class="ach-toast__ribbon">ACHIEVEMENT UNLOCKED</span>
        <div class="ach-toast__row">
          <span class="ach-toast__badge" :class="`ach-toast__badge--${t.badgeColor}`">{{ t.badge }}</span>
          <div class="ach-toast__text">
            <span class="ach-toast__label">成就解锁</span>
            <span class="ach-toast__title">{{ t.title }}</span>
          </div>
        </div>
        <span class="ach-toast__bar" />
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watchEffect } from 'vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import { useAchievementStore } from '@/stores/achievementStore';
import { useThemeStore } from '@/stores/themeStore';
import type { AchievementDef } from '@/data/achievements';

interface ToastItem extends AchievementDef {
  uid: number;
}

const achStore = useAchievementStore();
const theme = useThemeStore();

// zzz 夜间背景色（从 CSS 变量读取）
const zzzBg = ref<string>('');
const active = ref<ToastItem[]>([]);
let uidSeq = 0;
const timers = new Map<number, ReturnType<typeof setTimeout>>();

const DURATION = 4000;

watchEffect(() => {
  while (achStore.toastQueue.length > 0) {
    const def = achStore.shiftToast();
    if (!def) break;
    const item: ToastItem = { ...def, uid: ++uidSeq };
    active.value.push(item);
    timers.set(
      item.uid,
      setTimeout(() => dismiss(item.uid), DURATION),
    );
  }
});

function dismiss(uid: number) {
  const t = timers.get(uid);
  if (t) {
    clearTimeout(t);
    timers.delete(uid);
  }
  active.value = active.value.filter((x) => x.uid !== uid);
}

function readCssVars() {
  const cs = getComputedStyle(document.documentElement);
  zzzBg.value = cs.getPropertyValue('--bg-panel').trim() || `rgba(20, 24, 31, .96)`;
}

onMounted(() => {
  readCssVars();
  window.addEventListener('resize', readCssVars);
});

onUnmounted(() => {
  window.removeEventListener('resize', readCssVars);
  timers.forEach((t) => clearTimeout(t));
});
</script>

<style scoped>
.ach-toasts {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: none;
  max-width: min(340px, calc(100vw - 32px));
}

.ach-toast {
  pointer-events: auto;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  padding: 14px 18px 16px;
  border-left: 3px solid var(--amber);
  background: var(--bg-panel);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
  clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
}

/* 手机端：全宽居中，减小内边距，加显式关闭区 */
@media (max-width: 767px) {
  .ach-toasts {
    top: 12px;
    right: 10px;
    left: 10px;
    max-width: none;
    width: auto;
  }
  .ach-toast {
    padding: 12px 14px;
    min-height: 56px; /* 足够大的点击区域 */
  }
  .ach-toast__ribbon {
    font-size: 8px;
    margin-bottom: 4px;
  }
  .ach-toast__badge {
    padding: 3px 8px;
    font-size: 10px;
  }
  .ach-toast__title {
    font-size: 14px;
  }
  .ach-toast__label {
    font-size: 9px;
  }
}

/* AK 日间：浅色玻璃卡 + 发丝描边，对齐设计体系 */
.ach-toast--ak {
  background: var(--card-surface);
  border: 1px solid var(--card-border);
  border-left: 3px solid var(--amber-deep);
  box-shadow: var(--shadow-card);
}

.ach-toast__ribbon {
  display: block;
  font-family: var(--font-mono);
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.25em;
  color: var(--amber);
  text-transform: uppercase;
  margin-bottom: 8px;
}

.ach-toast__row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ach-toast__badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  clip-path: polygon(6px 0, 100% 0, 100% calc(100% - 6px), calc(100% - 6px) 100%, 0 100%, 0 6px);
  flex-shrink: 0;
}
.ach-toast__badge--yellow { background: var(--amber); color: var(--on-amber); }
.ach-toast__badge--cyan { background: var(--neon-cyan); color: #FFFFFF; }
.ach-toast__badge--magenta { background: var(--neon-magenta); color: #FFFFFF; }
.ach-toast__badge--dark { background: var(--bg-panel-3); color: var(--text-secondary); border: 1px solid var(--border-subtle); }

.ach-toast__text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.ach-toast__label {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.2em;
  color: var(--text-muted);
  text-transform: uppercase;
}

.ach-toast__title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  margin-top: 1px;
}

.ach-toast__bar {
  position: absolute;
  left: 0;
  bottom: 0;
  height: 2px;
  background: var(--amber);
  animation: ach-toast-var 4s linear forwards;
}

@keyframes ach-toast-var {
  from { width: 100%; }
  to { width: 0; }
}

/* 进出场动画 */
.ach-toast-enter-active,
.ach-toast-leave-active {
  transition: all 0.4s ease;
}
.ach-toast-enter-from {
  opacity: 0;
  transform: translateX(40px);
}
.ach-toast-leave-to {
  opacity: 0;
  transform: translateX(40px);
}
</style>