<template>
  <div class="hud-page">
    <HudBackground />
    <HudTopBar
      :current-route="route.path"
      :is-mobile="isMobile"
      :show-home="true"
      @on-avatar-click="handleAvatarClick"
      @on-notification-click="go('/changelog')"
      @on-menu-click="drawerOpen = true"
    />
    <main class="hud-page-body hud-fade-in" ref="scrollBodyEl">
      <div class="hud-page-container">
        <h1 class="page-title">{{ title }}</h1>
        <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
        <slot />
      </div>
    </main>

    <!-- 夜间 zzz：zenless-ui 回到顶部 -->
    <z-backtop v-if="theme.isZzz" :target="scrollBodyEl" :visible-height="300" :right="28" :bottom="90" />

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
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import HudBackground from '@/components/hud/HudBackground.vue';
import HudTopBar from '@/components/hud/HudTopBar.vue';
import NavDrawer from '@/components/nav/NavDrawer.vue';
import SettingsDrawer from '@/components/settings/SettingsDrawer.vue';
import { useNavStore } from '@/stores/navStore';
import { useThemeStore } from '@/stores/themeStore';
import { useUserStore } from '@/stores/userStore';
import { useViewport } from '@/composables/useViewport';

const props = withDefaults(defineProps<{ title: string; subtitle?: string; activeKey?: string }>(), {
  subtitle: '',
  activeKey: '',
});

const route = useRoute();
const router = useRouter();
const nav = useNavStore();
const theme = useThemeStore();
const userStore = useUserStore();
const { isMobile } = useViewport();

const drawerOpen = ref(false);
const settingsOpen = ref(false);
const scrollBodyEl = ref<HTMLElement | null>(null);

onMounted(() => {
  if (!nav.loaded) nav.load();
});

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

function onDrawerNav(path: string) {
  drawerOpen.value = false;
  router.push(path);
}
</script>
