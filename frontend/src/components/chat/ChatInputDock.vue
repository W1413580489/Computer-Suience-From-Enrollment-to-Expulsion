<template>
  <div class="dock">
    <div class="dock__row">
      <textarea
        ref="inputEl"
        v-model="text"
        class="dock__input"
        rows="1"
        placeholder="输入你的问题，回车发送…"
        :disabled="sending"
        @keydown.enter.exact.prevent="onSend"
        @input="autoGrow"
      />
      <button
        v-if="sending"
        class="dock__btn dock__btn--stop"
        aria-label="停止生成"
        @click="emit('onStop')"
      >
        <NeonIcon name="stop" :size="18" />
      </button>
      <button
        v-else
        class="dock__btn dock__btn--send"
        aria-label="发送"
        :disabled="!text.trim()"
        @click="onSend"
      >
        <NeonIcon name="send" :size="20" />
      </button>
    </div>
    <div class="dock__meta">
      <button class="dock__meta-btn" :disabled="!canRegenerate || sending" @click="emit('onRegenerate')">
        <NeonIcon name="refresh" :size="15" /> 重新生成
      </button>
      <button class="dock__meta-btn" :disabled="sending" @click="confirmClear">
        <NeonIcon name="close" :size="15" /> 清空会话
      </button>
      <span class="dock__meta-hint">{{ keyHint }}</span>
    </div>
    <ConfirmModal
      :visible="showClearConfirm"
      title="确认清空会话"
      message="清空后所有对话记录将无法恢复，确定要继续吗？"
      confirm-text="确认清空"
      @on-confirm="doClear"
      @on-cancel="showClearConfirm = false"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import ConfirmModal from '@/components/common/ConfirmModal.vue';
import { useSettingsStore } from '@/stores/settingsStore';

defineProps<{ sending: boolean; canRegenerate: boolean }>();
const emit = defineEmits<{
  onSend: [text: string];
  onStop: [];
  onRegenerate: [];
  onClear: [];
}>();

const settings = useSettingsStore();
const text = ref('');
const inputEl = ref<HTMLTextAreaElement | null>(null);
const showClearConfirm = ref(false);

const keyHint = computed(() =>
  settings.hasKey ? `BYOK · ${settings.preset.label}` : '平台免费额度 · 配置 Key 解除限额',
);

function onSend() {
  const q = text.value.trim();
  if (!q) return;
  emit('onSend', q);
  text.value = '';
  autoGrow();
}

function autoGrow() {
  const el = inputEl.value;
  if (!el) return;
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

function confirmClear() {
  showClearConfirm.value = true;
}

function doClear() {
  showClearConfirm.value = false;
  emit('onClear');
}
</script>

<style scoped>
.dock {
  flex-shrink: 0;
  border-top: 1px solid var(--border-subtle);
  background: var(--bg-panel);
  padding: 10px 16px calc(10px + env(safe-area-inset-bottom));
}

.dock__row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  max-width: 860px;
  margin: 0 auto;
}

.dock__input {
  flex: 1;
  resize: none;
  padding: 12px 14px;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  font-size: 14px;
  font-family: var(--font-body);
  line-height: 1.5;
  outline: none;
  transition: border-color 200ms;
}

.dock__input:focus {
  border-color: var(--accent-primary);
}

.dock__input:disabled {
  opacity: 0.6;
}

.dock__btn {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 200ms, opacity 200ms;
}

.dock__btn--send {
  background: var(--accent-primary);
  color: #fff;
}

.dock__btn--send:hover:not(:disabled) {
  background: var(--accent-bright);
}

.dock__btn--send:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.dock__btn--stop {
  background: var(--danger);
  color: #fff;
}

.dock__meta {
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 860px;
  margin: 8px auto 0;
}

.dock__meta-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  min-height: 40px;
  padding: 0 12px;
  border-radius: var(--radius-md);
  font-size: 13px;
  color: var(--text-muted);
  transition: color 200ms, background 200ms;
}

.dock__meta-btn:hover:not(:disabled) {
  color: var(--accent-bright);
  background: var(--bg-panel-2);
}

.dock__meta-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.dock__meta-hint {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-muted);
  font-family: var(--font-mono);
}
</style>
