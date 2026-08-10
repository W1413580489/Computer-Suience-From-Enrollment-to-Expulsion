<template>
  <div class="quest-root">
    <header class="quest-topbar">
      <button class="quest-topbar__back" @click="$router.push('/')">
        <NeonIcon name="back" :size="20" />
        <span class="quest-topbar__back-label">返回</span>
      </button>
      <span class="quest-topbar__title">🎮 新手任务</span>
      <span class="quest-topbar__ver">v1.0</span>
    </header>

    <!-- Login screen (first visit) -->
    <QuestLogin v-if="!progress.hasSeenIntro" @done="onLoginDone" />

    <!-- Main quest hub -->
    <div v-else class="quest-body">
      <!-- Global progress bar -->
      <div class="quest-progress-bar" v-if="totalProgress < 100">
        <div class="quest-progress-bar__segments">
          <div
            class="quest-progress-bar__seg"
            :style="{ width: segWidth(loginDone ? 3 : 0, 3) }"
            :class="{ done: loginDone }"
          />
          <div
            class="quest-progress-bar__seg"
            :style="{ width: segWidth(exploreDone, 9) }"
            :class="{ done: exploreDone >= 3 }"
          />
          <div
            class="quest-progress-bar__seg"
            :style="{ width: segWidth(studyDone, totalSections) }"
            :class="{ done: studyDone >= 3 }"
          />
        </div>
        <div class="quest-progress-bar__labels">
          <span :class="{ done: loginDone }">👤 登录</span>
          <span :class="{ done: exploreDone >= 3 }">🗺️ 探索 {{ exploreDone }}/9</span>
          <span :class="{ done: studyDone >= 3 }">📖 研读 {{ studyDone }}/{{ totalSections }}</span>
        </div>
      </div>

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
          <span v-if="tab.key === 'map'" class="quest-tab__badge">{{ exploreDone }}/9</span>
          <span v-if="tab.key === 'guide'" class="quest-tab__badge">{{ studyDone }}/{{ totalSections }}</span>
        </button>
      </nav>

      <!-- Tab content -->
      <div class="quest-page">
        <QuestMap v-if="activeTab === 'map'" :show-guide-overlay="showMapGuide" @dismiss-guide="showMapGuide = false" />
        <QuestGuide v-if="activeTab === 'guide'" @all-complete="onGuideComplete" />
      </div>
    </div>

    <!-- Celebration toast -->
    <Transition name="toast">
      <div v-if="showCelebrate" class="celebrate-toast" @click="showCelebrate = false">
        <div class="celebrate-toast__content">
          <span class="celebrate-toast__icon">🎉</span>
          <span class="celebrate-toast__text">{{ celebrateMsg }}</span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import QuestLogin from '@/components/quest/QuestLogin.vue';
import QuestMap from '@/components/quest/QuestMap.vue';
import QuestGuide from '@/components/quest/QuestGuide.vue';
import { loadProgress, saveProgress } from '@/composables/useQuest';
import { questChapters } from '@/data/questData';

const progress = reactive(loadProgress());
const activeTab = ref<'map' | 'guide'>('map');
const showMapGuide = ref(true);
const showCelebrate = ref(false);
const celebrateMsg = ref('');

const tabs = [
  { key: 'map' as const, label: '🗺️ 大地图探索' },
  { key: 'guide' as const, label: '📖 攻略手册' },
];

const loginDone = computed(() => progress.hasSeenIntro && progress.equipment.length >= 1);
const exploreDone = computed(() => progress.explored.length);
const totalSections = computed(() => questChapters.flatMap(c => c.sections).length);
const studyDone = computed(() => progress.mainComplete.filter(id =>
  questChapters.flatMap(c => c.sections).some(s => s.id === id)
).length);

const totalProgress = computed(() => {
  const total = 3 + 9 + totalSections.value;
  const done = (loginDone.value ? 3 : progress.equipment.length) + exploreDone.value + studyDone.value;
  return Math.min(100, Math.round((done / total) * 100));
});

function segWidth(done: number, total: number) {
  if (total === 0) return '0%';
  return Math.round((done / total) * 100) + '%';
}

function onLoginDone() {
  progress.hasSeenIntro = true;
  saveProgress({ ...progress });
  showCelebrate.value = true;
  celebrateMsg.value = '角色创建成功！欢迎来到新手村 🎮';
  activeTab.value = 'map';
  showMapGuide.value = true;
  setTimeout(() => { showCelebrate.value = false; }, 3000);
}

