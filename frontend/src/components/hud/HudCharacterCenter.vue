<template>
  <section class="hero">
    <!-- 海报式文字层 -->
    <div class="hero__masthead">
      <span class="hero__kicker">JNU INFORMATION</span>
      <h1 class="hero__title glitch-title" data-text="XKZ · GUIDE">XKZ · GUIDE</h1>
      <p class="hero__tagline">梦回人远许多愁，只在梨花风雨处</p>
      <span class="hero__year">2026</span>
    </div>

    <!-- 角色主视觉 -->
    <div class="hero__figure" @click="onActivate">
      <!-- 少量几何定位线 -->
      <span class="hero__cross hero__cross--tl" />
      <span class="hero__cross hero__cross--br" />
      <span class="hero__vline" />
      <img
        class="hero__image"
        :src="characterImage"
        alt="信科院向导立绘"
        draggable="false"
      />
      <span class="hero__figure-label">CAMPUS GUIDE</span>
    </div>

    <!-- 邀请语 -->
    <p class="hero__invite">今天想去哪里？</p>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';

withDefaults(
  defineProps<{
    characterImage: string;
    mainText?: string;
    subText?: string;
    slogan?: string;
  }>(),
  {
    mainText: '点击与我对话',
    subText: 'AI 问答助手',
    slogan: '你就问吧！',
  },
);

const emit = defineEmits<{ onActivate: [] }>();
const activating = ref(false);

function onActivate() {
  if (activating.value) return;
  activating.value = true;
  setTimeout(() => {
    emit('onActivate');
    activating.value = false;
  }, 480);
}
</script>

<style scoped>
/* ============ Hero 海报区 ============ */
.hero {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
  padding: 32px 24px 24px;
  min-height: 60vh;
}

/* ---- 报头文字层 ---- */
.hero__masthead {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  text-align: center;
  z-index: 2;
}

.hero__kicker {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 4px;
  color: var(--amber);
  text-transform: uppercase;
}

.hero__title {
  position: relative;
  font-family: var(--font-display);
  font-size: clamp(48px, 9vw, 96px);
  font-weight: 900;
  line-height: 0.95;
  letter-spacing: 0.06em;
  color: var(--text-primary);
  text-transform: uppercase;
}

/* Glitch 只作为瞬间点缀，幅度克制 */
.glitch-title::before,
.glitch-title::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  font-family: var(--font-display);
  font-size: clamp(48px, 9vw, 96px);
  font-weight: 900;
  line-height: 0.95;
  letter-spacing: 0.06em;
  text-transform: uppercase;
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

.hero__tagline {
  font-size: 14px;
  color: var(--text-secondary);
  letter-spacing: 3px;
  margin-top: 2px;
}

.hero__year {
  font-family: var(--font-display);
  font-size: 13px;
  letter-spacing: 6px;
  color: var(--text-muted);
  margin-top: 4px;
}

/* ---- 角色主视觉 ---- */
.hero__figure {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: transform 300ms ease;
}

.hero__figure:hover {
  transform: translateY(-4px);
}

.hero__figure:hover .hero__image {
  filter: drop-shadow(0 0 24px var(--amber-halo));
}

/* 少量几何定位符 — 平面设计感，非科技HUD */
.hero__cross {
  position: absolute;
  width: 16px;
  height: 16px;
  pointer-events: none;
  z-index: 3;
}

.hero__cross::before,
.hero__cross::after {
  content: '';
  position: absolute;
  background: var(--amber);
}

.hero__cross::before {
  top: 50%;
  left: 0;
  right: 0;
  height: 1.5px;
  transform: translateY(-50%);
}

.hero__cross::after {
  left: 50%;
  top: 0;
  bottom: 0;
  width: 1.5px;
  transform: translateX(-50%);
}

.hero__cross--tl {
  top: 0;
  left: -8px;
}

.hero__cross--br {
  bottom: 30px;
  right: -8px;
}

.hero__vline {
  position: absolute;
  top: 0;
  bottom: 30px;
  right: -24px;
  width: 1px;
  background: var(--border-subtle);
  z-index: 1;
}

.hero__image {
  position: relative;
  z-index: 2;
  width: 360px;
  max-width: 72vw;
  height: auto;
  max-height: 50vh;
  object-fit: contain;
  filter: drop-shadow(0 8px 32px var(--shadow-deep));
  transition: filter 300ms;
  mask-image: linear-gradient(to bottom, black 88%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, black 88%, transparent 100%);
  animation: figure-float 5s infinite ease-in-out;
}

@keyframes figure-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.hero__figure-label {
  position: absolute;
  bottom: 14px;
  left: 50%;
  transform: translateX(-50%);
  font-family: var(--font-mono);
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 4px;
  color: var(--text-muted);
  text-transform: uppercase;
  z-index: 3;
  white-space: nowrap;
}

/* ---- 邀请语 ---- */
.hero__invite {
  font-family: var(--font-display);
  font-size: clamp(20px, 3vw, 28px);
  font-weight: 500;
  letter-spacing: 4px;
  color: var(--amber);
  text-align: center;
  margin-top: 4px;
}

/* ---- 响应式 ---- */
@media (max-width: 767px) {
  .hero {
    padding: 20px 16px 16px;
    min-height: 50vh;
    gap: 12px;
  }

  .hero__title,
  .glitch-title::before,
  .glitch-title::after {
    font-size: 44px;
  }

  .hero__kicker {
    font-size: 10px;
    letter-spacing: 3px;
  }

  .hero__tagline {
    font-size: 12px;
    letter-spacing: 2px;
  }

  .hero__image {
    width: 220px;
    max-height: 36vh;
  }

  .hero__cross--tl { left: -4px; }
  .hero__cross--br { right: -4px; bottom: 24px; }
  .hero__vline { display: none; }

  .hero__invite {
    font-size: 18px;
    letter-spacing: 3px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero__image { animation: none; }
}
</style>
