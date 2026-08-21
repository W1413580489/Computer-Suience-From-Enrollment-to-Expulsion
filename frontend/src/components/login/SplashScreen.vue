<template>
  <div
    class="splash"
    :class="theme.isZzz ? 'splash--zzz' : 'splash--ak'"
    @click="skipToLogin"
  >
    <!-- ZZZ 夜间：网格背景 + 浮动菱形 -->
    <div v-if="theme.isZzz" class="splash__grid-bg" />
    <div v-if="theme.isZzz" class="splash__particles">
      <span v-for="i in 5" :key="i" class="splash__particle" :style="particleStyle(i)" />
    </div>
    <!-- AK 日间：发丝网格 + 对角线 -->
    <div v-else class="splash__ak-grid" />
    <div v-if="!theme.isZzz" class="splash__ak-corners">
      <span class="splash__ak-corner splash__ak-corner--tl" />
      <span class="splash__ak-corner splash__ak-corner--tr" />
      <span class="splash__ak-corner splash__ak-corner--bl" />
      <span class="splash__ak-corner splash__ak-corner--br" />
    </div>

    <!-- 顶部进度条 -->
    <div class="splash__progress-track" :class="theme.isZzz ? 'splash__progress-track--zzz' : 'splash__progress-track--ak'">
      <div class="splash__progress-bar" :class="theme.isZzz ? 'splash__progress-bar--zzz' : 'splash__progress-bar--ak'" :style="{ width: progress + '%' }" />
    </div>

    <!-- 主体内容 -->
    <div class="splash__content">
      <!-- LOGO -->
      <h1 v-if="theme.isZzz" class="splash__logo splash__logo--zzz">TERMINAL CONNECT</h1>
      <div v-else class="splash__logo-wrap">
        <h1 class="splash__logo splash__logo--ak">RHODES ISLAND</h1>
        <span class="splash__logo-sub">MEMBER ARCHIVE</span>
      </div>

      <!-- 打字机文字 -->
      <div class="splash__terminal">
        <p v-for="(line, i) in visibleLines" :key="i" class="splash__line">
          <span class="splash__prompt" :class="theme.isZzz ? 'splash__prompt--zzz' : 'splash__prompt--ak'">{{ theme.isZzz ? '>' : '►' }}</span>
          <span class="splash__text">{{ line }}</span>
          <span v-if="i === visibleLines.length - 1 && !allDone" class="splash__cursor" :class="theme.isZzz ? 'splash__cursor--zzz' : 'splash__cursor--ak'" />
        </p>
      </div>

      <!-- 底部波形图 -->
      <div class="splash__wave">
        <span
          v-for="i in 5"
          :key="i"
          class="splash__wave-bar"
          :class="theme.isZzz ? 'splash__wave-bar--zzz' : 'splash__wave-bar--ak'"
          :style="{ animationDelay: (i - 1) * 0.15 + 's' }"
        />
      </div>
    </div>

    <!-- 跳过按钮 -->
    <button class="splash__skip" @click.stop="skipToLogin">
      跳过 <span class="splash__skip-arrow">>></span>
    </button>

    <!-- 游客模式 -->
    <button class="splash__guest" @click.stop="guestBrowse">
      游客模式浏览
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useThemeStore } from '@/stores/themeStore';

const router = useRouter();
const theme = useThemeStore();

const lines = theme.isZzz
  ? ['连接终端中枢...', '正在验证身份凭证...', '同步角色数据...', '连接成功。欢迎回来。']
  : ['正在加载组织成员档案...', '校验身份密钥...', '同步战术数据...', '档案加载完成。欢迎入职。'];

const visibleLines = ref<string[]>([]);
const currentText = ref('');
const progress = ref(0);
const allDone = ref(false);

let lineIdx = 0;
let charIdx = 0;
let intervalId: ReturnType<typeof setInterval> | null = null;
let progressId: ReturnType<typeof setInterval> | null = null;
let doneTimer: ReturnType<typeof setTimeout> | null = null;

