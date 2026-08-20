<template>
  <!-- 夜间 zzz：zenless-ui 对话框。Teleport 到 body，避免父级 .hud-fade-in 的 transform 破坏 z-modal 的 position:fixed 上下文 -->
  <Teleport v-if="theme.isZzz && visible" to="body">
    <z-modal
      :model-value="visible"
      :title="title"
      :confirm-text="confirmText || '确认'"
      cancel-text="取消"
      @confirm="emit('onConfirm')"
      @cancel="emit('onCancel')"
      @close="emit('onCancel')"
    >
      <p v-if="message" class="zzz-message">{{ message }}</p>
    </z-modal>
  </Teleport>

  <!-- 日间 ak：原版样式 -->
  <Teleport v-else to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-mask" @click.self="emit('onCancel')">
        <div class="modal" role="alertdialog" :aria-label="title" @keydown.esc="emit('onCancel')">
          <h3 class="modal__title">{{ title }}</h3>
          <p v-if="message" class="modal__message">{{ message }}</p>
          <div class="modal__actions">
            <button class="modal__btn" @click="emit('onCancel')">取消</button>
            <button class="modal__btn modal__btn--danger" @click="emit('onConfirm')">{{ confirmText }}</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useThemeStore } from '@/stores/themeStore';

defineProps<{
  visible: boolean;
  title: string;
  message?: string;
  confirmText?: string;
}>();
const emit = defineEmits<{ onConfirm: []; onCancel: [] }>();
const theme = useThemeStore();
</script>

<style scoped>
.zzz-message {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
}
.modal-mask {
  position: fixed;
  inset: 0;
  background: var(--mask-strong);
  z-index: 140;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal {
  width: 340px;
  max-width: 100%;
  background: var(--bg-panel);
  border: 1px solid var(--border-glow);
  clip-path: var(--clip-md);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal__title {
  font-size: 15px;
  font-weight: 600;
}

.modal__message {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}

.modal__actions {
  display: flex;
  gap: 10px;
  margin-top: 8px;
}

.modal__btn {
  flex: 1;
  min-height: 48px;
  clip-path: var(--clip-sm);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-size: 13px;
}

.modal__btn:hover {
  border-color: var(--accent-primary);
  color: var(--accent-bright);
}

.modal__btn--danger {
  background: var(--danger);
  border-color: var(--danger);
  color: #fff;
}

.modal__btn--danger:hover {
  background: var(--danger);
  filter: brightness(1.15);
  color: #fff;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 200ms;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
