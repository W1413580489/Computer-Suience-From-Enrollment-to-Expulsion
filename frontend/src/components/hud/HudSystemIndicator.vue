<template>
  <div class="sys-indicator" role="status">
    <div class="sys-indicator__row">
      <PulseDot :status="status" :size="8" />
      <span class="sys-indicator__label">{{ label }}</span>
    </div>
    <span class="sys-indicator__version">{{ version }}</span>
  </div>
</template>

<script setup lang="ts">
import PulseDot from '@/components/common/PulseDot.vue';

withDefaults(defineProps<{ label?: string; version: string; status?: 'online' | 'maintenance' }>(), {
  label: 'SYSTEM ONLINE',
  status: 'online',
});
</script>

<style scoped>
.sys-indicator {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
  height: 64px;
  padding: 0 16px;
  background: var(--bg-panel-2);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}

.sys-indicator__row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sys-indicator__label {
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 2px;
  color: var(--accent-green);
}

.sys-indicator__version {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-muted);
}
</style>