function particleStyle(i: number) {
  const positions = [
    { top: '12%', left: '8%', delay: '0s' },
    { top: '25%', left: '85%', delay: '-2s' },
    { top: '70%', left: '15%', delay: '-1s' },
    { top: '80%', left: '75%', delay: '-3s' },
    { top: '45%', left: '50%', delay: '-1.5s' },
  ];
  return positions[i - 1] || {};
}

function tick() {
  if (lineIdx >= lines.length) {
    allDone.value = true;
    doneTimer = setTimeout(() => skipToLogin(), 600);
    if (intervalId) clearInterval(intervalId);
    return;
  }
  const target = lines[lineIdx];
  if (charIdx < target.length) {
    charIdx++;
    currentText.value = target.slice(0, charIdx);
    // 更新最后一行
    if (visibleLines.value.length === lineIdx) {
      visibleLines.value.push(currentText.value);
    } else {
      visibleLines.value[lineIdx] = currentText.value;
    }
  } else {
    // 本行完成，移到下一行
    visibleLines.value[lineIdx] = target;
    lineIdx++;
    charIdx = 0;
    currentText.value = '';
  }
}

function skipToLogin() {
  if (intervalId) clearInterval(intervalId);
  if (progressId) clearInterval(progressId);
  if (doneTimer) clearTimeout(doneTimer);
  router.push('/login');
}

function guestBrowse() {
  if (intervalId) clearInterval(intervalId);
  if (progressId) clearInterval(progressId);
  if (doneTimer) clearTimeout(doneTimer);
  router.push('/?guest=1');
}

onMounted(() => {
  intervalId = setInterval(tick, 55);
  progressId = setInterval(() => {
    progress.value = Math.min(100, progress.value + 2.5);
  }, 80);
});

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId);
  if (progressId) clearInterval(progressId);
  if (doneTimer) clearTimeout(doneTimer);
});
</script>

<style scoped>
.splash {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  cursor: pointer;
}

/* ============================================
   ZZZ 夜间模式
   ============================================ */
.splash--zzz {
  background: linear-gradient(135deg, #0A0A0A 0%, #121212 60%, #0A0A0A 100%);
  color: #F5F5F5;
}

.splash__grid-bg {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 217, 61, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 217, 61, 0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
}

.splash__particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.splash__particle {
  position: absolute;
  width: 6px;
  height: 6px;
  background: #FFD93D;
  clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%);
  opacity: 0.15;
  animation: splash-float 6s ease-in-out infinite;
}

@keyframes splash-float {
  0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.15; }
  50% { transform: translateY(-20px) rotate(180deg); opacity: 0.3; }
}

.splash__logo--zzz {
  font-family: 'Bebas Neue', sans-serif;
  font-size: clamp(28px, 5vw, 48px);
  font-weight: 400;
  letter-spacing: 4px;
  color: #FFD93D;
  text-shadow: 0 0 20px rgba(255, 217, 61, 0.4);
  text-align: center;
}

.splash__progress-track--zzz {
  background: rgba(255, 217, 61, 0.08);
  box-shadow: 0 0 10px rgba(255, 217, 61, 0.1);
}

