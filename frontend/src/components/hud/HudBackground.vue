<template>
  <div class="hud-background" aria-hidden="true">
    <div class="hud-background__grid" />
    <div class="hud-background__glow hud-background__glow--tl" />
    <div class="hud-background__glow hud-background__glow--br" />
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

.hud-background__grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(55, 138, 221, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(55, 138, 221, 0.05) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 75%);
}

.hud-background__glow {
  position: absolute;
  width: 480px;
  height: 480px;
  border-radius: 50%;
  filter: blur(120px);
}

.hud-background__glow--tl {
  top: -160px;
  left: -120px;
  background: rgba(55, 138, 221, 0.12);
}

.hud-background__glow--br {
  bottom: -200px;
  right: -140px;
  background: rgba(239, 159, 39, 0.06);
}
</style>
