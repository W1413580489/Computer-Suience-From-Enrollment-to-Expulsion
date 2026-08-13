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
        <span v-if="!isMobile" class="topbar__brand-cn">信息学院指南系统</span>
      </div>
    </div>

    <!-- 中间导航（仅首页桌面端） -->
    <nav v-if="isHome && !isMobile" class="topbar__nav">
      <button
        v-for="item in navItems"
        :key="item.key"
        class="topbar__nav-item"
        :class="{ 'topbar__nav-item--active': item.route === '/' ? currentRoute === '/' : currentRoute.startsWith(item.route) }"
        @click="goNav(item.route)"
      >
        {{ item.label }}
      </button>
    </nav>

    <div class="topbar__right">
      <span v-if="!isMobile && !isHome" class="topbar__tag">{{ routeLabel }}</span>
      <button class="topbar__icon-btn" aria-label="通知" @click="emit('onNotificationClick')">
        <NeonIcon name="notification" :size="22" />
      </button>
      <button class="topbar__avatar" aria-label="用户" @click="emit('onAvatarClick')">
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

const isHome = computed(() => props.currentRoute === '/');

const navItems = [
  { key: 'home', label: '首页', route: '/' },
  { key: 'guide', label: '攻略', route: '/guides' },
  { key: 'database', label: '资源', route: '/resources' },
];

const routeLabel = computed(() => {
  if (props.currentRoute === '/') return 'HOME';
  const item = nav.sideMenu.find((i) => i.route !== '/' && props.currentRoute.startsWith(i.route));
  if (item) return `${item.subLabel} · ${item.label}`;
  if (props.currentRoute.startsWith('/chat')) return 'AI CHAT';
  return 'INFO SYSTEM';
});

function goHome() {
  router.push('/');
}

function goNav(route: string) {
  router.push(route);
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
  background: rgba(10, 10, 10, 0.92);
  backdrop-filter: blur(12px);
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
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 2px;
  color: var(--amber);
  text-transform: uppercase;
}

.topbar__brand-cn {
  font-size: 11px;
  color: var(--text-muted);
}

/* 中间导航 — 简洁文字 */
.topbar__nav {
  display: flex;
  gap: 28px;
  align-items: center;
}

.topbar__nav-item {
  position: relative;
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--text-secondary);
  text-transform: uppercase;
  padding: 6px 0;
  transition: color 200ms;
}

.topbar__nav-item:hover {
  color: var(--amber);
}

.topbar__nav-item--active {
  color: var(--amber);
}

.topbar__nav-item--active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--amber);
}

.topbar__right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.topbar__tag {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 1px;
  color: var(--amber);
  border: 1px solid var(--border-subtle);
  padding: 4px 10px;
  clip-path: var(--clip-sm);
}

.topbar__back {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 44px;
  padding: 0 16px;
  clip-path: var(--clip-sm);
  border: 1px solid var(--amber);
  background: var(--amber-soft);
  color: var(--amber);
  font-size: 14px;
  font-weight: 700;
  transition: background 200ms, box-shadow 200ms;
}

.topbar__back:hover {
  background: var(--amber-mid);
  box-shadow: 0 0 14px var(--amber-glow);
}

.topbar__icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  clip-path: var(--clip-sm);
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
  clip-path: var(--clip-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-panel-3);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  transition: color 200ms, border-color 200ms;
}

.topbar__avatar:hover {
  color: var(--amber);
  border-color: var(--amber);
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
