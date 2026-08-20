<template>
  <!-- 夜间 zzz：zenless-ui 对话框。Teleport 到 body，避免父级 .hud-fade-in 的 transform 破坏 z-modal 的 position:fixed 上下文 -->
  <Teleport v-if="theme.isZzz && visible" to="body">
    <z-modal
      :model-value="visible"
      title="这条回答哪里有问题？"
      confirm-text="提交反馈"
      cancel-text="取消"
      @confirm="submit"
      @cancel="emit('onCancel')"
      @close="emit('onCancel')"
    >
      <div class="modal__options">
        <z-radio
          v-for="r in reasons"
          :key="r"
          v-model="selected"
          shape="button"
          :value="r"
          class="modal__zradio"
        >{{ r }}</z-radio>
      </div>
    </z-modal>
  </Teleport>

  <!-- 日间 ak：原版弹窗 -->
  <Teleport v-else to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-mask" @click.self="emit('onCancel')">
        <div class="modal" role="dialog" aria-label="点踩原因">
          <h3 class="modal__title">这条回答哪里有问题？</h3>
          <div class="modal__options">
            <button
              v-for="r in reasons"
              :key="r"
              class="modal__option"
              :class="{ 'modal__option--selected': selected === r }"
              @click="selected = r"
            >
              {{ r }}
            </button>
          </div>
          <div class="modal__actions">
            <button class="modal__btn" @click="emit('onCancel')">取消</button>
            <button class="modal__btn modal__btn--primary" @click="submit">提交反馈</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useThemeStore } from '@/stores/themeStore';

const props = defineProps<{ visible: boolean }>();
const emit = defineEmits<{ onSubmit: [reason: string]; onCancel: [] }>();
const theme = useThemeStore();

// FR-FB-02：点踩原因选项
const reasons = ['答案错误', '未命中问题', '引用缺失', '其他'];
const selected = ref(reasons[0]);

watch(
  () => props.visible,
  (v) => {
    if (v) selected.value = reasons[0];
  },
);

function submit() {
  emit('onSubmit', selected.value);
}
</script>

<style scoped>
.modal__options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin: 4px 0 8px;
}

/* zenless-ui 单选按钮铺满格子 */
.modal__zradio {
  width: 100%;
}

.modal__zradio :deep(.z-radio__label) {
  width: 100%;
}
.modal__option {
  min-height: 44px;
  padding: 0 12px;
  clip-path: var(--clip-sm);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-size: 13px;
  transition: border-color 160ms, color 160ms, background 160ms;
}
.modal__option:hover {
  border-color: var(--accent-primary);
  color: var(--text-primary);
}
.modal__option--selected {
  border-color: var(--accent-primary);
  color: var(--accent-bright);
  background: var(--accent-soft);
}
.modal-mask {
  position: fixed;
  inset: 0;
  background: var(--mask-overlay);
  z-index: 130;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal {
  width: 360px;
  max-width: 100%;
  background: var(--bg-panel);
  border: 1px solid var(--border-glow);
  clip-path: var(--clip-md);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal__title {
  font-size: 15px;
  font-weight: 600;
}

.modal__actions {
  display: flex;
  gap: 10px;
}

.modal__btn {
  flex: 1;
  min-height: 44px;
  clip-path: var(--clip-sm);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-size: 13px;
}

.modal__btn:hover {
  border-color: var(--accent-primary);
  color: var(--accent-bright);
}

.modal__btn--primary {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
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
