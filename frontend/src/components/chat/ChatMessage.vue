<template>
  <div class="msg" :class="`msg--${message.role}`">
    <div class="msg__bubble">
      <div class="msg__content">
        <span class="msg__text">{{ message.content }}</span>
        <ChatCursor v-if="message.streaming" />
        <p v-if="message.error" class="msg__error">
          {{ message.error }}
          <button v-if="showKeyFixHint" class="msg__error-link" @click="emit('onOpenSettings')">
            前往设置 →
          </button>
        </p>
      </div>

      <div v-if="message.citations?.length" class="msg__citations">
        <ChatCitationCard v-for="c in message.citations" :key="c.id" :citation="c" />
      </div>

      <div v-if="message.role === 'assistant' && !message.streaming && (message.content || message.error)" class="msg__actions">
        <button
          class="msg__action"
          :class="{ 'msg__action--up': message.feedback === 'up' }"
          aria-label="点赞"
          :disabled="message.feedback != null"
          @click="emit('onFeedback', 'up')"
        >
          <NeonIcon name="thumb-up" :size="18" />
        </button>
        <button
          class="msg__action"
          :class="{ 'msg__action--down': message.feedback === 'down' }"
          aria-label="点踩"
          :disabled="message.feedback != null"
          @click="emit('onFeedback', 'down')"
        >
          <NeonIcon name="thumb-down" :size="18" />
        </button>
        <span v-if="message.feedback" class="msg__feedback-done">
          {{ message.feedback === 'up' ? '已点赞' : '已反馈，感谢' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import ChatCursor from '@/components/chat/ChatCursor.vue';
import ChatCitationCard from '@/components/chat/ChatCitationCard.vue';
import type { ChatMessage } from '@/types/nav';

const props = defineProps<{ message: ChatMessage }>();
const emit = defineEmits<{
  onFeedback: [value: 'up' | 'down'];
  onOpenSettings: [];
}>();

// Key 失效类错误提示去设置页（FR-BY-08）
const showKeyFixHint = computed(
  () => !!props.message.error && /Key|key|设置页/.test(props.message.error),
);
</script>

<style scoped>
.msg {
  display: flex;
  width: 100%;
}

.msg--user {
  justify-content: flex-end;
}

.msg--assistant {
  justify-content: flex-start;
}

.msg__bubble {
  max-width: 82%;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 14px;
  clip-path: var(--clip-md);
  line-height: 1.7;
}

.msg--user .msg__bubble {
  background: var(--bg-panel-3);
  border: 1px solid var(--amber);
  border-top: 3px solid var(--amber);
}

.msg--assistant .msg__bubble {
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-left: 3px solid var(--neon-cyan);
}

.msg__content {
  font-size: 14px;
  color: var(--text-primary);
}

.msg__text {
  white-space: pre-wrap;
  word-break: break-word;
}

.msg__error {
  color: var(--danger);
  font-size: 13px;
}

.msg__error-link {
  color: var(--text-link);
  font-size: 13px;
  text-decoration: underline;
}

.msg__citations {
  display: flex;
  flex-direction: column;
  gap: 6px;
  border-top: 1px dashed var(--border-subtle);
  padding-top: 8px;
}

.msg__actions {
  display: flex;
  align-items: center;
  gap: 6px;
  border-top: 1px dashed var(--border-subtle);
  padding-top: 8px;
}

.msg__action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 40px;
  clip-path: var(--clip-sm);
  border: 1px solid var(--border-subtle);
  background: var(--bg-panel-2);
  color: var(--text-muted);
  transition: color 200ms, background 200ms, border-color 200ms;
}

.msg__action:hover:not(:disabled) {
  border-color: var(--amber);
  color: var(--amber);
}

.msg__action:disabled {
  cursor: default;
}

.msg__action--up {
  color: var(--success);
}

.msg__action--down {
  color: var(--danger);
}

.msg__feedback-done {
  font-size: 11px;
  color: var(--text-muted);
}

@media (max-width: 767px) {
  .msg__bubble {
    max-width: 92%;
  }
}
</style>
