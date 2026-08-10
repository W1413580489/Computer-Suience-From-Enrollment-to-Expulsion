<template>
  <div class="splash-root">
    <div class="splash-center">
      <!-- Decorative rings -->
      <div class="splash-rings">
        <div class="splash-ring splash-ring--outer" />
        <div class="splash-ring splash-ring--mid" />
        <div class="splash-ring splash-ring--inner" />
      </div>

      <!-- Content -->
      <div class="splash-content">
        <span class="splash-badge">XKZ · AGENT SYSTEM</span>
        <h1 class="splash-title">暨南大学番禺校区</h1>
        <p class="splash-sub">新生入学攻略指南</p>

        <div class="splash-divider">
          <span class="splash-divider__line" />
          <span class="splash-divider__dot" />
          <span class="splash-divider__line" />
        </div>

        <p class="splash-desc">
          装备清单 · 技能加点 · NPC 任务 · 主线攻略 · 大地图探索 · 道具采购
        </p>

        <button class="splash-btn" @click="$emit('done')">
          <span class="splash-btn__text">≡ 进入新手村 ≡</span>
          <span class="splash-btn__glow" />
        </button>

        <p class="splash-ver">v2.0 · 新生入学攻略指南</p>
      </div>
    </div>

    <!-- Corner decorations -->
    <div class="splash-corner splash-corner--tl" />
    <div class="splash-corner splash-corner--tr" />
    <div class="splash-corner splash-corner--bl" />
    <div class="splash-corner splash-corner--br" />
  </div>
</template>

<script setup lang="ts">
defineEmits<{ done: [] }>();
</script>

<style scoped>
.splash-root {
  height: 100vh;
  height: 100dvh;
  display: flex; align-items: center; justify-content: center;
  background: var(--bg-primary);
  position: relative;
  overflow: hidden;
}

/* ---- Animated rings ---- */
.splash-center {
  position: relative;
  width: clamp(280px, 60vw, 420px);
  height: clamp(280px, 60vw, 420px);
  display: flex; align-items: center; justify-content: center;
}
.splash-rings {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
}
.splash-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid;
}
.splash-ring--outer {
  width: 100%; height: 100%;
  border-color: var(--border-subtle);
  animation: ring-spin 20s linear infinite;
}
.splash-ring--mid {
  width: 75%; height: 75%;
  border-color: var(--amber-glow);
  animation: ring-spin 15s linear infinite reverse;
}
.splash-ring--inner {
  width: 50%; height: 50%;
  border-color: var(--border-subtle);
  border-style: dashed;
  border-width: .5px;
  animation: ring-spin 10s linear infinite;
}
@keyframes ring-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ---- Content ---- */
.splash-content {
  position: relative; z-index: 2;
  text-align: center;
  padding: clamp(20px, 4vw, 32px);
}
.splash-badge {
  display: inline-block;
  font-family: var(--font-display);
  font-size: clamp(10px, 1.5vw, 11px);
  letter-spacing: 3px;
  color: var(--text-muted);
  margin-bottom: 20px;
}
.splash-title {
  font-size: clamp(22px, 4vw, 30px);
  font-weight: 700;
  color: var(--amber);
  margin-bottom: 6px;
}
.splash-sub {
  font-size: clamp(14px, 2vw, 16px);
  color: var(--text-secondary);
  font-weight: 500;
  margin-bottom: 24px;
}

.splash-divider {
  display: flex; align-items: center; justify-content: center;
  gap: 12px; margin-bottom: 20px;
}
.splash-divider__line {
  width: clamp(30px, 6vw, 50px); height: 1px;
  background: var(--amber-glow);
}
.splash-divider__dot {
  width: 4px; height: 4px; border-radius: 50%;
  background: var(--amber);
}

.splash-desc {
  font-size: clamp(11px, 1.8vw, 13px);
  color: var(--text-muted);
  line-height: 1.8;
  margin-bottom: 32px;
}

/* ---- Button ---- */
.splash-btn {
  position: relative;
  padding: clamp(12px, 2vw, 16px) clamp(28px, 5vw, 48px);
  background: var(--amber);
  color: var(--on-amber);
  font-size: clamp(15px, 2.5vw, 18px);
  font-weight: 700;
  border-radius: 4px;
  cursor: pointer;
  letter-spacing: 2px;
  overflow: hidden;
  transition: transform 200ms, box-shadow 200ms;
  box-shadow: 0 0 20px var(--amber-glow);
}
.splash-btn:hover {
  transform: scale(1.03);
  box-shadow: 0 0 30px var(--amber-glow), 0 0 60px var(--amber-glow);
}
.splash-btn:active { transform: scale(.97); }
.splash-btn__text { position: relative; z-index: 2; }
.splash-btn__glow {
  position: absolute; inset: 0;
  background: radial-gradient(circle at center, rgba(255,255,255,.2) 0%, transparent 60%);
  animation: btn-pulse 2s ease-in-out infinite;
}
@keyframes btn-pulse {
  0%, 100% { opacity: .3; }
  50% { opacity: .7; }
}

.splash-ver {
  margin-top: 24px;
  font-family: var(--font-display);
  font-size: clamp(10px, 1.5vw, 11px);
  color: var(--text-muted);
  opacity: .4;
  letter-spacing: 2px;
}

/* ---- Corner decor ---- */
.splash-corner {
  position: absolute;
  width: clamp(60px, 10vw, 100px);
  height: clamp(60px, 10vw, 100px);
  border: 1px solid var(--border-subtle);
  opacity: .15;
}
.splash-corner--tl { top: -20px; left: -20px; border-right: none; border-bottom: none; }
.splash-corner--tr { top: -20px; right: -20px; border-left: none; border-bottom: none; }
.splash-corner--bl { bottom: -20px; left: -20px; border-right: none; border-top: none; }
.splash-corner--br { bottom: -20px; right: -20px; border-left: none; border-top: none; }
</style>
