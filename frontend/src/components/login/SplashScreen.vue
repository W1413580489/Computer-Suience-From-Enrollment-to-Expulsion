<template>
  <div
    class="splash"
    :class="theme.isZzz ? 'splash--zzz' : 'splash--ak'"
    @click="skipToLogin"
  >
    <!-- ZZZ 夜间：网格背景 + 浮动菱形 + CRT扫描线 + 噪点 -->
    <div v-if="theme.isZzz" class="splash__grid-bg" />
    <div v-if="theme.isZzz" class="splash__particles">
      <span v-for="i in 5" :key="i" class="splash__particle" :style="particleStyle(i)" />
    </div>
    <div v-if="theme.isZzz" class="splash__crt-scanline" />
    <div v-if="theme.isZzz" class="splash__crt-noise" />
    <!-- 数据流下落 -->
    <div v-if="theme.isZzz" class="splash__data-rain">
      <span v-for="i in 8" :key="i" class="splash__rain-col" :style="{ animationDelay: (i * -0.4) + 's', left: (i * 12.5) + '%' }">
        <span v-for="j in 6" :key="j" class="splash__rain-char">0</span>
      </span>
    </div>

    <!-- AK 日间：全息透视网格 + 战术角标 + 文件滚动虚影 -->
    <div v-else class="splash__ak-grid" />
    <div v-if="!theme.isZzz" class="splash__ak-holo-grid" />
    <div v-if="!theme.isZzz" class="splash__ak-file-scroll" />
    <div v-if="!theme.isZzz" class="splash__ak-corners">
      <span class="splash__ak-corner splash__ak-corner--tl" />
      <span class="splash__ak-corner splash__ak-corner--tr" />
      <span class="splash__ak-corner splash__ak-corner--bl" />
      <span class="splash__ak-corner splash__ak-corner--br" />
      <!-- 双线刻度装饰 -->
      <span class="splash__ak-corner-inner splash__ak-corner-inner--tl" />
      <span class="splash__ak-corner-inner splash__ak-corner-inner--tr" />
      <span class="splash__ak-corner-inner splash__ak-corner-inner--bl" />
      <span class="splash__ak-corner-inner splash__ak-corner-inner--br" />
    </div>

    <!-- 顶部进度条 -->
    <div class="splash__progress-track" :class="theme.isZzz ? 'splash__progress-track--zzz' : 'splash__progress-track--ak'">
      <div class="splash__progress-bar" :class="theme.isZzz ? 'splash__progress-bar--zzz' : 'splash__progress-bar--ak'" :style="{ width: progress + '%' }" />
    </div>

    <!-- 主体内容 -->
    <div class="splash__content" :class="theme.isZzz ? 'splash__content--zzz-frame' : 'splash__content--ak-frame'">
      <!-- LOGO -->
      <h1 v-if="theme.isZzz" class="splash__logo splash__logo--zzz" data-text="TERMINAL CONNECT">TERMINAL CONNECT</h1>
      <div v-else class="splash__logo-wrap">
        <h1 class="splash__logo splash__logo--ak">RHODES ISLAND</h1>
        <span class="splash__logo-sub">MEMBER ARCHIVE</span>
      </div>

      <!-- 打字机终端窗口 -->
      <div class="splash__terminal" :class="theme.isZzz ? 'splash__terminal--zzz' : 'splash__terminal--ak'">
        <div v-if="theme.isZzz" class="splash__terminal-header">
          <span class="splash__terminal-dot splash__terminal-dot--r" />
          <span class="splash__terminal-dot splash__terminal-dot--y" />
          <span class="splash__terminal-dot splash__terminal-dot--g" />
          <span class="splash__terminal-title">proxy_connect.sh</span>
        </div>
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

    <!-- 主题切换：预览日/夜间两种开屏风格 -->
    <button class="splash__theme" @click.stop="theme.toggle()">
      <span class="splash__theme-track">
        <span class="splash__theme-knob" :class="{ 'splash__theme-knob--ak': theme.isAk }"></span>
      </span>
      <span class="splash__theme-label">{{ theme.isAk ? '日' : '夜' }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useThemeStore } from '@/stores/themeStore';

const router = useRouter();
const theme = useThemeStore();

const lines = computed(() =>
  theme.isZzz
    ? ['连接终端中枢...', '正在验证身份凭证...', '同步角色数据...', '连接成功。欢迎回来。']
    : ['正在加载组织成员档案...', '校验身份密钥...', '同步战术数据...', '档案加载完成。欢迎入职。'],
);

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
  const cur = lines.value;
  if (lineIdx >= cur.length) {
    allDone.value = true;
    doneTimer = setTimeout(() => skipToLogin(), 600);
    if (intervalId) clearInterval(intervalId);
    return;
  }
  const target = cur[lineIdx];
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

