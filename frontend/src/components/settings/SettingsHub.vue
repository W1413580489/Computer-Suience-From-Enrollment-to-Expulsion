<template>
  <!-- 夜间 zzz：zenless-ui 居中弹窗 -->
  <Teleport v-if="theme.isZzz && visible" to="body">
    <z-modal
      :model-value="visible"
      title="设置中心 · SETTINGS HUB"
      :show-footer="false"
      @close="emit('onClose')"
    >
      <div class="hub">
        <!-- 顶部斜杠标题 -->
        <div class="hub__head">
          <span class="hub__head-slash">//</span>
          <span class="hub__head-title">{{ view === 'menu' ? 'SETTINGS' : 'BACKGROUND' }}</span>
          <span class="hub__head-line" />
        </div>

        <!-- 卡片选择视图 -->
        <template v-if="view === 'menu'">
          <div class="hub__grid">
            <button class="hub__card" @click="onCardClick('api')">
              <span class="hub__card-num">01</span>
              <div class="hub__card-body">
                <span class="hub__card-title">API 设置</span>
                <span class="hub__card-en">API CONFIG</span>
                <span class="hub__card-desc">配置 API Key 和模型参数</span>
              </div>
              <span class="hub__card-cta">进入 →</span>
            </button>

            <button class="hub__card" @click="onCardClick('bg')">
              <span class="hub__card-num">02</span>
              <div class="hub__card-body">
                <span class="hub__card-title">背景设置</span>
                <span class="hub__card-en">BACKGROUND</span>
                <span class="hub__card-desc">导入背景图片，自定义页面氛围</span>
              </div>
              <span class="hub__card-cta">进入 →</span>
            </button>

            <button class="hub__card hub__card--locked" disabled>
              <span class="hub__card-num">03</span>
              <div class="hub__card-body">
                <span class="hub__card-title">即将开放</span>
                <span class="hub__card-en">COMING SOON</span>
                <span class="hub__card-desc">功能开发中，敬请期待</span>
              </div>
              <span class="hub__card-cta hub__card-cta--locked">🔒</span>
            </button>
          </div>
        </template>

        <!-- 背景设置视图 -->
        <template v-else-if="view === 'bg'">
          <div class="hub__bg">
            <!-- 预览区 -->
            <div
              class="hub__preview"
              :class="{ 'hub__preview--empty': !displayUrl, 'hub__preview--draggable': !!displayUrl }"
              @mousedown="onDragStart"
              @touchstart.passive="onTouchStart"
            >
              <div
                v-if="displayUrl"
                class="hub__preview-img"
                :style="{ backgroundImage: `url(${displayUrl})`, backgroundPosition: `${bg.bgX.value}% ${bg.bgY.value}%` }"
              />
              <div v-else class="hub__preview-placeholder">
                <span class="hub__preview-tag">CHOOSE IMAGE</span>
                <span class="hub__preview-cn">请选择一张图片</span>
              </div>
              <!-- 待确认徽章 -->
              <span v-if="bg.pendingUrl.value" class="hub__pending-badge">PENDING</span>
              <span v-if="displayUrl" class="hub__drag-hint">拖动调整位置</span>
            </div>

            <!-- 操作区 -->
            <div class="hub__actions">
              <!-- 无待确认：选择图片 + 重置位置 -->
              <label v-if="!bg.pendingUrl.value" class="hub__btn hub__btn--primary">
                选择图片
                <input
                  ref="fileInput"
                  type="file"
                  accept="image/*"
                  class="hub__file-input"
                  @change="onFileChange"
                />
              </label>
              <button
                v-if="!bg.pendingUrl.value && bg.dataUrl.value"
                class="hub__btn hub__btn--ghost"
                @click="onResetPos"
              >重置位置</button>
              <button
                v-if="!bg.pendingUrl.value && bg.dataUrl.value"
                class="hub__btn hub__btn--danger"
                @click="onRemoveBg"
              >移除背景</button>

              <!-- 待确认：应用 / 取消 -->
              <button
                v-if="bg.pendingUrl.value"
                class="hub__btn hub__btn--primary"
                @click="onApply"
              >应用此背景</button>
              <button
                v-if="bg.pendingUrl.value"
                class="hub__btn hub__btn--ghost"
                @click="onCancel"
              >取消</button>
            </div>

            <p v-if="bg.error.value" class="hub__error">{{ bg.error.value }}</p>

            <p class="hub__note">图片仅保存在本浏览器，不会上传到服务器。</p>

            <button class="hub__back" @click="onBack">
              <span class="hub__back-arrow">←</span> 返回设置菜单
            </button>
          </div>
        </template>
      </div>
    </z-modal>
  </Teleport>

  <!-- 日间 ak：自定义弹窗 -->
  <Teleport v-else to="body">
    <Transition name="hub">
      <div v-if="visible" class="hub-mask" @click.self="emit('onClose')">
        <div class="hub hub--ak" role="dialog" aria-modal="true" aria-label="设置中心">
          <header class="hub__header">
            <h2 class="hub__title">设置中心 · SETTINGS HUB</h2>
            <button class="hub__close" aria-label="关闭" @click="emit('onClose')">
              <NeonIcon name="close" :size="18" />
            </button>
          </header>

          <div class="hub__body">
            <!-- 卡片选择视图 -->
            <template v-if="view === 'menu'">
              <div class="hub__grid">
                <button class="hub__card" @click="onCardClick('api')">
                  <span class="hub__card-num">01</span>
                  <div class="hub__card-body">
                    <span class="hub__card-title">API 设置</span>
                    <span class="hub__card-en">API CONFIG</span>
                    <span class="hub__card-desc">配置 API Key 和模型参数</span>
                  </div>
                  <span class="hub__card-cta">进入 →</span>
                </button>

                <button class="hub__card" @click="onCardClick('bg')">
                  <span class="hub__card-num">02</span>
                  <div class="hub__card-body">
                    <span class="hub__card-title">背景设置</span>
                    <span class="hub__card-en">BACKGROUND</span>
                    <span class="hub__card-desc">导入背景图片，自定义页面氛围</span>
                  </div>
                  <span class="hub__card-cta">进入 →</span>
                </button>

                <button class="hub__card hub__card--locked" disabled>
                  <span class="hub__card-num">03</span>
                  <div class="hub__card-body">
                    <span class="hub__card-title">即将开放</span>
                    <span class="hub__card-en">COMING SOON</span>
                    <span class="hub__card-desc">功能开发中，敬请期待</span>
                  </div>
                  <span class="hub__card-cta hub__card-cta--locked">🔒</span>
                </button>
              </div>
            </template>

            <!-- 背景设置视图 -->
            <template v-else-if="view === 'bg'">
              <div class="hub__bg">
                <div
                  class="hub__preview"
                  :class="{ 'hub__preview--empty': !displayUrl, 'hub__preview--draggable': !!displayUrl }"
                  @mousedown="onDragStart"
                  @touchstart.passive="onTouchStart"
                >
                  <div
                    v-if="displayUrl"
                    class="hub__preview-img"
                    :style="{ backgroundImage: `url(${displayUrl})`, backgroundPosition: `${bg.bgX.value}% ${bg.bgY.value}%` }"
                  />
                  <div v-else class="hub__preview-placeholder">
                    <span class="hub__preview-tag">CHOOSE IMAGE</span>
                    <span class="hub__preview-cn">请选择一张图片</span>
                  </div>
                  <span v-if="bg.pendingUrl.value" class="hub__pending-badge">PENDING</span>
                  <span v-if="displayUrl" class="hub__drag-hint">拖动调整位置</span>
                </div>

                <div class="hub__actions">
                  <label v-if="!bg.pendingUrl.value" class="hub__btn hub__btn--primary">
                    选择图片
                    <input
                      ref="fileInput"
                      type="file"
                      accept="image/*"
                      class="hub__file-input"
                      @change="onFileChange"
                    />
                  </label>
                  <button
                    v-if="!bg.pendingUrl.value && bg.dataUrl.value"
                    class="hub__btn hub__btn--ghost"
                    @click="onResetPos"
                  >重置位置</button>
                  <button
                    v-if="!bg.pendingUrl.value && bg.dataUrl.value"
                    class="hub__btn hub__btn--danger"
                    @click="onRemoveBg"
                  >移除背景</button>

                  <button
                    v-if="bg.pendingUrl.value"
                    class="hub__btn hub__btn--primary"
                    @click="onApply"
                  >应用此背景</button>
                  <button
                    v-if="bg.pendingUrl.value"
                    class="hub__btn hub__btn--ghost"
                    @click="onCancel"
                  >取消</button>
                </div>

                <p v-if="bg.error.value" class="hub__error">{{ bg.error.value }}</p>

                <p class="hub__note">图片仅保存在本浏览器，不会上传到服务器。</p>

                <button class="hub__back" @click="onBack">
                  <span class="hub__back-arrow">←</span> 返回设置菜单
                </button>
              </div>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import { useThemeStore } from '@/stores/themeStore';
