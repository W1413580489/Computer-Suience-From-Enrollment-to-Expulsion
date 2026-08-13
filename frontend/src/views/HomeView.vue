<template>
  <div class="hud-root">
    <HudBackground />
    <HudTopBar
      :current-route="route.path"
      :is-mobile="isMobile"
      @on-avatar-click="settingsOpen = true"
      @on-notification-click="go('/changelog')"
      @on-menu-click="drawerOpen = true"
    />

    <main v-if="nav.loaded" class="home-main hud-fade-in">
      <!-- Hero：标题 + 角色主视觉 -->
      <HudCharacterCenter
        :character-image="characterImg"
        @on-go-dest="scrollToDest"
        @on-open-api="settingsOpen = true"
      />

      <!-- 目的地 -->
      <DestinationGrid />

      <!-- 智能助手 -->
      <AiInvitation />

      <!-- 数据面板 -->
      <DataPanel />

      <!-- 个人配置 -->
      <PersonalConfig />
    </main>

    <main v-else class="home-main home-main--loading">
      <p v-if="nav.loadError" class="hud-load-error">
        配置加载失败：{{ nav.loadError }}（请确认后端服务已启动）
      </p>
      <p v-else class="hud-loading">SYSTEM LOADING…</p>
    </main>

    <!-- 第四视觉：外部系统（低视觉层级） -->
    <HudFooterTools :items="nav.footerTools" @on-item-click="(i) => openExternal(i.url)" />

    <MobileBottomTabs
      v-if="isMobile"
      :current-route="route.path"
      :tabs="mobileTabs"
      @on-tab-click="(t) => go(t.route)"
    />
    <NavDrawer
      :visible="drawerOpen"
      :items="nav.sideMenu"
      :active-key="activeKey"
      @on-item-click="onDrawerNav"
      @on-close="drawerOpen = false"
    />
    <SettingsDrawer :visible="settingsOpen" @on-close="settingsOpen = false" />
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
import MobileBottomTabs from '@/components/nav/MobileBottomTabs.vue';
import NavDrawer from '@/components/nav/NavDrawer.vue';
import SettingsDrawer from '@/components/settings/SettingsDrawer.vue';
import { useNavStore } from '@/stores/navStore';
import { useViewport, openExternal } from '@/composables/useViewport';
import type { MobileTab } from '@/types/nav';
import characterImg from '@/assets/images/character.webp';

const route = useRoute();
const router = useRouter();
const nav = useNavStore();
const { isMobile } = useViewport();

const drawerOpen = ref(false);
const settingsOpen = ref(false);

onMounted(() => {
  if (!nav.loaded) nav.load();
});

const activeKey = computed(
  () => nav.sideMenu.find((i) => (i.route === '/' ? route.path === '/' : route.path.startsWith(i.route)))?.key ?? '',
);

const mobileTabs = computed<MobileTab[]>(() => [
  { key: 'home', label: '首页', subLabel: 'HOME', icon: 'home', route: '/' },
  { key: 'guide', label: '攻略', subLabel: 'GUIDE', icon: 'guide', route: '/guides' },
  { key: 'chat', label: 'AI助手', subLabel: 'AI', icon: 'chat', route: nav.chatRoute },
  { key: 'about', label: '关于我', subLabel: 'ABOUT', icon: 'user', route: '/about' },
]);

function go(path: string) {
  router.push(path);
}

function scrollToDest() {
  document.getElementById('destinations')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function onDrawerNav(path: string) {
  drawerOpen.value = false;
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

@media (max-width: 767px) {
  .hud-root {
    overflow-y: auto;
    display: block;
    padding-bottom: var(--bottomtabs-h);
  }
}
</style>
