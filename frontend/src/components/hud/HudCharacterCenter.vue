<template>
  <section class="hero">
    <!-- 城市光晕背景 -->
    <div class="hero__glow hero__glow--tl" />
    <div class="hero__glow hero__glow--br" />

    <div class="hero__layout">
      <!-- 左侧：标题 + 按钮 -->
      <div class="hero__left">
        <span class="hero__kicker">JNU INFORMATION</span>
        <h1 class="hero__title glitch-title" data-text="信科院指南">信科院指南</h1>
        <div class="hero__intro">
          <p v-if="gradeSubtitle" class="hero__intro--grade">{{ gradeSubtitle }}</p>
          <p>主要面向对象：信科院/学习编程的学生</p>
          <p class="hero__intro--mid">其他专业可参考就业发展规划以外的内容</p>
          <p>本文档11章节11子文档，共8.1万余字</p>
        </div>
        <div class="hero__actions">
          <!-- 夜间 zzz：zenless-ui 按钮 -->
          <template v-if="theme.isZzz">
            <z-button type="primary" size="large" @click="emit('onGoDest')">目的地</z-button>
            <z-button size="large" @click="emit('onOpenApi')">配置 API</z-button>
          </template>
          <!-- 日间 ak：原版按钮 -->
          <template v-else>
            <button class="hero__btn hero__btn--primary" @click="emit('onGoDest')">
              <span>目的地</span>
              <span class="hero__btn-arrow">→</span>
            </button>
            <button class="hero__btn hero__btn--secondary" @click="emit('onOpenApi')">
              配置 API
            </button>
          </template>
        </div>
      </div>

      <!-- 中间：角色（悬停透出介绍文字） -->
      <div class="hero__figure">
        <img
          class="hero__image"
          :src="characterImage"
          alt="信科院向导立绘"
          draggable="false"
        />
        <div class="hero__overlay">
          <p>本站是面向大学信科院的非官方学生指南，作用仅为减少信息差</p>
          <p>政策，规则或会更变，但过去的经历与未尽总能作鉴</p>
          <p>愿指南能令你走出更遥远距离</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useThemeStore } from '@/stores/themeStore';

defineProps<{
  characterImage: string;
  gradeSubtitle?: string;
}>();

const theme = useThemeStore();

const emit = defineEmits<{
  onGoDest: [];
  onOpenApi: [];
}>();
</script>

<style scoped>
/* ============ Hero ============ */
.hero {
  position: relative;
  min-height: 88vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  overflow: hidden;
}

.hero__glow {
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  filter: blur(120px);
  pointer-events: none;
}

.hero__glow--tl {
  top: -180px;
  left: -140px;
  background: radial-gradient(circle, var(--amber-glow), transparent 70%);
  opacity: 0.5;
}

.hero__glow--br {
  bottom: -220px;
  right: -160px;
  background: radial-gradient(circle, var(--neon-cyan-glow), transparent 70%);
  opacity: 0.35;
}