import { useBgImage } from '@/composables/useBgImage';
import { useAchievementStore } from '@/stores/achievementStore';

const props = defineProps<{ visible: boolean }>();
const emit = defineEmits<{ onClose: []; onOpenApi: [] }>();

const theme = useThemeStore();
const bg = useBgImage();

const view = ref<'menu' | 'bg'>('menu');
const fileInput = ref<HTMLInputElement | null>(null);

// 预览显示：优先 pending（待确认），其次已生效
const displayUrl = computed(() => bg.pendingUrl.value || bg.dataUrl.value);

watch(
  () => props.visible,
  (v) => {
    if (v) {
      view.value = 'menu';
      bg.cancelPending();
    }
  },
);

function onCardClick(card: string) {
  if (card === 'api') {
    emit('onOpenApi');
  } else if (card === 'bg') {
    view.value = 'bg';
  }
}

async function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  try {
    await bg.previewImage(file);
  } catch (err) {
    console.error('背景图读取失败', err);
  }
  if (fileInput.value) fileInput.value.value = '';
}

function onApply() {
  bg.applyPending();
  useAchievementStore().unlock('one_last_kiss');
}

function onCancel() {
  bg.cancelPending();
}

function onRemoveBg() {
  bg.removeImage();
  useAchievementStore().unlock('cant_say_goodbye');
}

