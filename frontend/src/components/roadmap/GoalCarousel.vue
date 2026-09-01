<template>
  <div class="carousel">
    <!-- 顶部提示 -->
    <div class="carousel__hint">
      <span class="carousel__hint-en">SELECT YOUR PATH</span>
      <span class="carousel__hint-cn">选择你的发展目标</span>
    </div>

    <!-- 轮播主体 -->
    <div class="carousel__stage" :style="{ height: stageHeight }">
      <button
        class="carousel__arrow carousel__arrow--left"
        aria-label="上一个目标"
        @click="prev"
      >
        <NeonIcon name="back" :size="22" />
      </button>

      <div class="carousel__track">
        <div
          v-for="(g, i) in goals"
          :key="g.id"
          class="gcard"
          :class="cardClass(i)"
          :style="cardStyle(i)"
          @click="onCardClick(g, i)"
        >
          <!-- 顶部编号行 -->
          <div class="gcard__meta">
            <span class="gcard__num">{{ g.num }}</span>
            <span class="gcard__en">{{ g.en }}</span>
          </div>

          <!-- 主视觉区（图片占位） -->
          <div class="gcard__visual">
            <img v-if="g.image" :src="g.image" :alt="g.title" class="gcard__img" />
            <div v-else class="gcard__placeholder" aria-hidden="true">
              <span class="gcard__placeholder-tag">VISUAL</span>
              <span class="gcard__placeholder-cn">主视觉待补充</span>
            </div>
          </div>

          <!-- 标题区 -->
          <div class="gcard__body">
            <h3 class="gcard__title">{{ g.title }}</h3>
            <p class="gcard__desc">{{ g.desc }}</p>
            <span v-if="i === active" class="gcard__cta">
              进入路线
              <NeonIcon name="arrow-right" :size="14" />
            </span>
          </div>
        </div>
      </div>

      <button
        class="carousel__arrow carousel__arrow--right"
        aria-label="下一个目标"
        @click="next"
      >
        <NeonIcon name="arrow-right" :size="22" />
      </button>
    </div>

    <!-- 指示器 -->
    <div class="carousel__dots" role="tablist" aria-label="目标切换">
      <button
        v-for="(g, i) in goals"
        :key="g.id"
        class="carousel__dot"
        :class="{ 'carousel__dot--active': i === active }"
        role="tab"
        :aria-selected="i === active"
        :aria-label="g.title"
        @click="active = i"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import type { RoadmapGoal } from '@/data/roadmapData';

const props = defineProps<{ goals: RoadmapGoal[] }>();
const emit = defineEmits<{ select: [goal: RoadmapGoal] }>();

const active = ref(0);
const expanding = ref(false);

function cardClass(i: number) {
  const offset = i - active.value;
  return {
    'gcard--active': offset === 0,
    'gcard--side': Math.abs(offset) === 1,
    'gcard--far': Math.abs(offset) > 1,
    'gcard--expanding': expanding.value && offset === 0,
  };
}

function cardStyle(i: number) {
  const offset = i - active.value;
  const dir = offset === 0 ? 0 : Math.sign(offset);
  const abs = Math.abs(offset);
  // 中心卡片不动；相邻卡片横向偏移并缩小压暗；更远的几乎隐藏
  const translateX = dir * (abs === 1 ? 78 : 130);
  const scale = abs === 0 ? 1 : abs === 1 ? 0.86 : 0.72;
  const opacity = abs === 0 ? 1 : abs === 1 ? 0.45 : 0;
  const zIndex = 10 - abs;
  return {
    transform: `translateX(-50%) translate(${translateX}%, 0) scale(${scale})`,
    opacity: String(opacity),
    zIndex: String(zIndex),
    pointerEvents: abs <= 1 ? 'auto' : 'none',
  };
}

const stageHeight = computed(() => 'clamp(420px, 56vh, 560px)');

function prev() {
  expanding.value = false;
  active.value = (active.value - 1 + props.goals.length) % props.goals.length;
}
function next() {
  expanding.value = false;
  active.value = (active.value + 1) % props.goals.length;
}

function onCardClick(goal: RoadmapGoal, i: number) {
  if (i !== active.value) {
    active.value = i;
    return;
  }
  // 当前卡片点击 → 展开动画 → 通知父级进入时间线
  expanding.value = true;
  window.setTimeout(() => emit('select', goal), 300);
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'ArrowLeft') prev();
  else if (e.key === 'ArrowRight') next();
  else if (e.key === 'Enter' && !expanding.value) onCardClick(props.goals[active.value], active.value);
}

onMounted(() => window.addEventListener('keydown', onKeydown));
onUnmounted(() => window.removeEventListener('keydown', onKeydown));
</script>

