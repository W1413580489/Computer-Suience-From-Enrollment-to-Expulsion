<template>
  <div class="dock">
    <!-- 夜间 zzz：回复中流光进度条（zenless-ui） -->
    <div v-if="theme.isZzz && fakePercent > 0" class="dock__progress">
      <span class="dock__progress-label">{{ fakePercent >= 100 ? '已完成' : '思考中' }}</span>
      <z-progress :percent="fakePercent" />
    </div>
    <div class="dock__row">
      <!-- 夜间 zzz：zenless-ui 输入框 / 日间 ak：原版 textarea -->
      <z-input
        v-if="theme.isZzz"
        v-model="text"
        type="textarea"
        :auto-size="true"
        :rows="1"
        :maxlength="2000"
        class="dock__zinput"
        placeholder="输入你的问题，回车发送…"
        :disabled="sending"
        @keydown="onKeydown"
      />
      <textarea
        v-else
        ref="inputEl"
        v-model="text"
        class="dock__input"
        rows="1"
        placeholder="输入你的问题，回车发送…"
        :disabled="sending"
        @keydown="onKeydown"
        @input="autoGrow"
      />
      <!-- 夜间 zzz：zenless-ui 发送/停止按钮 -->
      <template v-if="theme.isZzz">
        <z-button
          v-if="sending"
          type="fire"
          size="large"
          class="dock__zbtn dock__zbtn--stop"
          aria-label="停止生成"
          @click="emit('onStop')"
        >
          <NeonIcon name="stop" :size="18" />
        </z-button>
        <z-button
          v-else
          type="primary"
          size="large"
          class="dock__zbtn dock__zbtn--send"
          aria-label="发送"
          :disabled="!text.trim()"
          @click="onSend"
        >
          <NeonIcon name="send" :size="20" />
        </z-button>
      </template>
      <!-- 日间 ak：原版按钮 -->
      <template v-else>
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
      </template>
    </div>
    <div class="dock__meta">
      <!-- 夜间 zzz：zenless-ui 下拉菜单 + 回车发送开关 -->
      <template v-if="theme.isZzz">
        <z-dropdown trigger="click" @command="onMetaCommand">
          <z-button size="small">更多操作</z-button>
          <template #dropdown>
            <z-dropdown-item command="regenerate" :disabled="!canRegenerate || sending">
              重新生成
            </z-dropdown-item>
            <z-dropdown-item command="clear" :disabled="sending">清空会话</z-dropdown-item>
          </template>
        </z-dropdown>
        <z-checkbox v-model="enterSend" class="dock__zcheck">Enter 发送</z-checkbox>
      </template>
      <!-- 日间 ak：原版按钮 -->
      <template v-else>
        <button class="dock__meta-btn" :disabled="!canRegenerate || sending" @click="emit('onRegenerate')">
          <NeonIcon name="refresh" :size="15" /> 重新生成
        </button>
        <button class="dock__meta-btn" :disabled="sending" @click="confirmClear">
          <NeonIcon name="close" :size="15" /> 清空会话
        </button>
      </template>
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
import { computed, onBeforeUnmount, ref, watch } from 'vue';
import { useMessage } from 'zenless-ui';
import NeonIcon from '@/components/common/NeonIcon.vue';
import ConfirmModal from '@/components/common/ConfirmModal.vue';
import { useSettingsStore } from '@/stores/settingsStore';
import { useThemeStore } from '@/stores/themeStore';

const props = defineProps<{ sending: boolean; canRegenerate: boolean }>();
const emit = defineEmits<{
  onSend: [text: string];
  onStop: [];
  onRegenerate: [];
  onClear: [];
}>();

const settings = useSettingsStore();
const theme = useThemeStore();
const message = useMessage();
const text = ref('');
const inputEl = ref<HTMLTextAreaElement | null>(null);
const showClearConfirm = ref(false);
/* Enter 直接发送 / Ctrl+Enter 发送（夜间 zzz 显示开关） */
const enterSend = ref(true);

/* 夜间流光进度：sending 时模拟缓慢推进，结束时冲刺到 100% 再隐藏 */
const fakePercent = ref(0);
let fakeTimer: ReturnType<typeof setInterval> | null = null;

function startFake() {
  stopFake();
  fakePercent.value = 8;
  fakeTimer = setInterval(() => {
    // 越接近 92 越慢，制造"模型在思考"的观感
    fakePercent.value = Math.min(92, fakePercent.value + Math.max(0.4, (92 - fakePercent.value) * 0.03));
  }, 200);
}

function stopFake() {
  if (fakeTimer) {
    clearInterval(fakeTimer);
    fakeTimer = null;
  }
}

watch(
  () => props.sending,
  (sending) => {
    if (sending) {
      startFake();
    } else if (fakePercent.value > 0) {
      stopFake();
      fakePercent.value = 100;
      setTimeout(() => {
        fakePercent.value = 0;
      }, 500);
    }
  },
);

onBeforeUnmount(stopFake);

const keyHint = computed(() =>
  settings.hasKey ? `BYOK · ${settings.preset.label}` : '平台免费额度 · 配置 Key 解除限额',
);

