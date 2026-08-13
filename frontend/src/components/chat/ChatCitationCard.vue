<template>
  <button class="citation" :title="citation.title" @click="open">
    <span class="citation__badge">[来源{{ citation.id }}]</span>
    <span class="citation__body">
      <span class="citation__title">{{ citation.title }}</span>
      <span v-if="citation.excerpt" class="citation__excerpt">{{ citation.excerpt }}</span>
    </span>
    <NeonIcon name="external" :size="14" class="citation__icon" />
  </button>
</template>

<script setup lang="ts">
import NeonIcon from '@/components/common/NeonIcon.vue';
import { openExternal } from '@/composables/useViewport';
import type { Citation } from '@/types/nav';

const props = defineProps<{ citation: Citation }>();

function open() {
  if (props.citation.url) openExternal(props.citation.url);
}
</script>

<style scoped>
.citation {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 10px;
  background: var(--bg-panel-2);
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-sm);
  color: var(--text-primary);
  text-align: left;
  transition: border-color 200ms;
}

.citation:hover {
  border-color: var(--accent-primary);
}

.citation__badge {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--warning);
  flex-shrink: 0;
}

.citation__body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.citation__title {
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.citation__excerpt {
  font-size: 11px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.citation__icon {
  color: var(--text-muted);
  flex-shrink: 0;
}
</style>
