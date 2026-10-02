<template>
  <div class="msg" :class="`msg--${message.role}`">
    <div class="msg__bubble">
      <div class="msg__content">
        <span class="msg__text" v-if="message.role === 'user'">{{ message.content }}</span>
        <span class="msg__text md-body" v-else v-html="renderMarkdown(message.content)"></span>
        <ChatCursor v-if="message.streaming" />
        <p v-if="message.error" class="msg__error">
          {{ message.error }}
          <button v-if="showKeyFixHint" class="msg__error-link" @click="emit('onOpenSettings')">
            前往设置 →
          </button>
        </p>
      </div>

      <div v-if="message.citations?.length" class="msg__citations">
        <!-- 夜间 zzz：zenless-ui 折叠面板 -->
        <z-collapse v-if="theme.isZzz" v-model="citationsExpanded" class="msg__zcite">
          <z-collapse-item :name="'cite'">
            <template #title>
              <NeonIcon name="doc" :size="14" />
              <span class="msg__citations-label">参考来源（{{ message.citations.length }}）</span>
            </template>
            <div class="msg__citations-list">
              <ChatCitationCard v-for="c in message.citations" :key="c.id" :citation="c" />
            </div>
          </z-collapse-item>
        </z-collapse>
        <!-- 日间 ak：原版折叠 -->
        <template v-else>
          <button
            class="msg__citations-toggle"
            :aria-expanded="citationsExpanded"
            @click="citationsExpanded = !citationsExpanded"
          >
            <NeonIcon name="doc" :size="14" />
            <span class="msg__citations-label">参考来源（{{ message.citations.length }}）</span>
            <NeonIcon
              name="arrow-right"
              :size="14"
              class="msg__citations-arrow"
              :class="{ 'msg__citations-arrow--open': citationsExpanded }"
            />
          </button>
          <div v-show="citationsExpanded" class="msg__citations-list">
            <ChatCitationCard v-for="c in message.citations" :key="c.id" :citation="c" />
          </div>
        </template>
      </div>

      <div v-if="message.role === 'assistant' && !message.streaming && (message.content || message.error)" class="msg__actions">
        <!-- 夜间 zzz：zenless-ui 按钮 -->
        <template v-if="theme.isZzz">
          <z-button
            size="mini"
            :type="message.feedback === 'up' ? 'primary' : 'default'"
            :disabled="message.feedback != null"
            @click="emit('onFeedback', 'up')"
          >
            <NeonIcon name="thumb-up" :size="16" />
          </z-button>
          <z-button
            size="mini"
            :type="message.feedback === 'down' ? 'fire' : 'default'"
            :disabled="message.feedback != null"
            @click="emit('onFeedback', 'down')"
          >
            <NeonIcon name="thumb-down" :size="16" />
          </z-button>
        </template>
        <!-- 日间 ak：原版按钮 -->
        <template v-else>
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
        </template>
        <span v-if="message.feedback" class="msg__feedback-done">
          {{ message.feedback === 'up' ? '已点赞' : '已反馈，感谢' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import ChatCursor from '@/components/chat/ChatCursor.vue';
import ChatCitationCard from '@/components/chat/ChatCitationCard.vue';
import { renderMarkdown } from '@/composables/useMarkdown';
import { useThemeStore } from '@/stores/themeStore';
import type { ChatMessage } from '@/types/nav';

const props = defineProps<{ message: ChatMessage }>();
const emit = defineEmits<{
  onFeedback: [value: 'up' | 'down'];
  onOpenSettings: [];
}>();

const theme = useThemeStore();

// 参考来源默认折叠，点击展开（避免来源列表占满屏幕）
const citationsExpanded = ref(false);

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
  border-top: 1px dashed var(--border-subtle);
  padding-top: 8px;
}

.msg__citations-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 4px 6px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 12px;
  cursor: pointer;
  transition: color 200ms;
}

.msg__citations-toggle:hover {
  color: var(--accent-primary);
}

.msg__citations-label {
  flex: 1;
  text-align: left;
}

.msg__citations-arrow {
  transition: transform 200ms ease;
  transform: rotate(90deg);
}

.msg__citations-arrow--open {
  transform: rotate(-90deg);
}

.msg__citations-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 6px;
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

/* markdown 渲染样式（和 TeachView 保持一致） */
.md-body { white-space: normal; }
.md-body > :first-child { margin-top: 0; }
.md-body > :last-child { margin-bottom: 0; }
.md-body p { margin: 6px 0; }
.md-body ul, .md-body ol { margin: 6px 0; padding-left: 20px; }
.md-body li { margin: 3px 0; }
.md-body h1, .md-body h2, .md-body h3, .md-body h4 { margin: 10px 0 6px; }
.md-body h1 { font-size: 18px; }
.md-body h2 { font-size: 16px; }
.md-body h3, .md-body h4 { font-size: 15px; }
.md-body blockquote { margin: 6px 0; padding: 4px 10px; border-left: 3px solid var(--border-subtle); color: var(--text-muted); }
.md-body code:not(.hljs) {
  background: rgba(128, 128, 128, 0.18); border-radius: 4px; padding: 1px 5px;
  font-family: ui-monospace, Consolas, monospace; font-size: 12.5px;
}
.md-body pre {
  background: #14161a; color: #e6e6e6; border-radius: 8px; padding: 10px 12px;
  overflow-x: auto; margin: 8px 0; font-size: 12.5px; line-height: 1.55;
}
.md-body pre code { font-family: ui-monospace, Consolas, monospace; background: none; padding: 0; white-space: pre; }
.md-body table { border-collapse: collapse; margin: 8px 0; font-size: 12.5px; }
.md-body th, .md-body td { border: 1px solid var(--border-subtle); padding: 4px 8px; text-align: left; }
.md-body th { background: rgba(128, 128, 128, 0.12); }
.md-body a { color: var(--text-link); text-decoration: underline; }
.md-body a:hover { color: var(--amber); }

/* zenless-ui 引用折叠面板 */
.msg__zcite {
  width: 100%;
}

.msg__zcite :deep(.z-collapse-item__title) {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
}

@media (max-width: 767px) {
  .msg__bubble {
    max-width: 92%;
  }
}
</style>
