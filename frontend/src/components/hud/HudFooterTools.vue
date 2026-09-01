<template>
  <nav class="ext-system" aria-label="外部系统">
    <span class="ext-system__label">EXTERNAL SYSTEM</span>
    <div class="ext-system__list">
      <button
        v-for="item in items"
        :key="item.label"
        class="ext-system__item"
        @click="emit('onItemClick', item)"
      >
        <span class="ext-system__dot" />
        <span>{{ item.label }}</span>
      </button>
    </div>
    <div class="ext-system__icp">
      <a
        href="https://beian.mps.gov.cn/#/query/webSearch?code=44011302005840"
        target="_blank"
        rel="noreferrer"
        class="ext-system__icp-link"
      >
        <img
          :src="beianIcon"
          alt="公安备案图标"
          class="ext-system__beian-icon"
        />
        粤公网安备44011302005840号
      </a>
      <a
        href="https://beian.miit.gov.cn"
        target="_blank"
        rel="noopener noreferrer"
        class="ext-system__icp-link"
      >
        闽ICP备2026031193号-1
      </a>
    </div>
  </nav>
</template>

<script setup lang="ts">
import type { FooterToolItem } from '@/types/nav';
import beianIcon from '@/assets/images/beian_icon.png';

defineProps<{ items: FooterToolItem[] }>();
const emit = defineEmits<{ onItemClick: [item: FooterToolItem] }>();
</script>

<style scoped>
.ext-system {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px 24px;
  background: var(--bg-panel);
  border-top: 1px solid var(--border-subtle);
}

.ext-system__label {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 3px;
  color: var(--text-muted);
  text-transform: uppercase;
}

.ext-system__list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 24px;
}

.ext-system__item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 15.6px;
  color: var(--text-secondary);
  white-space: nowrap;
  transition: color 200ms;
}

.ext-system__item:hover {
  color: var(--amber);
}

.ext-system__dot {
  width: 5px;
  height: 5px;
  background: currentColor;
  opacity: 0.6;
  transition: opacity 200ms;
}

.ext-system__item:hover .ext-system__dot {
  opacity: 1;
}

.ext-system__icp {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  margin-top: 8px;
}

.ext-system__icp-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 14.4px;
  color: var(--text-muted);
  text-decoration: none;
  transition: color 200ms;
}

.ext-system__beian-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.ext-system__icp-link:hover {
  color: var(--amber);
}

@media (max-width: 767px) {
  .ext-system {
    padding: 12px 16px;
    gap: 8px;
  }

  .ext-system__list {
    gap: 16px;
  }

  .ext-system__item {
    font-size: 14.4px;
  }
}
</style>
