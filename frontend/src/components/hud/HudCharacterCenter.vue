<template>
  <div class="character" :class="{ 'character--activating': activating }">
    <!-- 游戏登录界面风格大标题（参照参考图排版） -->
    <div class="character__hero">
      <h1 class="character__hero-title">
        <span class="character__hero-line">信科院</span>
        <span class="character__hero-line character__hero-line--accent">指南</span>
      </h1>
      <span class="character__hero-script">Guide</span>
      <p class="character__hero-tag">梦回人远许多愁，只在梨花风雨处</p>
    </div>

    <button class="character__trigger" aria-label="与 AI 助手对话" @click="onActivate">
      <span class="character__rings">
        <span class="character__ring character__ring--1" />
        <span class="character__ring character__ring--2" />
        <span class="character__ring character__ring--3" />
        <span class="character__ring-glow" />
      </span>
      <img class="character__image" :src="characterImage" alt="娘化立绘()" draggable="false" />
      <span class="character__cta">
        <span class="character__cta-main">{{ mainText }}</span>
        <span class="character__cta-sub">{{ subText }}</span>
      </span>
    </button>
    <p v-if="slogan" class="character__slogan">{{ slogan }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

withDefaults(
  defineProps<{
    characterImage: string;
    ringColor?: string;
    mainText?: string;
    subText?: string;
    slogan?: string;
  }>(),
  {
    ringColor: '#FFC82E',
    mainText: '点击与我对话',
    subText: 'AI问答助手',
    slogan: '你就问吧！',
  },
);

const emit = defineEmits<{ onActivate: [] }>();

const activating = ref(false);

function onActivate() {
  if (activating.value) return;
  activating.value = true;
  // FR-CHAR-03：光圈放大 + 收缩动画后跳转
  setTimeout(() => {
    emit('onActivate');
    activating.value = false;
  }, 480);
}
</script>

<style scoped>
.character {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

/* ---- 大标题区 ---- */
.character__hero {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  user-select: none;
  z-index: 2;
}

.character__hero-title {
  display: flex;
  gap: 0.18em;
  font-size: clamp(40px, 5.4vw, 76px);
  font-weight: 900;
  line-height: 1.05;
  letter-spacing: 0.04em;
  color: var(--text-primary);
  text-shadow: 0 4px 24px rgba(0, 0, 0, 0.6);
}

.character__hero-line--accent {
  color: var(--amber);
  text-shadow: 0 0 24px var(--amber-glow), 0 4px 24px rgba(0, 0, 0, 0.6);
}

.character__hero-script {
  font-family: var(--font-display);
  font-style: italic;
  font-size: clamp(18px, 2.2vw, 30px);
  letter-spacing: 8px;
  color: var(--accent-bright);
  margin-top: 2px;
}

.character__hero-tag {
  margin-top: 8px;
  font-size: 15px;
  color: var(--text-secondary);
  letter-spacing: 2px;
}

/* ---- 立绘触发区 ---- */
.character__trigger {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: transform 200ms;
}

.character__trigger:hover {
  transform: scale(1.03);
}

.character__trigger:hover .character__image {
  filter: drop-shadow(0 0 28px rgba(255, 200, 46, 0.45));
}

.character__trigger:active {
  transform: scale(0.97);
}

.character__rings {
  position: absolute;
  top: 44%;
  left: 50%;
  width: 340px;
  height: 340px;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.character__ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 1px solid v-bind(ringColor);
  opacity: 0.6;
  animation: ring-breathe 2s infinite ease-in-out;
}

.character__ring--2 {
  inset: 26px;
  opacity: 0.4;
  animation-delay: 0.4s;
}

.character__ring--3 {
  inset: 56px;
  opacity: 0.25;
  animation-delay: 0.8s;
}

.character__ring-glow {
  position: absolute;
  inset: -10%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 200, 46, 0.14) 0%, transparent 65%);
  animation: ring-breathe 2s infinite ease-in-out;
}

@keyframes ring-breathe {
  0%, 100% { transform: scale(1); opacity: 0.7; }
  50% { transform: scale(1.05); opacity: 1; }
}

.character--activating .character__rings {
  animation: ring-activate 480ms ease-out;
}

@keyframes ring-activate {
  0% { transform: translate(-50%, -50%) scale(1); }
  60% { transform: translate(-50%, -50%) scale(1.2); }
  100% { transform: translate(-50%, -50%) scale(1); }
}

.character__image {
  position: relative;
  z-index: 0;
  width: 384px;          /* 放大 20% */
  max-width: 67vw;
  height: auto;
  max-height: 48vh;
  object-fit: contain;
  filter: drop-shadow(0 0 18px rgba(255, 200, 46, 0.28));
  transition: filter 200ms;
  mask-image: linear-gradient(to bottom, black 82%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, black 82%, transparent 100%);
}

.character__cta {
  position: relative;
  z-index: 3;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  margin-top: -16px;
  padding: 8px 24px;
  border-radius: 999px;
  border: 2px solid var(--amber);
  background: linear-gradient(135deg, rgba(255, 200, 46, 0.18) 0%, rgba(240, 168, 0, 0.08) 100%);
  box-shadow: 0 0 16px var(--amber-glow);
  transition: box-shadow 200ms, background 200ms;
}

.character__trigger:hover .character__cta {
  background: linear-gradient(135deg, rgba(255, 200, 46, 0.3) 0%, rgba(240, 168, 0, 0.15) 100%);
  box-shadow: 0 0 24px var(--amber-glow);
}

.character__cta-main {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--amber);
  text-shadow: 0 0 12px var(--amber-glow);
}

.character__cta-sub {
  font-family: var(--font-display);
  font-size: 13px;
  letter-spacing: 4px;
  color: var(--text-secondary);
}

.character__slogan {
  font-size: 14px;
  color: var(--text-secondary);
  text-align: center;
}

@media (max-width: 767px) {
  .character__hero-title {
    font-size: 34px;          /* 38 × 0.9 */
  }
  .character__hero-script {
    font-size: 14px;
    letter-spacing: 5px;
  }
  .character__hero-tag {
    font-size: 12px;
  }
  .character__rings {
    width: 160px;
    height: 160px;
    top: 38%;
  }
  .character__image {
    width: 204px;          /* 170 × 1.2 */
    max-height: 32vh;
  }
  .character__cta {
    margin-top: -8px;
    padding: 6px 18px;
  }
  .character__cta-main {
    font-size: 15px;
  }
  .character__cta-sub {
    font-size: 11px;
  }
  .character__slogan {
    font-size: 13px;
    padding: 0 16px;
  }
}
</style>
