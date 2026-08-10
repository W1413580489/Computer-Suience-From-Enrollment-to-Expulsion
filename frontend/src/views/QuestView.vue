<template>
  <div class="quest-root">
    <header class="quest-topbar">
      <button class="quest-topbar__back" @click="$router.push('/')">
        <NeonIcon name="back" :size="20" />
        <span>返回</span>
      </button>
      <span class="quest-topbar__title">🎮 新手任务</span>
      <span class="quest-topbar__ver">v1.0</span>
    </header>

    <!-- Login screen (first visit) -->
    <QuestLogin v-if="!progress.hasSeenIntro" @done="progress.hasSeenIntro = true" />

    <!-- Main quest hub -->
    <div v-else class="quest-body">
      <!-- Tab bar -->
      <nav class="quest-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="quest-tab"
          :class="{ 'quest-tab--active': activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
          <span v-if="tab.key === 'map'" class="quest-tab__badge">
            {{ progress.explored.length }}/9
          </span>
          <span v-if="tab.key === 'guide'" class="quest-tab__badge">
            {{ overallProgress }}%
          </span>
        </button>
      </nav>

      <!-- Tab content -->
      <div class="quest-page">
        <QuestMap v-if="activeTab === 'map'" />
        <QuestGuide v-if="activeTab === 'guide'" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import QuestLogin from '@/components/quest/QuestLogin.vue';
import QuestMap from '@/components/quest/QuestMap.vue';
import QuestGuide from '@/components/quest/QuestGuide.vue';
import { loadProgress } from '@/composables/useQuest';
import { questChapters } from '@/data/questData';

const progress = reactive(loadProgress());
const activeTab = ref<'map' | 'guide'>('map');

const tabs = [
  { key: 'map' as const, label: '🗺️ 大地图探索' },
  { key: 'guide' as const, label: '📖 攻略手册' },
];

const overallProgress = (() => {
  const all = questChapters.flatMap(c => c.sections.map(s => s.id));
  if (all.length === 0) return 0;
  const done = all.filter(id => progress.mainComplete.includes(id)).length;
  return Math.round((done / all.length) * 100);
})();
</script>

<style scoped>
.quest-root {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  overflow: hidden;
}

.quest-topbar {
  display: flex; align-items: center; gap: 12px;
  padding: 0 16px; height: var(--topbar-h);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}
.quest-topbar__back {
  display: flex; align-items: center; gap: 6px;
  font-size: 14px; color: var(--text-secondary);
  cursor: pointer; transition: color 150ms;
}
.quest-topbar__back:hover { color: var(--text-primary); }
.quest-topbar__title {
  flex: 1; font-size: 17px; font-weight: 600; color: var(--amber);
}
.quest-topbar__ver {
  font-family: var(--font-display);
  font-size: 11px; color: var(--text-muted);
}

.quest-body {
  flex: 1;
  display: flex; flex-direction: column;
  overflow: hidden;
}

.quest-tabs {
  display: flex;
  padding: 12px 16px 0;
  gap: 8px;
  flex-shrink: 0;
}
.quest-tab {
  flex: 1;
  padding: 10px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
  border-bottom: none;
  font-size: 14px; font-weight: 500; color: var(--text-secondary);
  cursor: pointer;
  transition: color 150ms, background 150ms;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
.quest-tab:hover { color: var(--text-primary); }
.quest-tab--active {
  color: var(--amber);
  background: var(--bg-primary);
  border-color: var(--amber);
  border-bottom: 2px solid var(--amber);
}
.quest-tab__badge {
  font-size: 11px; color: var(--text-muted);
  background: var(--bg-panel-3);
  border-radius: var(--radius-sm);
  padding: 1px 6px;
}

.quest-page {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}
</style>