// 主题切换时重置打字机，重新播放新风格的文字
watch(() => theme.mode, () => {
  if (intervalId) clearInterval(intervalId);
  if (doneTimer) clearTimeout(doneTimer);
  visibleLines.value = [];
  currentText.value = '';
  progress.value = 0;
  allDone.value = false;
  lineIdx = 0;
  charIdx = 0;
  intervalId = setInterval(tick, 55);
});

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

/* CRT 扫描线覆盖层 */
.splash__crt-scanline {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent 0px,
    transparent 2px,
    rgba(255, 217, 61, 0.025) 2px,
    rgba(255, 217, 61, 0.025) 3px
  );
  pointer-events: none;
  z-index: 1;
  animation: splash-scanline-move 8s linear infinite;
}

@keyframes splash-scanline-move {
  0% { transform: translateY(0); }
  100% { transform: translateY(6px); }
}

/* CRT 噪点纹理（纯径向渐变模拟） */
.splash__crt-noise {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(255, 217, 61, 0.015) 0%, transparent 8%),
    radial-gradient(circle at 70% 60%, rgba(0, 240, 255, 0.012) 0%, transparent 6%),
    radial-gradient(circle at 50% 80%, rgba(255, 217, 61, 0.01) 0%, transparent 7%),
    radial-gradient(circle at 85% 20%, rgba(255, 217, 61, 0.015) 0%, transparent 5%);
  background-size: 80px 80px, 60px 60px, 100px 100px, 50px 50px;
  pointer-events: none;
  animation: splash-noise-shift 0.3s steps(3) infinite;
  z-index: 1;
}

@keyframes splash-noise-shift {
  0% { transform: translate(0, 0); }
  33% { transform: translate(2px, -1px); }
  66% { transform: translate(-1px, 2px); }
  100% { transform: translate(0, 0); }
}

/* 数据流下落 */
.splash__data-rain {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 1;
}

.splash__rain-col {
  position: absolute;
  top: 0;
  width: 14px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: rgba(255, 217, 61, 0.18);
  animation: splash-rain-fall 4s linear infinite;
}

.splash__rain-char {
  display: block;
  text-align: center;
}

@keyframes splash-rain-fall {
  0% { transform: translateY(-30%); opacity: 0; }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { transform: translateY(110vh); opacity: 0; }
}

/* 终端窗口头部 */
.splash__terminal--zzz {
  border: 1px solid rgba(255, 217, 61, 0.25);
  border-radius: 4px;
  background: rgba(10, 10, 10, 0.5);
  box-shadow:
    0 0 20px rgba(255, 217, 61, 0.08),
    inset 0 0 30px rgba(255, 217, 61, 0.03);
  padding: 12px 16px;
  position: relative;
}

.splash__terminal--zzz::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 4px;
  background: linear-gradient(transparent 50%, rgba(255, 217, 61, 0.02) 50%);
  background-size: 100% 3px;
  pointer-events: none;
}

.splash__terminal-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding-bottom: 8px;
  margin-bottom: 8px;
  border-bottom: 1px solid rgba(255, 217, 61, 0.15);
}

