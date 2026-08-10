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

    <main v-if="nav.loaded" class="hud-main hud-fade-in">
      <template v-if="!isMobile">
        <HudSideNav :items="nav.sideMenu" :active-key="activeKey" @on-item-click="go" />
      </template>

      <section class="hud-center">
        <HudCharacterCenter
          :character-image="characterImg"
          @on-activate="goChat"
        />
        <HudSystemIndicator
          v-if="!isMobile"
          class="hud-center__sys"
          :label="nav.systemIndicator.label"
          :version="nav.systemIndicator.version"
        />
      </section>

      <aside class="hud-right">
        <HudQuickAccess :items="questAccessItems" @on-item-click="onQuickAccess" />
      </aside>
    </main>

    <main v-else class="hud-main hud-main--loading">
      <p v-if="nav.loadError" class="hud-load-error">
        配置加载失败：{{ nav.loadError }}（请确认后端服务已启动）
      </p>
      <p v-else class="hud-loading">SYSTEM LOADING…</p>
    </main>

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
import HudSideNav from '@/components/hud/HudSideNav.vue';
import HudQuickAccess from '@/components/hud/HudQuickAccess.vue';
import HudCharacterCenter from '@/components/hud/HudCharacterCenter.vue';
import HudSystemIndicator from '@/components/hud/HudSystemIndicator.vue';
import HudFooterTools from '@/components/hud/HudFooterTools.vue';
import MobileBottomTabs from '@/components/nav/MobileBottomTabs.vue';
import NavDrawer from '@/components/nav/NavDrawer.vue';
import SettingsDrawer from '@/components/settings/SettingsDrawer.vue';
import { useNavStore } from '@/stores/navStore';
import { useViewport, openExternal } from '@/composables/useViewport';
import type { MobileTab, QuickAccessItem } from '@/types/nav';
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

// 移动端底部 Tab（校园动态已按需求移除，时景 Tab 一并取消）
const mobileTabs = computed<MobileTab[]>(() => [
  { key: 'home', label: '首页', subLabel: 'HOME', icon: 'home', route: '/' },
  { key: 'guide', label: '攻略', subLabel: 'GUIDE', icon: 'guide', route: '/guides' },
  { key: 'chat', label: 'AI助手', subLabel: 'AI', icon: 'chat', route: nav.chatRoute },
  { key: 'about', label: '关于我', subLabel: 'ABOUT', icon: 'user', route: '/about' },
]);

function go(path: string) {
  router.push(path);
}

function goChat() {
  router.push(nav.chatRoute);
}

/** 快速入口 —— 把第一张卡片置为「新手任务」，其余保持飞书跳转 */
const questAccessItems = computed<QuickAccessItem[]>(() => {
  const questCard: QuickAccessItem = {
    label: '🎮 新手任务',
    desc: '新玩家账号登录 · 大地图探索 · 攻略手册',
    url: '/quest',
  };
  const resourceCard: QuickAccessItem = {
    label: '🔗 资源中心',
    desc: '常用网站与学习资源',
    url: '/resources',
  };
  const items = nav.quickAccess.map(i => ({ ...i }));
  items[0] = questCard;
  items[2] = resourceCard;
  return items;
});

function onQuickAccess(item: QuickAccessItem) {
  if (item.url.startsWith('/')) {
    router.push(item.url);
  } else {
    openExternal(item.url);
  }
}

function onDrawerNav(path: string) {
  drawerOpen.value = false;
  router.push(path);
}
</script>

<style scoped>
.hud-center__sys {
  position: absolute;
  left: 24px;
  bottom: 24px;
  width: 200px;
}

.hud-main--loading {
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
