<template>
  <header class="topbar">
    <div class="topbar__left">
      <!-- 返回主页：夜间 zzz 用 zenless-ui 按钮 / 日间 ak 原版 -->
      <z-button v-if="showHome && theme.isZzz" size="small" class="topbar__zback" @click="goHome">
        <NeonIcon name="home" :size="18" />
        <span class="topbar__back-text">返回主页</span>
      </z-button>
      <button v-if="showHome && !theme.isZzz" class="topbar__back" aria-label="返回主页" @click="goHome">
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
        :class="{ 'topbar__nav-item--active': item.route && (item.route === '/' ? currentRoute === '/' : currentRoute.startsWith(item.route)) }"
        @click="goNav(item)"
      >
        {{ item.label }}
      </button>
    </nav>

    <div class="topbar__right">
      <!-- 夜间 zzz：zenless-ui 标签 / 日间 ak：原版标签 -->
      <z-tag v-if="!isMobile && !isHome && theme.isZzz" size="mini" class="topbar__ztag">{{ routeLabel }}</z-tag>
      <span v-else-if="!isMobile && !isHome" class="topbar__tag">{{ routeLabel }}</span>
      <!-- 日夜间模式切换（绝区零 ↔ 明日方舟），紧邻「更新日志」铃铛 -->
      <button
        class="theme-toggle"
        :aria-label="theme.isAk ? '切换到夜间模式' : '切换到日间模式'"
        :title="theme.isAk ? '切换到夜间模式 · 绝区零' : '切换到日间模式 · 明日方舟'"
        @click="theme.toggle()"
      >
        <span class="theme-toggle__track">
          <span class="theme-toggle__knob" :class="{ 'theme-toggle__knob--ak': theme.isAk }"></span>
        </span>
        <span class="theme-toggle__label">{{ theme.isAk ? '日' : '夜' }}</span>
      </button>
      <!-- 更新日志：夜间 zzz 用 zenless-ui 徽标+气泡 / 日间 ak 原版 -->
      <z-tooltip v-if="theme.isZzz" content="更新日志" placement="bottom">
        <z-badge is-dot type="fire" class="topbar__zbadge">
          <button class="topbar__icon-btn" aria-label="更新日志" @click="emit('onNotificationClick')">
            <NeonIcon name="notification" :size="22" />
          </button>
        </z-badge>
      </z-tooltip>
      <button v-else class="topbar__icon-btn" aria-label="更新日志" @click="emit('onNotificationClick')">
        <NeonIcon name="notification" :size="22" />
      </button>

      <!-- 用户信息（登录后）：点击弹出身份工牌 -->
      <button v-if="userStore.isLoggedIn" class="topbar__user" @click="showBadge = true">
        <img v-if="userStore.user?.avatar" :src="userStore.user.avatar" alt="头像" class="topbar__user-avatar" />
        <NeonIcon v-else name="user" :size="18" />
        <span class="topbar__user-name">{{ userStore.user?.nickname }}</span>
        <span class="topbar__user-badge">{{ userStore.gradeLabel }} · {{ userStore.majorLabel }}</span>
      </button>
      <IdentityBadge :visible="showBadge" mode="view" @close="showBadge = false" />

      <button v-if="!userStore.isLoggedIn" class="topbar__avatar" aria-label="用户" @click="emit('onAvatarClick')">
        <NeonIcon name="user" :size="18" />
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import JnuLogo from '@/components/common/JnuLogo.vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import IdentityBadge from '@/components/login/IdentityBadge.vue';
import { useNavStore } from '@/stores/navStore';
import { useThemeStore } from '@/stores/themeStore';
import { useUserStore } from '@/stores/userStore';

const theme = useThemeStore();
const userStore = useUserStore();

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

/* 身份工牌弹窗 */
const showBadge = ref(false);

const isHome = computed(() => props.currentRoute === '/');

interface NavItem {
  key: string;
  label: string;
  route?: string;
  url?: string;
}

const navItems: NavItem[] = [
  { key: 'home', label: '首页', route: '/' },
  { key: 'guide', label: '起点', url: 'https://tralis2671.feishu.cn/wiki/VvKVwsHo2iIIC4ko0PmcKs4lnKd' },
  { key: 'zzz', label: 'zzz', url: 'https://zzz.mihoyo.com/' },
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

function goNav(item: NavItem) {
  if (item.url) {
    window.open(item.url, '_blank', 'noopener');
    return;
  }
  if (item.route) router.push(item.route);
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
  background: var(--surface-blur);
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
  font-size: 18px;
  font-weight: 500;
  letter-spacing: 2px;
  color: var(--amber);
  text-transform: uppercase;
}

.topbar__brand-cn {
  font-size: 12px;
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
  font-size: 14px;
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

/* 日夜间模式切换 — 绝区零(夜) ↔ 明日方舟(日) */
.theme-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 32px;
  padding: 0 10px 0 8px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-panel);
  color: var(--text-secondary);
  clip-path: var(--clip-sm);
  cursor: pointer;
  transition: border-color 200ms, color 200ms, box-shadow 200ms;
}
.theme-toggle:hover {
  border-color: var(--amber);
  color: var(--amber);
  box-shadow: 0 0 14px var(--amber-glow);
}
.theme-toggle__track {
  position: relative;
  width: 34px;
  height: 18px;
  background: var(--bg-panel-3);
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-sm);
  transition: background 400ms, border-color 400ms;
}
.theme-toggle__knob {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 12px;
  height: 12px;
  background: var(--amber);
  clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%);
  transition: transform 400ms cubic-bezier(0.4, 0, 0.2, 1), background 400ms;
}
.theme-toggle__knob--ak {
  transform: translateX(16px);
}
.theme-toggle__label {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--amber);
  min-width: 12px;
  text-align: center;
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

/* zenless-ui 徽标 / 标签对齐 */
.topbar__zbadge {
  display: inline-flex;
  line-height: 1;
  flex-shrink: 0;
}

.topbar__ztag {
  flex-shrink: 0;
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

/* zenless-ui 返回主页按钮 */
.topbar__zback {
  display: flex !important;
  align-items: center;
  gap: 8px;
  height: 40px;
  padding: 0 14px !important;
  flex-shrink: 0;
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

/* 用户信息标签 */
.topbar__user {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-panel);
  clip-path: var(--clip-sm);
  cursor: pointer;
  transition: border-color 200ms, background 200ms;
}

.topbar__user:hover {
  border-color: var(--amber);
  background: var(--bg-panel-2);
}

.topbar__user-avatar {
  width: 24px;
  height: 24px;
  object-fit: cover;
  clip-path: var(--clip-sm);
}

.topbar__user-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}

.topbar__user-badge {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--amber);
  padding: 2px 6px;
  background: var(--amber-soft);
  clip-path: var(--clip-sm);
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
