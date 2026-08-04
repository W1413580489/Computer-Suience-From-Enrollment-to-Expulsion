<template>
  <Teleport to="body">
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

const props = defineProps<{ visible: boolean }>();
const emit = defineEmits<{ onSubmit: [reason: string]; onCancel: [] }>();

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
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(4, 10, 24, 0.7);
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
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal__title {
  font-size: 15px;
  font-weight: 600;
}

.modal__options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.modal__option {
  padding: 14px;
  min-height: 52px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 13px;
  transition: border-color 200ms, color 200ms, background 200ms;
}

.modal__option:hover {
  border-color: var(--accent-primary);
  color: var(--accent-bright);
}

.modal__option--selected {
  border-color: var(--accent-primary);
  background: var(--bg-panel-3);
  color: var(--accent-bright);
}

.modal__actions {
  display: flex;
  gap: 10px;
}

.modal__btn {
  flex: 1;
  min-height: 48px;
  border-radius: var(--radius-md);
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

.modal__btn--primary:hover {
  background: var(--accent-bright);
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