function onSend() {
  const q = text.value.trim();
  if (!q) return;
  if (props.sending && theme.isZzz) {
    message.warning('回复生成中，请稍候…');
    return;
  }
  emit('onSend', q);
  text.value = '';
  if (!theme.isZzz) autoGrow(); // z-input autoSize 自动收缩，原版需手动
}

/* 回车发送策略：enterSend 开=无修饰键 Enter 发送；关=仅 Ctrl+Enter 发送。Shift+Enter 始终换行 */
function onKeydown(e: KeyboardEvent) {
  if (e.key !== 'Enter') return;
  const hasModifier = e.ctrlKey || e.metaKey || e.altKey;
  const shouldSend = enterSend.value ? !hasModifier && !e.shiftKey : e.ctrlKey || e.metaKey;
  if (!shouldSend) return;
  e.preventDefault();
  onSend();
}

/* 夜间 zzz：下拉菜单命令分发 */
function onMetaCommand(cmd: string | number) {
  if (cmd === 'regenerate') {
    emit('onRegenerate');
  } else if (cmd === 'clear') {
    confirmClear();
  }
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
  if (theme.isZzz) message.success('会话已清空');
}
</script>

<style scoped>
.dock {
  flex-shrink: 0;
  border-top: 2px solid var(--amber);
  background: var(--surface-blur);
  backdrop-filter: blur(12px);
  padding: 10px 16px calc(10px + env(safe-area-inset-bottom));
}

/* 回复中进度条 */
.dock__progress {
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 860px;
  margin: 0 auto 8px;
}

.dock__progress-label {
  flex-shrink: 0;
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--text-muted);
  letter-spacing: 2px;
}

.dock__progress :deep(.z-progress) {
  flex: 1;
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
  clip-path: var(--clip-sm);
  color: var(--text-primary);
  font-size: 14px;
  font-family: var(--font-body);
  line-height: 1.5;
  outline: none;
  transition: border-color 200ms;
}

.dock__input:focus {
  border-color: var(--amber);
}

.dock__input:disabled {
  opacity: 0.6;
}

/* zenless-ui 输入框：铺满剩余宽度 */
.dock__zinput {
  flex: 1;
  min-width: 0;
}

.dock__zinput :deep(.z-textarea__inner) {
  resize: none;
  min-height: 44px;
  max-height: 120px;
  padding: 12px 14px;
  font-size: 14px;
  font-family: var(--font-body);
  line-height: 1.5;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  outline: none;
  transition: border-color 200ms;
}

.dock__zinput :deep(.z-textarea__inner:focus) {
  border-color: var(--amber);
}

.dock__zinput :deep(.z-textarea__inner:disabled) {
  opacity: 0.6;
}

/* zenless-ui 发送/停止按钮：方形 */
.dock__zbtn {
  width: 52px !important;
  height: 52px !important;
  min-width: auto !important;
  padding: 0 !important;
  display: flex !important;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

@media (max-width: 767px) {
  .dock__zbtn {
    width: 44px !important;
    height: 44px !important;
  }
}

.dock__btn {
  width: 52px;
  height: 52px;
  clip-path: var(--clip-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 200ms, opacity 200ms;
}

.dock__btn--send {
  background: var(--amber);
  color: var(--on-amber);
}

.dock__btn--send:hover:not(:disabled) {
  background: var(--amber);
  filter: brightness(1.15);
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
  clip-path: var(--clip-sm);
  font-size: 13px;
  color: var(--text-muted);
  transition: color 200ms, background 200ms;
}

.dock__meta-btn:hover:not(:disabled) {
  color: var(--amber);
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

/* zenless-ui 回车发送开关 */
.dock__zcheck {
  flex-shrink: 0;
}

/* 修复 z-dropdown：库默认向下打开（bottom:-8px + translateY(100%)），
   在底部输入坞里会被裁切。改为向上打开 + 提升 z-index + 加宽 */
.dock__meta :deep(.z-dropdown) {
  position: static;
}

.dock__meta :deep(.z-dropdown__content) {
  bottom: auto !important;
  top: 0;
  right: auto;
  left: 0;
  width: auto;
  min-width: 140px;
  transform: translateY(calc(-100% - 4px)) scaleY(0);
  transform-origin: bottom;
  z-index: 100;
}

.dock__meta :deep(.z-dropdown.is-visible .z-dropdown__content) {
  transform: translateY(calc(-100% - 4px)) scaleY(1);
}

@media (max-width: 767px) {
  .dock {
    padding: 8px 12px calc(8px + env(safe-area-inset-bottom));
  }
  .dock__row {
    gap: 8px;
  }
  .dock__input {
    padding: 10px 12px;
    font-size: 16px; /* iOS 防 zoom */
  }
  .dock__btn {
    width: 44px;
    height: 44px;
  }
  .dock__meta {
    gap: 8px;
    margin-top: 6px;
  }
  .dock__meta-btn {
    min-height: 36px;
    padding: 0 10px;
    font-size: 12px;
  }
  /* 手机端隐藏冗长的 Key 提示，避免拥挤 */
  .dock__meta-hint {
    display: none;
  }
}
</style>
