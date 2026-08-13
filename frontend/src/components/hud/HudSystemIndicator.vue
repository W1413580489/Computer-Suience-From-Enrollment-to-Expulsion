<template>
  <div class="sys-indicator" role="status">
    <div class="sys-indicator__row">
      <PulseDot :status="status" :size="8" />
      <span class="sys-indicator__label">{{ label }}</span>
    </div>
    <div class="sys-indicator__bar">
      <span class="sys-indicator__bar-fill" />
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
  gap: 6px;
  padding: 12px 16px;
  background: var(--bg-panel-2);
  border: 1px solid var(--border-subtle);
  border-left: 3px solid var(--amber);
  clip-path: var(--clip-sm);
}

.sys-indicator__row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sys-indicator__label {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--success);
}

.sys-indicator__bar {
  width: 100%;
  height: 4px;
  background: var(--bg-panel-3);
  clip-path: var(--clip-sm);
  overflow: hidden;
}

.sys-indicator__bar-fill {
  display: block;
  height: 100%;
  width: 88%;
  background: linear-gradient(90deg, var(--amber), var(--neon-cyan));
  position: relative;
}

.sys-indicator__bar-fill::after {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(90deg, transparent 0, transparent 5px, rgba(0, 0, 0, 0.25) 5px, rgba(0, 0, 0, 0.25) 7px);
}

.sys-indicator__version {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 1px;
}
</style>