.splash__progress-bar--zzz {
  background: linear-gradient(90deg, #FFD93D, rgba(255, 217, 61, 0.6));
  box-shadow: 0 0 12px rgba(255, 217, 61, 0.5);
}

.splash__prompt--zzz {
  color: #FFD93D;
}

.splash__cursor--zzz {
  background: #FFD93D;
  box-shadow: 0 0 8px rgba(255, 217, 61, 0.6);
}

.splash__wave-bar--zzz:nth-child(odd) {
  background: linear-gradient(to top, #FFD93D, rgba(255, 217, 61, 0.2));
}
.splash__wave-bar--zzz:nth-child(even) {
  background: linear-gradient(to top, #00F0FF, rgba(0, 240, 255, 0.2));
}

/* ============================================
   AK 日间模式
   ============================================ */
.splash--ak {
  background: linear-gradient(135deg, #EAEDF0 0%, #E0E4E8 60%, #EAEDF0 100%);
  color: #1A1D24;
}

.splash__ak-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(200, 50, 63, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(200, 50, 63, 0.02) 1px, transparent 1px);
  background-size: 48px 48px;
  pointer-events: none;
}

.splash__ak-corners {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.splash__ak-corner {
  position: absolute;
  width: 40px;
  height: 40px;
  border: 1px solid rgba(200, 50, 63, 0.3);
}
.splash__ak-corner--tl { top: 24px; left: 24px; border-right: none; border-bottom: none; }
.splash__ak-corner--tr { top: 24px; right: 24px; border-left: none; border-bottom: none; }
.splash__ak-corner--bl { bottom: 24px; left: 24px; border-right: none; border-top: none; }
.splash__ak-corner--br { bottom: 24px; right: 24px; border-left: none; border-top: none; }

.splash__logo-wrap {
  text-align: center;
}

.splash__logo--ak {
  font-family: 'Noto Serif SC', serif;
  font-size: clamp(26px, 4.5vw, 42px);
  font-weight: 700;
  letter-spacing: 2px;
  color: #C8323F;
  text-align: center;
}

.splash__logo-sub {
  display: block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 4px;
  color: #C8323F;
  opacity: 0.6;
  margin-top: 4px;
}

.splash__progress-track--ak {
  background: rgba(200, 50, 63, 0.08);
}

.splash__progress-bar--ak {
  background: #C8323F;
}

.splash__prompt--ak {
  color: #C8323F;
}

.splash__cursor--ak {
  background: #C8323F;
}

.splash__wave-bar--ak:nth-child(odd) {
  background: linear-gradient(to top, #C8323F, rgba(200, 50, 63, 0.2));
}
.splash__wave-bar--ak:nth-child(even) {
  background: linear-gradient(to top, #2A78D8, rgba(42, 120, 216, 0.2));
}

/* ============================================
   通用元素
   ============================================ */
.splash__progress-track {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  overflow: hidden;
}

.splash__progress-bar {
  height: 100%;
  transition: width 80ms linear;
}

.splash__content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
  padding: 0 24px;
}

.splash__terminal {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  line-height: 2;
  text-align: left;
  min-height: 120px;
}

.splash__line {
  display: flex;
  align-items: center;
  gap: 8px;
}

.splash__prompt {
  font-weight: 700;
  flex-shrink: 0;
}

.splash__text {
  color: inherit;
  opacity: 0.9;
}

.splash__cursor {
  display: inline-block;
  width: 8px;
  height: 14px;
  animation: splash-blink 0.6s steps(2) infinite;
}

@keyframes splash-blink {
  0% { opacity: 1; }
  50% { opacity: 0; }
}

.splash__wave {
  display: flex;
  align-items: center;
  gap: 4px;
  height: 40px;
}

.splash__wave-bar {
  width: 4px;
  height: 100%;
  border-radius: 2px;
  animation: splash-wave 0.8s ease-in-out infinite alternate;
}

@keyframes splash-wave {
  0% { transform: scaleY(0.3); opacity: 0.4; }
  100% { transform: scaleY(1); opacity: 0.9; }
}

.splash__skip {
  position: absolute;
  bottom: 24px;
  right: 24px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1px;
  color: inherit;
  opacity: 0.4;
  background: none;
  border: none;
  cursor: pointer;
  transition: opacity 200ms;
}

.splash__skip:hover {
  opacity: 0.8;
}

.splash__skip-arrow {
  margin-left: 4px;
}

.splash__guest {
  position: absolute;
  bottom: 24px;
  left: 24px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1px;
  color: inherit;
  opacity: 0.4;
  background: none;
  border: none;
  cursor: pointer;
  transition: opacity 200ms;
}

.splash__guest:hover {
  opacity: 0.8;
}

@media (max-width: 767px) {
  .splash__terminal {
    font-size: 12px;
  }
  .splash__content {
    gap: 24px;
  }
}
</style>