.hero__layout {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 48px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

/* ---- 左侧标题 + 按钮 ---- */
.hero__left {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 18px;
  min-width: 0;
}

.hero__kicker {
  display: inline-flex;
  align-items: center;
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 3px;
  color: var(--amber);
  text-transform: uppercase;
  border: 1px solid var(--amber);
  padding: 6px 14px;
}

.hero__intro {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.hero__intro--grade {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  color: var(--amber);
  letter-spacing: 1px;
  margin-bottom: 4px;
}

.hero__intro--mid {
  color: var(--amber);
  font-weight: 600;
}

.hero__title {
  position: relative;
  font-family: var(--font-display);
  font-size: clamp(44px, 6.5vw, 88px);
  font-weight: 900;
  line-height: 1.05;
  letter-spacing: 0.06em;
  color: var(--text-primary);
}

/* Glitch 重影（克制） */
.glitch-title::before,
.glitch-title::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  font-family: var(--font-display);
  font-size: clamp(44px, 6.5vw, 88px);
  font-weight: 900;
  line-height: 1.05;
  letter-spacing: 0.06em;
  pointer-events: none;
}

.glitch-title::before {
  color: var(--neon-cyan);
  animation: glitch-anim-1 4s infinite linear alternate-reverse;
  z-index: -1;
  opacity: 0.5;
}

.glitch-title::after {
  color: var(--neon-magenta);
  animation: glitch-anim-2 3.5s infinite linear alternate-reverse;
  z-index: -2;
  opacity: 0.5;
}

@keyframes glitch-anim-1 {
  0% { clip-path: inset(20% 0 60% 0); transform: translate(-2px, 0); }
  25% { clip-path: inset(70% 0 10% 0); transform: translate(2px, 0); }
  50% { clip-path: inset(40% 0 40% 0); transform: translate(-2px, 0); }
  75% { clip-path: inset(10% 0 75% 0); transform: translate(2px, 0); }
  100% { clip-path: inset(55% 0 25% 0); transform: translate(-2px, 0); }
}

@keyframes glitch-anim-2 {
  0% { clip-path: inset(70% 0 10% 0); transform: translate(2px, 0); }
  25% { clip-path: inset(15% 0 65% 0); transform: translate(-2px, 0); }
  50% { clip-path: inset(50% 0 30% 0); transform: translate(2px, 0); }
  75% { clip-path: inset(25% 0 55% 0); transform: translate(-2px, 0); }
  100% { clip-path: inset(60% 0 20% 0); transform: translate(2px, 0); }
}

/* ---- 按钮（指南 btn-primary / btn-secondary） ---- */
.hero__actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.hero__btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
  padding: 15px 30px;
  cursor: pointer;
  transition: all 160ms ease;
}

.hero__btn--primary {
  background: var(--amber);
  color: var(--on-amber);
  font-weight: 900;
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
}

.hero__btn--primary:hover {
  transform: translate(2px, -2px);
  filter: brightness(1.1);
  box-shadow: -4px 4px 0 var(--neon-cyan);
}

.hero__btn--secondary {
  background: transparent;
  color: var(--text-primary);
  border: 2px solid var(--border-subtle);
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
}

.hero__btn--secondary:hover {
  border-color: var(--amber);
  color: var(--amber);
  background: var(--amber-soft);
}

.hero__btn-arrow {
  transition: transform 160ms;
}

.hero__btn--primary:hover .hero__btn-arrow {
  transform: translateX(3px);
}

/* ---- 中间角色：悬停透出介绍 ---- */
.hero__figure {
  position: relative;
  flex-shrink: 0;
  width: 380px;
  max-width: 40vw;
}

.hero__image {
  display: block;
  width: 100%;
  height: auto;
  max-height: 70vh;
  object-fit: contain;
  filter: drop-shadow(0 8px 32px var(--shadow-deep));
  transition: filter 300ms;
  animation: figure-float 5s infinite ease-in-out;
}

@keyframes figure-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.hero__figure:hover .hero__image {
  filter: blur(6px) brightness(0.65);
}

/* 悬停透出的介绍文字：无蒙版，直接浮在模糊人物上 */
.hero__overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
  padding: 28px;
  opacity: 0;
  transition: opacity 260ms ease;
  pointer-events: none;
}

.hero__figure:hover .hero__overlay {
  opacity: 1;
}

.hero__overlay p {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-primary);
  text-align: center;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.9);
}

/* ---- 响应式 ---- */
@media (max-width: 900px) {
  .hero__layout {
    flex-direction: column;
    gap: 24px;
    text-align: center;
  }

  .hero__left {
    align-items: center;
  }

  .hero__figure {
    width: 260px;
    max-width: 70vw;
  }

  .hero__image {
    max-height: 40vh;
  }
}

@media (max-width: 767px) {
  .hero {
    min-height: 60vh;
    padding: 28px 16px;
  }

  .hero__title,
  .glitch-title::before,
  .glitch-title::after {
    font-size: 40px;
  }

  .hero__kicker {
    font-size: 11px;
    letter-spacing: 3px;
  }

  .hero__btn {
    font-size: 14px;
    padding: 13px 24px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero__image { animation: none; }
}
</style>
