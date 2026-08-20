<template>
  <section class="data-section">
    <SectionHeader num="03" title="数据面板" en="DATA PANEL" />

    <!-- 已登录：年级里程碑三列网格 -->
    <div v-if="userStore.user && milestones" class="milestones">
      <div v-for="col in milestones.columns" :key="col.key" class="milestone-col" :class="`milestone-col--${col.key}`">
        <div class="milestone-col__head">
          <span class="milestone-col__title">{{ col.title }}</span>
          <span class="milestone-col__en">{{ col.en }}</span>
          <span class="milestone-col__count">{{ doneCount(col) }}/{{ col.items.length }}</span>
        </div>
        <ul class="milestone-list">
          <li v-for="item in col.items" :key="item.id" class="milestone-item">
            <button
              class="milestone-check"
              :class="{ 'milestone-check--on': isDone(item.id) }"
              role="checkbox"
              :aria-checked="isDone(item.id)"
              @click="toggle(item.id)"
            >
              <span class="milestone-check__box">{{ isDone(item.id) ? '✓' : '' }}</span>
              <span class="milestone-check__text" :class="{ 'milestone-check__text--done': isDone(item.id) }">
                {{ item.text }}
              </span>
            </button>
          </li>
        </ul>
      </div>
    </div>

    <!-- 游客/未登录：登录解锁占位 -->
    <div v-else class="milestones milestones--locked">
      <div class="milestone-locked">
        <div class="milestone-locked__icon">🔒</div>
        <div class="milestone-locked__title">登录以解锁个人里程碑</div>
        <div class="milestone-locked__sub">填写昵称与年级，获得属于你的大学进度清单</div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useUserStore } from '@/stores/userStore';
import { useThemeStore } from '@/stores/themeStore';
import { gradeMilestones } from '@/data/gradeContent';
import {
  loadMilestones,
  toggleMilestone,
  isChecked,
  type MilestoneProgress,
} from '@/composables/useMilestones';
import SectionHeader from './SectionHeader.vue';

const userStore = useUserStore();
const theme = useThemeStore();

// 里程碑进度（响应式，勾选即写 localStorage）
const progress = ref<MilestoneProgress>(loadMilestones());

// 当前年级对应的里程碑数据
const milestones = computed(() => {
  if (!userStore.user) return null;
  return gradeMilestones[userStore.user.grade] ?? null;
});

// 登录身份切换时重读进度（避免跨年级数据串）
watch(
  () => userStore.user?.grade,
  () => {
    progress.value = loadMilestones();
  },
);

function isDone(itemId: string): boolean {
  if (!userStore.user) return false;
  return isChecked(progress.value, userStore.user.grade, itemId);
}

function toggle(itemId: string) {
  if (!userStore.user) return;
  progress.value = toggleMilestone(progress.value, userStore.user.grade, itemId);
}

function doneCount(col: { items: { id: string }[] }): number {
  if (!userStore.user) return 0;
  return col.items.filter((it) => isChecked(progress.value, userStore.user.grade, it.id)).length;
}
</script>

<style scoped>
.data-section {
  padding: 80px 32px 96px;
  max-width: 1120px;
  margin: 0 auto;
  width: 100%;
}

/* ---- 里程碑三列网格 ---- */
.milestones {
  display: grid;
  grid-template-columns: 1fr 1fr 1.1fr;
  gap: 14px;
}

.milestone-col {
  background: var(--bg-panel-2);
  padding: 18px 20px;
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
  border-bottom: 2px solid var(--amber);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.milestone-col--achieve {
  border-bottom-color: var(--neon-cyan);
}

.milestone-col--hidden {
  border-bottom-color: var(--neon-magenta);
}

.milestone-col__head {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}

.milestone-col__title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 900;
  color: var(--text-primary);
}

.milestone-col--achieve .milestone-col__title { color: var(--neon-cyan); }
.milestone-col--hidden .milestone-col__title { color: var(--neon-magenta); }

.milestone-col__en {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 1.5px;
  color: var(--text-muted);
}

.milestone-col__count {
  margin-left: auto;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  color: var(--amber);
}

.milestone-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.milestone-item {
  display: flex;
}

.milestone-check {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 0;
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  color: var(--text-primary);
}

.milestone-check__box {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  font-size: 12px;
  font-weight: 900;
  color: var(--ink);
  background: var(--bg-panel-3);
  border: 1px solid var(--border-subtle);
  clip-path: polygon(0 0, 100% 0, 100% 0, 100% 100%, 4px 100%, 0 calc(100% - 4px));
  transition: background 160ms, border-color 160ms;
}

.milestone-check--on .milestone-check__box {
  background: var(--amber);
  border-color: var(--amber);
}

.milestone-check__text {
  font-size: 13.5px;
  line-height: 1.4;
  color: var(--text-secondary);
  transition: color 160ms, opacity 160ms;
}

.milestone-check__text--done {
  color: var(--text-muted);
  opacity: 0.6;
  text-decoration: line-through;
}

.milestone-check:hover .milestone-check__box {
  border-color: var(--amber);
}

/* ---- 游客占位 ---- */
.milestones--locked {
  grid-template-columns: 1fr;
}

.milestone-locked {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 48px 24px;
  background: var(--bg-panel-2);
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
  border-bottom: 2px solid var(--amber);
  text-align: center;
}

.milestone-locked__icon {
  font-size: 32px;
}

.milestone-locked__title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 900;
  color: var(--amber);
}

.milestone-locked__sub {
  font-size: 13px;
  color: var(--text-muted);
}

@media (max-width: 900px) {
  .milestones {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 767px) {
  .data-section {
    padding: 48px 16px 64px;
  }
}
</style>
