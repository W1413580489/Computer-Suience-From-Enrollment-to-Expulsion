<template>
  <div ref="listEl" class="msg-list">
    <div v-if="!messages.length" class="msg-list__welcome">
      <p class="msg-list__welcome-title">你好！我是信科智能助手</p>
      <p class="msg-list__welcome-sub">基于《信科院-从入学到被开除》校园指南回答你的问题</p>
      <div v-if="hotQuestions.length" class="msg-list__hot">
        <p class="msg-list__hot-title">高频问题</p>
        <div class="msg-list__hot-grid">
          <!-- 夜间 zzz：zenless-ui 按钮卡片 -->
          <z-button
            v-for="item in hotQuestions"
            v-if="theme.isZzz"
            :key="item.q"
            class="msg-list__zhot"
            @click="emit('onAskHot', item.q)"
          >
            <span class="msg-list__hot-label">{{ item.label }}</span>
            <span class="msg-list__hot-q">{{ item.q }}</span>
          </z-button>
          <!-- 日间 ak：原版卡片 -->
          <button
            v-for="item in hotQuestions"
            v-if="!theme.isZzz"
            :key="item.q"
            class="msg-list__hot-card"
            @click="emit('onAskHot', item.q)"
          >
            <span class="msg-list__hot-label">{{ item.label }}</span>
            <span class="msg-list__hot-q">{{ item.q }}</span>
          </button>
        </div>
      </div>
    </div>

    <ChatMessage
      v-for="m in messages"
      :key="m.id"
      :message="m"
      @on-feedback="(v) => emit('onFeedback', m, v)"
      @on-open-settings="emit('onOpenSettings')"
    />
  </div>

  <!-- 夜间 zzz：zenless-ui 回到顶部（消息列表滚动区） -->
  <z-backtop
    v-if="theme.isZzz"
    :target="listEl"
    :visible-height="300"
    :right="20"
    :bottom="150"
  />
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from 'vue';
import ChatMessage from '@/components/chat/ChatMessage.vue';
import { useThemeStore } from '@/stores/themeStore';
import type { ChatMessage as ChatMessageType } from '@/types/nav';

const props = defineProps<{
  messages: ChatMessageType[];
  hotQuestions: { q: string; label: string }[];
}>();

const emit = defineEmits<{
  onFeedback: [msg: ChatMessageType, value: 'up' | 'down'];
  onAskHot: [q: string];
  onOpenSettings: [];
}>();

const theme = useThemeStore();
const listEl = ref<HTMLElement | null>(null);

watch(
  () => props.messages.map((m) => m.content.length).join(','),
  async () => {
    await nextTick();
    listEl.value?.scrollTo({ top: listEl.value.scrollHeight, behavior: 'smooth' });
  },
);
</script>

<style scoped>
.msg-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.msg-list__welcome {
  margin: auto;
  max-width: 640px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 24px 0;
}

.msg-list__welcome-title {
  font-family: var(--font-display);
  font-size: 20px;
  letter-spacing: 1px;
  color: var(--accent-bright);
}

.msg-list__welcome-sub {
  font-size: 13px;
  color: var(--text-secondary);
}

.msg-list__hot {
  margin-top: 16px;
}

.msg-list__hot-title {
  font-size: 12px;
  letter-spacing: 2px;
  color: var(--text-muted);
  margin-bottom: 10px;
}

.msg-list__hot-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.msg-list__hot-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 14px 16px;
  min-height: 64px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-sm);
  text-align: left;
  transition: border-color 200ms, box-shadow 200ms;
}

.msg-list__hot-card:hover {
  border-color: var(--accent-primary);
  box-shadow: var(--shadow-glow);
}

.msg-list__hot-label {
  font-size: 11px;
  color: var(--warning);
}

.msg-list__hot-q {
  font-size: 13px;
  color: var(--text-primary);
}

/* zenless-ui 高频问题按钮卡片 */
.msg-list__zhot {
  display: flex !important;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  height: auto;
  min-height: 64px;
  padding: 14px 16px;
  line-height: 1.4;
  text-align: left;
  white-space: normal;
}

@media (max-width: 767px) {
  .msg-list {
    padding: 14px 12px;
  }
  /* 手机端隐藏推荐问题，保障页面简洁 */
  .msg-list__hot {
    display: none;
  }
}
</style>
