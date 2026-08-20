<template>
  <div class="hud-page">
    <HudBackground />
    <HudTopBar
      :current-route="route.path"
      :is-mobile="isMobile"
      :show-home="true"
      @on-avatar-click="settingsOpen = true"
      @on-notification-click="go('/changelog')"
      @on-menu-click="drawerOpen = true"
    />

    <!-- BYOK 引导横幅：未配置 Key 时醒目提示（点击直接打开设置） -->
    <button v-if="!settings.hasKey && !bannerDismissed" class="byok-banner" @click="settingsOpen = true">
      <NeonIcon name="settings" :size="18" class="byok-banner__icon" />
      <span class="byok-banner__text">
        <strong>配置自己的 API Key</strong>
        <span>解除每日 30 次限额，30 秒完成 →</span>
      </span>
      <span
        class="byok-banner__close"
        role="button"
        aria-label="不再提示"
        @click.stop="dismissBanner"
      >
        <NeonIcon name="close" :size="14" />
      </span>
    </button>

    <ChatMessageList
      :messages="chat.messages"
      :hot-questions="hotQuestions"
      @on-feedback="onFeedback"
      @on-ask-hot="(q) => chat.ask(q)"
      @on-open-settings="settingsOpen = true"
    />

    <p class="chat-disclaimer">内容由学长学姐共创，非官方，政策以学校最新通知为准</p>

    <ChatInputDock
      :sending="chat.sending"
      :can-regenerate="canRegenerate"
      @on-send="(q) => chat.ask(q)"
      @on-stop="chat.stop()"
      @on-regenerate="chat.regenerate()"
      @on-clear="chat.clear()"
    />

    <MobileBottomTabs
      v-if="isMobile"
      :current-route="route.path"
      :tabs="mobileTabs"
      @on-tab-click="(t) => go(t.route)"
    />
    <NavDrawer
      :visible="drawerOpen"
      :items="nav.sideMenu"
      active-key=""
      @on-item-click="onDrawerNav"
      @on-close="drawerOpen = false"
    />
    <SettingsDrawer :visible="settingsOpen" @on-close="settingsOpen = false" />
    <FeedbackReasonModal
      :visible="feedbackModalOpen"
      @on-submit="onFeedbackReason"
      @on-cancel="feedbackModalOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import HudBackground from '@/components/hud/HudBackground.vue';
import HudTopBar from '@/components/hud/HudTopBar.vue';
import ChatMessageList from '@/components/chat/ChatMessageList.vue';
import ChatInputDock from '@/components/chat/ChatInputDock.vue';
import FeedbackReasonModal from '@/components/chat/FeedbackReasonModal.vue';
import MobileBottomTabs from '@/components/nav/MobileBottomTabs.vue';
import NavDrawer from '@/components/nav/NavDrawer.vue';
import SettingsDrawer from '@/components/settings/SettingsDrawer.vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import { fetchHotQuestions } from '@/api/client';
import { useChatStore } from '@/stores/chatStore';
import { useNavStore } from '@/stores/navStore';
import { useSettingsStore } from '@/stores/settingsStore';
import { useViewport } from '@/composables/useViewport';
import type { ChatMessage, MobileTab } from '@/types/nav';

const BANNER_LS_KEY = 'xkz_byok_banner_dismissed';

const route = useRoute();
const router = useRouter();
const chat = useChatStore();
const nav = useNavStore();
const settings = useSettingsStore();
const { isMobile } = useViewport();

const settingsOpen = ref(false);
const drawerOpen = ref(false);
const feedbackModalOpen = ref(false);
const pendingDownMsg = ref<ChatMessage | null>(null);
const hotQuestions = ref<{ q: string; label: string }[]>([]);
const bannerDismissed = ref(localStorage.getItem(BANNER_LS_KEY) === '1');

onMounted(async () => {
  if (!nav.loaded) nav.load();
  hotQuestions.value = await fetchHotQuestions();
});

const mobileTabs = computed<MobileTab[]>(() => [
  { key: 'home', label: '首页', subLabel: 'HOME', icon: 'home', route: '/' },
  { key: 'guide', label: '攻略', subLabel: 'GUIDE', icon: 'guide', route: '/guides' },
  { key: 'chat', label: 'AI助手', subLabel: 'AI', icon: 'chat', route: '/chat' },
  { key: 'about', label: '关于我', subLabel: 'ABOUT', icon: 'user', route: '/about' },
]);

const canRegenerate = computed(() => chat.messages.some((m) => m.role === 'user'));

function dismissBanner() {
  bannerDismissed.value = true;
  localStorage.setItem(BANNER_LS_KEY, '1');
}

function go(path: string) {
  router.push(path);
}

function onDrawerNav(path: string) {
  drawerOpen.value = false;
  router.push(path);
}

function onFeedback(msg: ChatMessage, value: 'up' | 'down') {
  if (value === 'up') {
    chat.feedback(msg, 'up');
  } else {
    // FR-FB-02：点踩弹出原因选择
    pendingDownMsg.value = msg;
    feedbackModalOpen.value = true;
  }
}

function onFeedbackReason(reason: string) {
  if (pendingDownMsg.value) {
    chat.feedback(pendingDownMsg.value, 'down', reason);
  }
  feedbackModalOpen.value = false;
  pendingDownMsg.value = null;
}
</script>

<style scoped>
.byok-banner {
  position: relative;
  z-index: 1;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 12px auto 0;
  width: min(860px, calc(100% - 32px));
  min-height: 56px;
  padding: 10px 16px;
  clip-path: var(--clip-md);
  border: 1px solid var(--amber);
  background: linear-gradient(135deg, var(--amber-soft) 0%, var(--amber-deep-soft) 100%);
  color: var(--text-primary);
  text-align: left;
  transition: box-shadow 200ms, transform 200ms;
}

.byok-banner:hover {
  box-shadow: 0 0 18px var(--amber-glow);
  transform: translateY(-1px);
}

.byok-banner__icon {
  color: var(--amber);
  flex-shrink: 0;
}

.byok-banner__text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 13px;
  color: var(--text-secondary);
}

.byok-banner__text strong {
  font-size: 14px;
  color: var(--amber);
}

.byok-banner__close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  clip-path: var(--clip-sm);
  color: var(--text-muted);
  flex-shrink: 0;
}

.byok-banner__close:hover {
  color: var(--text-primary);
  background: var(--surface-glass);
}

.chat-disclaimer {
  flex-shrink: 0;
  text-align: center;
  font-size: 11px;
  color: var(--text-muted);
  padding: 6px 16px 0;
  position: relative;
  z-index: 1;
}

@media (max-width: 767px) {
  .hud-page {
    padding-bottom: var(--bottomtabs-h);
  }
  /* 横幅紧凑化，释放内容区空间 */
  .byok-banner {
    margin: 8px auto 0;
    width: calc(100% - 24px);
    min-height: 48px;
    padding: 8px 12px;
    gap: 8px;
  }
  .byok-banner__text {
    font-size: 12px;
  }
  .byok-banner__text strong {
    font-size: 13px;
  }
  .byok-banner__close {
    width: 28px;
    height: 28px;
  }
  .chat-disclaimer {
    font-size: 10px;
    padding: 4px 12px 0;
  }
}
</style>