function onResetPos() {
  bg.resetPos();
  useAchievementStore().unlock('poincare_return');
}

function onBack() {
  bg.cancelPending();
  view.value = 'menu';
}

// ===== 拖拽调整背景图位置 =====
let dragging = false;
let dragStartX = 0;
let dragStartY = 0;
let dragStartBgX = 50;
let dragStartBgY = 50;
const previewRef = ref<HTMLElement | null>(null);

function onDragStart(e: MouseEvent) {
  if (!displayUrl.value) return;
  dragging = true;
  dragStartX = e.clientX;
  dragStartY = e.clientY;
  dragStartBgX = bg.bgX.value;
  dragStartBgY = bg.bgY.value;
  previewRef.value = (e.currentTarget as HTMLElement);
  window.addEventListener('mousemove', onDragMove);
  window.addEventListener('mouseup', onDragEnd);
  e.preventDefault();
}

function onDragMove(e: MouseEvent) {
  if (!dragging || !previewRef.value) return;
  const rect = previewRef.value.getBoundingClientRect();
  if (rect.width === 0 || rect.height === 0) return;
  const dx = ((e.clientX - dragStartX) / rect.width) * 100;
  const dy = ((e.clientY - dragStartY) / rect.height) * 100;
  bg.setPos(dragStartBgX + dx, dragStartBgY + dy);
}

function onDragEnd() {
  dragging = false;
  window.removeEventListener('mousemove', onDragMove);
  window.removeEventListener('mouseup', onDragEnd);
  bg.persistPos();
}

