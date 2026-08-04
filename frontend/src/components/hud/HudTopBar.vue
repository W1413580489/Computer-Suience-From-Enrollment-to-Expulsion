<template>
  <header class="topbar">
    <div class="topbar__left">
      <button v-if="showHome" class="topbar__back" aria-label="返回主页" @click="goHome">
        <NeonIcon name="home" :size="20" />
        <span class="topbar__back-text">返回主页</span>
      </button>
      <button v-if="isMobile" class="topbar__icon-btn" aria-label="菜单" @click="emit('onMenuClick')">
        <NeonIcon name="menu" :size="24" />
      </button>
      <JnuLogo :size="isMobile ? 30 : 36" />
      <div class="topbar__brand">
        <span class="topbar__brand-en">INFO SYSTEM</span>
        <span v-if="!isMobile" class="topbar__brand-cn">信科院指南系统</span>
      </div>
    </div>

    <div class="topbar__right">
      <button
        class="topbar__key-chip"
        :class="settings.hasKey ? 'topbar__key-chip--ok' : 'topbar__key-chip--warn'"
        :title="settings.hasKey ? '已配置 API Key，点击管理' : '未配置 API Key，点击前往设置'"
        @click="emit('onAvatarClick')"
      >
        <span class="topbar__key-dot" />
        {{ settings.hasKey ? 'BYOK 已连接' : '配置 API Key' }}
      </button>
      <template v-if="!isMobile">
        <span class="topbar__tag">{{ routeLabel }}</span>
        <span class="topbar__meta">JNU ID: 2026</span>
        <span class="topbar__level">LV.1</span>
      </template>
      <button class="topbar__icon-btn" aria-label="通知" @click="emit('onNotificationClick')">
        <NeonIcon name="notification" :size="22" />
      </button>
      <button class="topbar__avatar" aria-label="设置" @click="emit('onAvatarClick')">
        <NeonIcon name="user" :size="18" />
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import JnuLogo from '@/components/common/JnuLogo.vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import { useNavStore } from '@/stores/navStore';
import { useSettingsStore } from '@/stores/settingsStore';

const props = withDefaults(
  defineProps<{
    currentRoute: string;
    isMobile?: boolean;
    showHome?: boolean;
  }>(),
  { isMobile: false, showHome: false },
);

const emit = defineEmits<{
  onAvatarClick: [];
  onNotificationClick: [];
  onMenuClick: [];
}>();

const router = useRouter();
const nav = useNavStore();
const settings = useSettingsStore();

const routeLabel = computed(() => {
  if (props.currentRoute === '/') return 'HOME GUIDE';
  const item = nav.sideMenu.find((i) => i.route !== '/' && props.currentRoute.startsWith(i.route));
  if (item) return `${item.subLabel} · ${item.label}`;
  if (props.currentRoute.startsWith('/chat')) return 'AI CHAT';
  return 'INFO SYSTEM';
});

function goHome() {
  router.push('/');
}
</script>

<style scoped>
.topbar {
  height: var(--topbar-h);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border-subtle);
  position: relative;
  z-index: 10;
  gap: 12px;
}

.topbar__left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.topbar__brand {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.topbar__brand-en {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 1.5px;
  color: var(--text-primary);
}

.topbar__brand-cn {
  font-size: 11px;
  color: var(--text-muted);
}

.topbar__right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* BYOK 状态引导入口（醒目，解决「接 API 的地方不明显」） */
.topbar__key-chip {
  display: flex;
  align-items: center;
  gap: 7px;
  min-height: 36px;
  padding: 0 14px;
  border-radius: 18px;
  font-size: 13px;
  font-weight: 600;
  transition: box-shadow 200ms, transform 200ms;
}

.topbar__key-chip:hover {
  transform: translateY(-1px);
}

.topbar__key-chip--warn {
  background: linear-gradient(135deg, var(--amber) 0%, var(--amber-deep) 100%);
  color: var(--on-amber);
  box-shadow: 0 0 14px var(--amber-glow);
  animation: chip-pulse 2s infinite;
}

.topbar__key-chip--ok {
  background: rgba(78, 204, 163, 0.12);
  border: 1px solid rgba(78, 204, 163, 0.45);
  color: var(--success);
}

@keyframes chip-pulse {
  0%, 100% { box-shadow: 0 0 10px var(--amber-glow); }
  50% { box-shadow: 0 0 22px var(--amber-glow); }
}

.topbar__key-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.topbar__tag {
  font-family: var(--font-display);
  font-size: 11px;
  letter-spacing: 1px;
  color: var(--accent-yellow);
  border: 1px solid var(--border-subtle);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
}

.topbar__meta {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-secondary);
}

.topbar__level {
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 700;
  color: var(--amber);
  border: 1px solid var(--amber);
  padding: 3px 8px;
  border-radius: var(--radius-sm);
}

.topbar__back {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 44px;
  padding: 0 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--amber);
  background: rgba(255, 200, 46, 0.1);
  color: var(--amber);
  font-size: 14px;
  font-weight: 600;
  transition: background 200ms, box-shadow 200ms;
}

.topbar__back:hover {
  background: rgba(255, 200, 46, 0.2);
  box-shadow: 0 0 14px var(--amber-glow);
}

.topbar__icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  transition: color 200ms, background 200ms;
}

.topbar__icon-btn:hover {
  color: var(--amber);
  background: var(--bg-panel-2);
}

.topbar__avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-panel-3);
  border: 1px solid var(--border-glow);
  color: var(--accent-bright);
  transition: box-shadow 200ms;
}

.topbar__avatar:hover {
  box-shadow: var(--shadow-glow);
}

@media (max-width: 767px) {
  .topbar__back {
    min-height: 40px;
    padding: 0 12px;
    font-size: 13px;
  }
  .topbar__icon-btn {
    width: 44px;
    height: 44px;
  }
}
</style>