<style scoped>
/* ===== 顶部提示 ===== */
.carousel__hint {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 12px;
  margin-bottom: clamp(16px, 3vw, 28px);
}
.carousel__hint-en {
  font-family: var(--font-display);
  font-size: clamp(15px, 2.4vw, 20px);
  letter-spacing: 0.35em;
  color: var(--amber);
}
.carousel__hint-cn {
  font-size: clamp(12px, 1.8vw, 14px);
  color: var(--text-secondary);
  letter-spacing: 0.2em;
}

/* ===== 舞台 ===== */
.carousel__stage {
  position: relative;
  display: flex;
  align-items: center;
}

/* 左右箭头（ZZZ 设定档案式半透明箭头） */
.carousel__arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 20;
  width: 46px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  background: var(--surface-glass);
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-sm);
  cursor: pointer;
  transition: color 180ms, border-color 180ms, background 180ms;
}
.carousel__arrow--left { left: 2%; }
.carousel__arrow--right { right: 2%; }
.carousel__arrow:hover {
  color: var(--amber);
  border-color: var(--border-glow);
  background: var(--accent-mid);
}

/* ===== 轨道与卡片 ===== */
.carousel__track {
  position: relative;
  width: min(420px, 88vw);
  height: 100%;
  margin: 0 auto;
}

.gcard {
  position: absolute;
  top: 0;
  left: 50%;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-md);
  cursor: pointer;
  transition: transform 420ms cubic-bezier(0.22, 1, 0.36, 1),
    opacity 380ms ease, border-color 220ms ease, box-shadow 220ms ease;
  will-change: transform, opacity;
}
.gcard--active {
  border-color: var(--border-glow);
  box-shadow: var(--shadow-glow), var(--shadow-card);
}
.gcard--side:hover {
  border-color: var(--border-glow);
}
/* 点击展开动画 */
.gcard--expanding {
  transform: translateX(-50%) scale(1.08) !important;
  opacity: 0 !important;
  box-shadow: 0 0 60px var(--amber-halo);
}

/* 编号行 */
.gcard__meta {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 14px 18px 10px;
}
.gcard__num {
  font-family: var(--font-display);
  font-size: clamp(34px, 6vw, 48px);
  line-height: 1;
  color: var(--amber);
}
.gcard__en {
  font-family: var(--font-mono);
  font-size: clamp(10px, 1.6vw, 12px);
  letter-spacing: 0.28em;
  color: var(--text-muted);
}

/* 主视觉区（图片占位） */
.gcard__visual {
  flex: 1;
  position: relative;
  margin: 0 14px;
  min-height: 0;
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  overflow: hidden;
}
.gcard__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.gcard__placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background:
    repeating-linear-gradient(
      45deg,
      transparent 0 14px,
      var(--accent-soft) 14px 28px
    ),
    var(--bg-primary);
}
.gcard__placeholder-tag {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.4em;
  color: var(--text-muted);
  border: 1px dashed var(--border-subtle);
  padding: 4px 12px;
}
.gcard__placeholder-cn {
  font-size: 12px;
  color: var(--text-muted);
}

/* 标题区 */
.gcard__body {
  padding: 14px 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.gcard__title {
  margin: 0;
  font-size: clamp(22px, 4vw, 28px);
  font-weight: 800;
  letter-spacing: 0.12em;
  color: var(--text-primary);
}
.gcard__desc {
  margin: 0;
  font-size: clamp(12px, 1.8vw, 13px);
  line-height: 1.6;
  color: var(--text-secondary);
}
.gcard__cta {
  margin-top: 10px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  align-self: flex-end;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.2em;
  color: var(--amber);
}
.gcard__cta :deep(.neon-icon) {
  transition: transform 200ms;
}
.gcard--active:hover .gcard__cta :deep(.neon-icon) {
  transform: translateX(4px);
}

/* ===== 指示器 ===== */
.carousel__dots {
  display: flex;
  justify-content: center;
  gap: 14px;
  margin-top: clamp(18px, 3vw, 26px);
}
.carousel__dot {
  width: 28px;
  height: 4px;
  background: var(--border-subtle);
  clip-path: var(--clip-sm);
  cursor: pointer;
  transition: background 200ms;
}
.carousel__dot--active {
  background: var(--amber);
}

/* ===== 移动端 ===== */
@media (max-width: 640px) {
  .carousel__arrow {
    width: 38px;
    height: 52px;
  }
  .carousel__arrow--left { left: 0; }
  .carousel__arrow--right { right: 0; }
  .gcard__meta { padding: 10px 14px 8px; }
  .gcard__body { padding: 10px 14px 14px; }
}
</style>