function onTouchStart(e: TouchEvent) {
  if (!displayUrl.value) return;
  const t = e.touches[0];
  dragging = true;
  dragStartX = t.clientX;
  dragStartY = t.clientY;
  dragStartBgX = bg.bgX.value;
  dragStartBgY = bg.bgY.value;
  previewRef.value = (e.currentTarget as HTMLElement);
  window.addEventListener('touchmove', onTouchMove, { passive: false });
  window.addEventListener('touchend', onTouchEnd);
}

function onTouchMove(e: TouchEvent) {
  if (!dragging || !previewRef.value) return;
  e.preventDefault();
  const t = e.touches[0];
  const rect = previewRef.value.getBoundingClientRect();
  if (rect.width === 0 || rect.height === 0) return;
  const dx = ((t.clientX - dragStartX) / rect.width) * 100;
  const dy = ((t.clientY - dragStartY) / rect.height) * 100;
  bg.setPos(dragStartBgX + dx, dragStartBgY + dy);
}

function onTouchEnd() {
  dragging = false;
  window.removeEventListener('touchmove', onTouchMove);
  window.removeEventListener('touchend', onTouchEnd);
  bg.persistPos();
}
</script>

<style scoped>
/* ===== 顶部斜杠标题 ===== */
.hub__head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.hub__head-slash {
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 700;
  color: var(--amber);
}

.hub__head-title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.2em;
  color: var(--amber);
}

.hub__head-line {
  flex: 1;
  height: 1px;
  background: var(--amber);
  opacity: 0.4;
}

/* ===== 卡片网格 ===== */
.hub__grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hub__card {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 18px 20px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  clip-path: polygon(var(--cut-sm) 0, 100% 0, 100% calc(100% - var(--cut-sm)), calc(100% - var(--cut-sm)) 100%, 0 100%, 0 var(--cut-sm));
  cursor: pointer;
  transition: border-color 200ms, background 200ms, transform 160ms;
  text-align: left;
  font-family: inherit;
  color: inherit;
}

.hub__card:hover:not(:disabled) {
  border-color: var(--amber);
  background: var(--accent-soft);
  transform: translateX(4px);
}

.hub__card:active:not(:disabled) {
  transform: translateX(2px);
}

.hub__card--locked {
  opacity: 0.4;
  cursor: not-allowed;
}

.hub__card-num {
  font-family: var(--font-display);
  font-size: 36px;
  line-height: 1;
  color: var(--amber);
  min-width: 48px;
  flex-shrink: 0;
}

.hub__card--locked .hub__card-num {
  color: var(--text-muted);
}

.hub__card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.hub__card-title {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--text-primary);
}

.hub__card-en {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.24em;
  color: var(--text-muted);
}

.hub__card-desc {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.hub__card-cta {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.1em;
  color: var(--amber);
  white-space: nowrap;
  flex-shrink: 0;
}

.hub__card-cta--locked {
  font-size: 16px;
}

/* ===== 背景设置视图 ===== */
.hub__bg {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hub__preview {
  width: 100%;
  height: 180px;
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
  border: 1px solid var(--border-subtle);
  overflow: hidden;
  position: relative;
  background: var(--bg-primary);
}

.hub__preview-img {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.hub__preview-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background:
    repeating-linear-gradient(45deg, transparent 0 14px, var(--accent-soft) 14px 28px),
    var(--bg-primary);
}

.hub__preview-tag {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.4em;
  color: var(--text-muted);
  border: 1px dashed var(--border-subtle);
  padding: 4px 12px;
}

.hub__preview-cn {
  font-size: 12px;
  color: var(--text-muted);
}

.hub__pending-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.2em;
  color: var(--on-amber);
  background: var(--amber);
  padding: 3px 8px;
  clip-path: polygon(4px 0, 100% 0, calc(100% - 4px) 100%, 0 100%);
}

/* 拖拽提示 */
.hub__drag-hint {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  color: var(--text-secondary);
  background: rgba(0, 0, 0, 0.6);
  padding: 3px 10px;
  border-radius: 3px;
  pointer-events: none;
  white-space: nowrap;
}

/* 可拖拽时显示 move 光标 */
.hub__preview--draggable {
  cursor: move;
  cursor: grab;
}
.hub__preview--draggable:active {
  cursor: grabbing;
}

.hub__actions {
  display: flex;
  gap: 10px;
}

.hub__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-height: 44px;
  padding: 0 20px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.05em;
  clip-path: polygon(var(--cut-sm) 0, 100% 0, 100% calc(100% - var(--cut-sm)), calc(100% - var(--cut-sm)) 100%, 0 100%, 0 var(--cut-sm));
  cursor: pointer;
  transition: background 200ms, border-color 200ms, color 200ms;
  font-family: inherit;
  border: 1px solid transparent;
}

