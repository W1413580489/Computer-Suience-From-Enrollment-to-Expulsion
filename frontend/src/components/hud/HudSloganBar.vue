<template>
  <footer class="slogan-bar">
    <span class="slogan-bar__main">{{ main }}</span>
    <span class="slogan-bar__sub">{{ sub }}</span>
    <span class="slogan-bar__copy">© 2026 JNU·IST INFO SYSTEM</span>
  </footer>
</template>

<script setup lang="ts">
defineProps<{ main: string; sub: string }>();
</script>

<style scoped>
.slogan-bar {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  min-height: var(--slogan-h);
  background: rgba(10, 10, 10, 0.92);
  border-top: 2px solid var(--amber);
  position: relative;
  z-index: 1;
  padding: 8px;
}

.slogan-bar__main {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 500;
  letter-spacing: 6px;
  color: var(--amber);
  text-shadow: 0 0 14px var(--amber-glow);
}

.slogan-bar__sub {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 8px;
  color: var(--text-muted);
}

.slogan-bar__copy {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-muted);
  opacity: 0.7;
}

@media (max-width: 767px) {
  .slogan-bar {
    min-height: 64px;
  }
  .slogan-bar__main {
    font-size: 16px;
    letter-spacing: 3px;
  }
  .slogan-bar__sub {
    letter-spacing: 4px;
  }
}
</style>
