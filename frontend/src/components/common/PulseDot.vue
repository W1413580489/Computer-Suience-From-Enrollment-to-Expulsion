<template>
  <span class="pulse-dot" :class="`pulse-dot--${status}`" :style="{ width: size + 'px', height: size + 'px' }" />
</template>

<script setup lang="ts">
withDefaults(defineProps<{ status?: 'online' | 'maintenance'; size?: number }>(), {
  status: 'online',
  size: 8,
});
</script>

<style scoped>
.pulse-dot {
  display: inline-block;
  border-radius: 50%;
  flex-shrink: 0;
}
.pulse-dot--online {
  background: var(--accent-green);
  box-shadow: 0 0 6px var(--accent-green);
  animation: pulse-green 2s infinite;
}
.pulse-dot--maintenance {
  background: var(--accent-warn);
  box-shadow: 0 0 6px var(--accent-warn);
  animation: pulse-orange 2s infinite;
}
@keyframes pulse-green {
  0%, 100% { opacity: 1; box-shadow: 0 0 4px var(--accent-green); }
  50% { opacity: 0.5; box-shadow: 0 0 10px var(--accent-green); }
}
@keyframes pulse-orange {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
