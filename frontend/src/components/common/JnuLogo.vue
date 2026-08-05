<template>
  <svg :width="size" :height="size" viewBox="0 0 40 40" class="jnu-logo" aria-label="JNU Logo">
    <rect x="2" y="2" width="36" height="36" rx="8" fill="none" stroke="var(--accent-primary)" stroke-width="2" />
    <text
      x="20"
      y="26"
      text-anchor="middle"
      font-family="Orbitron, sans-serif"
      font-size="12"
      font-weight="700"
      fill="var(--accent-bright)"
    >JNU</text>
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ size?: number }>(), { size: 32 });
</script>

<style scoped>
.jnu-logo {
  flex-shrink: 0;
  filter: drop-shadow(0 0 6px var(--accent-strong));
}
</style>
