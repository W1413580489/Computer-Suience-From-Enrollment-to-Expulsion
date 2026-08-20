<template>
  <div class="hud-background" aria-hidden="true">
    <!-- 城市感光晕 -->
    <div class="hud-background__glow hud-background__glow--tl" />
    <div class="hud-background__glow hud-background__glow--br" />
    <!-- 克制的几何线条 — 城市视觉包装 -->
    <div class="hud-background__lines" />
    <!-- ZZZ 专属：青柠斜向警示条纹底纹（仅夜间显示） -->
    <div class="hud-background__stripes" />
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.hud-background {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

/* 城市光晕 — 克制，不喧宾夺主 */
.hud-background__glow {
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.5;
}

.hud-background__glow--tl {
  top: -200px;
  left: -160px;
  background: radial-gradient(circle, var(--amber-glow), transparent 70%);
}

.hud-background__glow--br {
  bottom: -240px;
  right: -180px;
  background: radial-gradient(circle, var(--neon-cyan-glow), transparent 70%);
  opacity: 0.3;
}

/* 几何线条 — 城市建筑感，非科技网格（颜色随主题切换） */
.hud-background__lines {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, transparent 0%, transparent 70%, var(--bg-glow-1) 100%),
    repeating-linear-gradient(
      90deg,
      transparent 0,
      transparent 200px,
      rgba(255, 255, 255, 0.012) 200px,
      rgba(255, 255, 255, 0.012) 201px
    );
  mask-image: radial-gradient(ellipse at center, black 40%, transparent 85%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 40%, transparent 85%);
}

/* ZZZ 斜向警示条纹 — zenless-ui 官网同款底纹，日间隐藏 */
.hud-background__stripes {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    -45deg,
    transparent 0,
    transparent 22px,
    rgba(201, 255, 11, 0.04) 22px,
    rgba(201, 255, 11, 0.04) 24px
  );
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 90%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 30%, transparent 90%);
}
[data-theme='ak'] .hud-background__stripes {
  display: none;
}
</style>
