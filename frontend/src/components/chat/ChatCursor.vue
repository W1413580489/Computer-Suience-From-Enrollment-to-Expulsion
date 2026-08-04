<template>
  <span class="chat-cursor" aria-hidden="true" />
</template>

<script setup lang="ts">
</script>

<style scoped>
.chat-cursor {
  display: inline-block;
  width: 8px;
  height: 16px;
  margin-left: 2px;
  vertical-align: text-bottom;
  background: var(--accent-bright);
  animation: cursor-blink 0.9s steps(2) infinite;
}

@keyframes cursor-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
</style>
