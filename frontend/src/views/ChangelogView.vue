<template>
  <PageShell title="更新日志" subtitle="UPDATE · 系统更新记录" active-key="changelog">
    <div v-if="nav.changelog.length" class="changelog">
      <article v-for="entry in nav.changelog" :key="entry.version" class="changelog__entry">
        <header class="changelog__header">
          <span class="changelog__version">VER {{ entry.version }}</span>
          <span class="changelog__date">{{ entry.date }}</span>
        </header>
        <ul class="changelog__list">
          <li v-for="(change, i) in entry.changes" :key="i" class="changelog__item">{{ change }}</li>
        </ul>
      </article>
    </div>
    <p v-else-if="nav.loaded" class="empty">暂无更新记录</p>
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from '@/components/common/PageShell.vue';
import { useNavStore } from '@/stores/navStore';

const nav = useNavStore();
</script>

<style scoped>
.changelog {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.changelog__entry {
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
}

.changelog__header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 10px;
}

.changelog__version {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-warn);
}

.changelog__date {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-muted);
}

.changelog__list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.changelog__item {
  font-size: 13px;
  color: var(--text-secondary);
  padding-left: 14px;
  position: relative;
}

.changelog__item::before {
  content: '▸';
  position: absolute;
  left: 0;
  color: var(--accent-primary);
}

.empty {
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
  padding: 32px 0;
}
</style>