function onGuideComplete() {
  showCelebrate.value = true;
  celebrateMsg.value = '🎊 全攻略阅读完成！你已经是一名合格的 JNU 新生了！';
  setTimeout(() => { showCelebrate.value = false; }, 4000);
}
</script>

<style scoped>
.quest-root {
  height: 100vh;
  height: 100dvh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  overflow: hidden;
}

/* ---- Topbar ---- */
.quest-topbar {
  display: flex; align-items: center; gap: 12px;
  padding: 0 clamp(12px, 2vw, 16px);
  height: var(--topbar-h);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}
.quest-topbar__back {
  display: flex; align-items: center; gap: 6px;
  font-size: clamp(13px, 2vw, 14px); color: var(--text-secondary);
  cursor: pointer; transition: color 150ms;
}
.quest-topbar__back:hover { color: var(--text-primary); }
.quest-topbar__title {
  flex: 1; font-size: clamp(15px, 2.5vw, 17px); font-weight: 600; color: var(--amber);
}
.quest-topbar__ver {
  font-family: var(--font-display);
  font-size: clamp(10px, 1.5vw, 11px); color: var(--text-muted);
}

/* ---- Progress Bar ---- */
.quest-progress-bar {
  flex-shrink: 0;
  padding: clamp(6px, 1.5vw, 10px) clamp(12px, 2vw, 16px);
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-panel);
}
.quest-progress-bar__segments {
  display: flex; gap: 4px; height: 6px;
  border-radius: 3px; overflow: hidden;
  background: var(--bg-panel-3);
  margin-bottom: 6px;
}
.quest-progress-bar__seg {
  height: 100%; background: var(--border-subtle);
  transition: width .4s ease, background .3s;
}
.quest-progress-bar__seg.done { background: var(--amber); }
.quest-progress-bar__labels {
  display: flex; justify-content: space-between;
  font-size: clamp(10px, 1.5vw, 11px);
  color: var(--text-muted);
}
.quest-progress-bar__labels span.done { color: var(--success); }

/* ---- Tab bar ---- */
.quest-body {
  flex: 1;
  display: flex; flex-direction: column;
  overflow: hidden;
}
.quest-tabs {
  display: flex;
  padding: clamp(8px, 1.5vw, 12px) clamp(12px, 2vw, 16px) 0;
  gap: 8px;
  flex-shrink: 0;
}
.quest-tab {
  flex: 1;
  padding: clamp(8px, 1.5vw, 10px);
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
  border-bottom: none;
  font-size: clamp(13px, 2vw, 14px); font-weight: 500; color: var(--text-secondary);
  cursor: pointer;
  transition: color 150ms, background 150ms;
  display: flex; align-items: center; justify-content: center; gap: clamp(4px, 1vw, 8px);
}
.quest-tab:hover { color: var(--text-primary); }
.quest-tab--active {
  color: var(--amber);
  background: var(--bg-primary);
  border-color: var(--amber);
  border-bottom: 2px solid var(--amber);
}
.quest-tab__badge {
  font-size: clamp(10px, 1.5vw, 11px); color: var(--text-muted);
  background: var(--bg-panel-3);
  border-radius: var(--radius-sm);
  padding: 1px 6px;
}

.quest-page {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* ---- Celebration Toast ---- */
.celebrate-toast {
  position: fixed; bottom: clamp(80px, 15vh, 120px);
  left: 50%; transform: translateX(-50%);
  z-index: 200;
  cursor: pointer;
  animation: toast-bounce .5s ease-out;
}
.celebrate-toast__content {
  background: var(--bg-panel);
  border: 1px solid var(--amber);
  border-radius: var(--radius-lg);
  padding: clamp(10px, 2vw, 14px) clamp(18px, 3vw, 24px);
  display: flex; align-items: center; gap: 10px;
  box-shadow: 0 4px 24px var(--amber-glow);
  white-space: nowrap;
}
.celebrate-toast__icon { font-size: clamp(18px, 3vw, 22px); }
.celebrate-toast__text {
  font-size: clamp(13px, 2vw, 15px); font-weight: 600; color: var(--amber);
}

@keyframes toast-bounce {
  0% { opacity: 0; transform: translateX(-50%) translateY(20px); }
  60% { transform: translateX(-50%) translateY(-4px); }
  100% { opacity: 1; transform: translateX(-50%) translateY(0); }
}
.toast-enter-active { animation: toast-bounce .5s ease-out; }
.toast-leave-active { transition: opacity .3s ease; }
.toast-leave-to { opacity: 0; }

/* ---- Mobile ---- */
@media (max-width: 640px) {
  .quest-topbar__back-label { display: none; }
}
</style>