.splash__terminal-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.splash__terminal-dot--r { background: #FF5F56; }
.splash__terminal-dot--y { background: #FFBD2E; }
.splash__terminal-dot--g { background: #27C93F; }

.splash__terminal-title {
  margin-left: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: rgba(255, 217, 61, 0.5);
}

/* LOGO glitch 抖动 */
.splash__logo--zzz {
  position: relative;
}

.splash__logo--zzz::before,
.splash__logo--zzz::after {
  content: attr(data-text);
  position: absolute;
  inset: 0;
  text-align: center;
  overflow: hidden;
  opacity: 0.7;
}

.splash__logo--zzz::before {
  color: #00F0FF;
  animation: splash-glitch-1 3s infinite;
  clip-path: polygon(0 20%, 100% 20%, 100% 28%, 0 28%);
}

.splash__logo--zzz::after {
  color: #FF3B6B;
  animation: splash-glitch-2 2.5s infinite;
  clip-path: polygon(0 60%, 100% 60%, 100% 68%, 0 68%);
}

@keyframes splash-glitch-1 {
  0%, 90%, 100% { transform: translate(0); opacity: 0; }
  91% { transform: translate(-2px, 1px); opacity: 0.7; }
  93% { transform: translate(2px, -1px); opacity: 0.5; }
  95% { transform: translate(-1px, 0); opacity: 0.7; }
}

@keyframes splash-glitch-2 {
  0%, 88%, 100% { transform: translate(0); opacity: 0; }
  89% { transform: translate(2px, -1px); opacity: 0.6; }
  92% { transform: translate(-2px, 1px); opacity: 0.4; }
  94% { transform: translate(1px, 0); opacity: 0.6; }
}

/* 荧光边框内容框 */
.splash__content--zzz-frame {
  padding: 48px 40px;
  border-radius: 6px;
  box-shadow:
    0 0 0 1px rgba(255, 217, 61, 0.15),
    0 0 40px rgba(255, 217, 61, 0.06),
    inset 0 0 60px rgba(255, 217, 61, 0.02);
  backdrop-filter: blur(2px);
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

/* 全息透视网格 — 从中心向外的3D网格 */
.splash__ak-holo-grid {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200vw;
  height: 200vh;
  transform: translate(-50%, -50%) perspective(400px) rotateX(65deg);
  background-image:
    linear-gradient(rgba(200, 50, 63, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(200, 50, 63, 0.06) 1px, transparent 1px);
  background-size: 60px 60px;
  transform-origin: center center;
  animation: splash-holo-drift 12s linear infinite;
  pointer-events: none;
  mask-image: radial-gradient(ellipse 50% 50% at center, black 0%, transparent 70%);
  -webkit-mask-image: radial-gradient(ellipse 50% 50% at center, black 0%, transparent 70%);
}

@keyframes splash-holo-drift {
  0% { background-position: 0 0; }
  100% { background-position: 0 60px; }
}

/* 文件列表滚动虚影 */
.splash__ak-file-scroll {
  position: absolute;
  top: 0;
  left: 0;
  width: 200px;
  height: 100%;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: rgba(200, 50, 63, 0.08);
  line-height: 2.4;
  overflow: hidden;
  pointer-events: none;
  white-space: pre;
  animation: splash-file-up 15s linear infinite;
}

.splash__ak-file-scroll::before {
  content: 'ARCHIVE_0001.dat\A RECORD_0024.dat\A OPERATOR_LIST.csv\A MISSION_LOG.txt\A ARCHIVE_0002.dat\A CLASSIFIED.md\A TACTICAL_MAP.png\A PERSONNEL.db\A ARCHIVE_0003.dat\A EQUIPMENT.log\A STATUS_REPORT.doc\A ARCHIVE_0004.dat';
  white-space: pre;
}

@keyframes splash-file-up {
  0% { transform: translateY(0); }
  100% { transform: translateY(-50%); }
}

/* 双线战术角标内框 */
.splash__ak-corner-inner {
  position: absolute;
  width: 28px;
  height: 28px;
  border: 1px solid rgba(200, 50, 63, 0.15);
}

.splash__ak-corner-inner--tl { top: 28px; left: 28px; border-right: none; border-bottom: none; }
.splash__ak-corner-inner--tr { top: 28px; right: 28px; border-left: none; border-bottom: none; }
.splash__ak-corner-inner--bl { bottom: 28px; left: 28px; border-right: none; border-top: none; }
.splash__ak-corner-inner--br { bottom: 28px; right: 28px; border-left: none; border-top: none; }

/* AK 终端框 */
.splash__terminal--ak {
  border: 1px solid rgba(200, 50, 63, 0.2);
  border-left: 3px solid #C8323F;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(4px);
  padding: 16px 20px;
  position: relative;
}

.splash__terminal--ak::before {
  content: 'PRTS // RECORD';
  position: absolute;
  top: -10px;
  left: 16px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #C8323F;
  background: linear-gradient(135deg, #EAEDF0, #E0E4E8);
  padding: 0 6px;
}

/* AK 内容框 */
.splash__content--ak-frame {
  padding: 48px 40px;
  border: 1px solid rgba(200, 50, 63, 0.12);
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(6px);
  box-shadow: 0 8px 32px rgba(200, 50, 63, 0.06);
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

/* 主题切换按钮 — 与 HudTopBar 风格一致 */
.splash__theme {
  position: absolute;
  top: 24px;
  right: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  height: 32px;
  padding: 0 10px 0 8px;
  border: 1px solid;
  border-color: rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  color: inherit;
  clip-path: polygon(6px 0, 100% 0, 100% calc(100% - 6px), calc(100% - 6px) 100%, 0 100%, 0 6px);
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 200ms, border-color 200ms;
}

.splash--ak .splash__theme {
  border-color: rgba(200, 50, 63, 0.2);
  background: rgba(200, 50, 63, 0.04);
}

.splash__theme:hover {
  opacity: 1;
  border-color: var(--amber);
}

.splash__theme-track {
  position: relative;
  width: 34px;
  height: 18px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  clip-path: polygon(4px 0, 100% 0, 100% calc(100% - 4px), calc(100% - 4px) 100%, 0 100%, 0 4px);
  transition: background 400ms;
}

.splash--ak .splash__theme-track {
  background: rgba(200, 50, 63, 0.08);
  border-color: rgba(200, 50, 63, 0.15);
}

.splash__theme-knob {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 12px;
  height: 12px;
  background: #FFD93D;
  clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%);
  transition: transform 400ms cubic-bezier(0.4, 0, 0.2, 1), background 400ms;
}

.splash__theme-knob--ak {
  transform: translateX(16px);
  background: #C8323F;
}

.splash__theme-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  min-width: 12px;
  text-align: center;
}

.splash--zzz .splash__theme-label {
  color: #FFD93D;
}

.splash--ak .splash__theme-label {
  color: #C8323F;
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
