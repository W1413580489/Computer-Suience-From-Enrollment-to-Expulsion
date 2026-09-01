<template>
  <div class="hud-root">
    <HudBackground />
    <HudTopBar
      :current-route="route.path"
      :is-mobile="isMobile"
      @on-avatar-click="handleAvatarClick"
      @on-notification-click="go('/changelog')"
      @on-menu-click="drawerOpen = true"
    />

    <main v-if="nav.loaded" ref="homeMainEl" class="home-main hud-fade-in">
      <!-- 硬件/其他类 黄色提示条 -->
      <div v-if="userStore.isLoggedIn && !userStore.isSoftware" class="home-warning">
        <span class="home-warning__icon">!</span>
        <span>你选择的专业（{{ userStore.majorLabel }}）内容正在开发中，敬请期待</span>
      </div>

      <!-- Hero：标题 + 角色主视觉 -->
      <HudCharacterCenter
        :character-image="characterImg"
        :grade-subtitle="gradeSubtitle"
        @on-go-dest="scrollToDest"
        @on-go-roadmap="goRoadmap"
      />

      <!-- 目的地 -->
      <DestinationGrid />

      <!-- 智能助手 -->
      <AiInvitation />

      <!-- 数据面板 -->
      <DataPanel />

      <!-- 个人配置 -->
      <PersonalConfig @on-open-hub="hubOpen = true" />

      <!-- 成就系统 -->
      <AchievementSection />
    </main>

    <main v-else class="home-main home-main--loading">
      <p v-if="nav.loadError" class="hud-load-error">
        配置加载失败：{{ nav.loadError }}（请确认后端服务已启动）
      </p>
      <p v-else class="hud-loading">SYSTEM LOADING…</p>
    </main>

    <!-- 第四视觉：外部系统（低视觉层级） -->
    <HudFooterTools :items="nav.footerTools" @on-item-click="(i) => openExternal(i.url)" />

    <NavDrawer
      :visible="drawerOpen"
      :items="nav.sideMenu"
      :active-key="activeKey"
      @on-item-click="onDrawerNav"
      @on-close="drawerOpen = false"
    />
    <SettingsDrawer :visible="settingsOpen" @on-close="settingsOpen = false" />
<SettingsHub :visible="hubOpen" @on-close="hubOpen = false" @on-open-api="hubOpen = false; settingsOpen = true" />

    <!-- 夜间 zzz：zenless-ui 回到顶部（首页主滚动区） -->
    <z-backtop
      v-if="theme.isZzz && nav.loaded"
      :target="homeMainEl"
      :visible-height="400"
      :right="24"
      :bottom="96"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import HudBackground from '@/components/hud/HudBackground.vue';
import HudTopBar from '@/components/hud/HudTopBar.vue';
import HudCharacterCenter from '@/components/hud/HudCharacterCenter.vue';
import HudFooterTools from '@/components/hud/HudFooterTools.vue';
import DestinationGrid from '@/components/home/DestinationGrid.vue';
import AiInvitation from '@/components/home/AiInvitation.vue';
import DataPanel from '@/components/home/DataPanel.vue';
import PersonalConfig from '@/components/home/PersonalConfig.vue';
import AchievementSection from '@/components/home/AchievementSection.vue';
import NavDrawer from '@/components/nav/NavDrawer.vue';
import SettingsDrawer from '@/components/settings/SettingsDrawer.vue';
import SettingsHub from '@/components/settings/SettingsHub.vue';
import { useNavStore } from '@/stores/navStore';
import { useThemeStore } from '@/stores/themeStore';
import { useUserStore } from '@/stores/userStore';
import { useAchievementStore } from '@/stores/achievementStore';
import { useViewport, openExternal } from '@/composables/useViewport';
import { heroSubtitles } from '@/data/gradeContent';
import characterImg from '@/assets/images/character.webp';

const route = useRoute();
const router = useRouter();
const nav = useNavStore();
const theme = useThemeStore();
const userStore = useUserStore();
const { isMobile } = useViewport();

const gradeSubtitle = computed(() => {
  if (!userStore.user) return '';
  return heroSubtitles[userStore.user.grade] ?? '';
});

const drawerOpen = ref(false);
const settingsOpen = ref(false);
const hubOpen = ref(false);
const homeMainEl = ref<HTMLElement | null>(null);

onMounted(() => {
  if (!nav.loaded) nav.load();
});

const activeKey = computed(
  () => nav.sideMenu.find((i) => (i.route === '/' ? route.path === '/' : route.path.startsWith(i.route)))?.key ?? '',
);

function go(path: string) {
  router.push(path);
}

// 点击用户头像：未登录跳转登录页，已登录打开设置面板
function handleAvatarClick() {
  if (userStore.isLoggedIn) {
    settingsOpen.value = true;
  } else {
    router.push('/login');
  }
}

function scrollToDest() {
  document.getElementById('destinations')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 点击"路线导航"按钮：跳转成长路线图
function goRoadmap() {
  useAchievementStore().unlock('where_wander');
  router.push('/roadmap');
}

function onDrawerNav(path: string) {
  drawerOpen.value = false;
  // 特殊项：API 配置 → 打开设置抽屉
  if (path === '__settings__') {
    settingsOpen.value = true;
    return;
  }
  // 成就：首次点击"关于我"
  if (path === '/about') {
    useAchievementStore().unlock('what_is_this');
  }
  // 成就：首次从导航菜单点击路线图
  if (path === '/roadmap') {
    useAchievementStore().unlock('homepage_has_entry');
  }
  router.push(path);
}
</script>

<style scoped>
.home-main {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
}

.home-main--loading {
  align-items: center;
  justify-content: center;
}

.hud-loading {
  font-family: var(--font-display);
  letter-spacing: 4px;
  color: var(--text-muted);
  animation: hud-fade-in 300ms ease-out both;
}

.hud-load-error {
  color: var(--danger);
  font-size: 14px;
  padding: 0 24px;
  text-align: center;
}

/* 警告条 */
.home-warning {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px 20px;
  background: #f5a623;
  color: #1a1a1a;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.5px;
  flex-shrink: 0;
  position: relative;
  z-index: 5;
}

.home-warning__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #1a1a1a;
  color: #f5a623;
  font-size: 13px;
  font-weight: 900;
  flex-shrink: 0;
}

@media (max-width: 767px) {
  .hud-root {
    overflow-y: auto;
    display: block;
  }
}
</style>