.hub__btn--primary {
  background: var(--amber);
  color: var(--on-amber);
  border-color: var(--amber);
}

.hub__btn--primary:hover {
  background: var(--amber-deep);
  border-color: var(--amber-deep);
}

.hub__btn--danger {
  background: transparent;
  color: var(--danger);
  border-color: rgba(255, 45, 149, 0.3);
}

.hub__btn--danger:hover {
  background: var(--danger-soft);
  border-color: var(--danger);
}

.hub__btn--ghost {
  background: transparent;
  color: var(--text-secondary);
  border-color: var(--border-subtle);
}

.hub__btn--ghost:hover {
  color: var(--amber);
  border-color: var(--amber);
}

.hub__file-input {
  display: none;
}

.hub__note {
  font-size: 11px;
  color: var(--text-muted);
  text-align: center;
  line-height: 1.6;
}

.hub__error {
  font-size: 12px;
  color: var(--danger);
  text-align: center;
  line-height: 1.6;
  padding: 6px 12px;
  background: var(--danger-soft);
  border: 1px solid rgba(255, 45, 149, 0.3);
  border-radius: 4px;
}

.hub__back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 0;
  font-family: inherit;
  align-self: flex-start;
  transition: color 160ms;
}

.hub__back:hover {
  color: var(--amber);
}

.hub__back-arrow {
  font-size: 14px;
}

/* ===== 日间模式 ===== */
.hub-mask {
  position: fixed;
  inset: 0;
  background: var(--mask-light);
  z-index: 120;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hub--ak {
  width: 420px;
  max-width: 92vw;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}

.hub__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-subtle);
}

.hub__title {
  font-size: 16px;
  font-weight: 600;
}

.hub__close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  color: var(--text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  border-radius: 50%;
  transition: background 160ms;
}

.hub__close:hover {
  background: var(--bg-panel-2);
  color: var(--accent-bright);
}

.hub__body {
  padding: 20px;
  overflow-y: auto;
}

/* 日间模式卡片去掉斜切角 */
[data-theme='ak'] .hub__card,
[data-theme='ak'] .hub__preview,
[data-theme='ak'] .hub__btn {
  clip-path: none;
  border-radius: 6px;
}

/* ===== 动画 ===== */
.hub-enter-active,
.hub-leave-active {
  transition: opacity 250ms;
}
.hub-enter-active .hub--ak,
.hub-leave-active .hub--ak {
  transition: transform 250ms ease-out, opacity 250ms;
}
.hub-enter-from,
.hub-leave-to {
  opacity: 0;
}
.hub-enter-from .hub--ak,
.hub-leave-to .hub--ak {
  transform: scale(0.92);
  opacity: 0;
}

/* ===== 移动端适配 ===== */
@media (max-width: 640px) {
  .hub__card {
    padding: 14px 16px;
    gap: 14px;
  }
  .hub__card-num {
    font-size: 28px;
    min-width: 36px;
  }
  .hub__card-title {
    font-size: 14px;
  }
  .hub__card-desc {
    font-size: 11px;
  }
  .hub__preview {
    height: 140px;
  }
}
</style>