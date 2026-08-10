<template>
  <div class="guide-root">
    <!-- Chapter tabs -->
    <nav class="guide-nav">
      <button
        v-for="ch in chapters"
        :key="ch.id"
        class="guide-nav__tab"
        :class="{ 'guide-nav__tab--active': activeChapter === ch.id }"
        @click="activeChapter = ch.id"
      >
        {{ ch.title }}
        <span v-if="chapterProgress(ch.id) === 100" class="guide-nav__done">✓</span>
      </button>
    </nav>

    <!-- Chapter content -->
    <div class="guide-content" :key="activeChapter">
      <h2 class="guide-content__title">{{ currentChapter?.title }}</h2>
      <p class="guide-content__progress">
        已完成 {{ chapterProgress(activeChapter) }}%
      </p>

      <div
        v-for="sec in currentChapter?.sections ?? []"
        :key="sec.id"
        class="guide-card"
        :class="{ 'guide-card--done': isDone(sec.id), 'guide-card--open': openSection === sec.id }"
      >
        <button class="guide-card__header" @click="toggleSection(sec.id)">
          <span class="guide-card__status">{{ isDone(sec.id) ? '✅' : '⬜' }}</span>
          <span class="guide-card__title">{{ sec.title }}</span>
          <span class="guide-card__arrow" :class="{ 'guide-card__arrow--expanded': openSection === sec.id }">▸</span>
        </button>

        <transition name="expand">
          <div v-if="openSection === sec.id" class="guide-card__body">
            <p class="guide-card__text">{{ sec.content }}</p>
            <button
              class="guide-card__done-btn"
              :class="{ 'guide-card__done-btn--checked': isDone(sec.id) }"
              @click.stop="toggleDone(sec.id)"
            >
              {{ isDone(sec.id) ? '✅ 已完成' : '✔ 标记完成' }}
            </button>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { questChapters } from '@/data/questData';
import { loadProgress, saveProgress } from '@/composables/useQuest';

const chapters = questChapters;
const activeChapter = ref(chapters[0].id);
const openSection = ref<string | null>(null);
const progress = reactive(loadProgress());

const currentChapter = computed(() => chapters.find(c => c.id === activeChapter.value));

function isDone(id: string) { return progress.mainComplete.includes(id); }
function toggleDone(id: string) {
  const idx = progress.mainComplete.indexOf(id);
  if (idx >= 0) progress.mainComplete.splice(idx, 1);
  else progress.mainComplete.push(id);
  saveProgress({ ...progress });
}
function toggleSection(id: string) {
  openSection.value = openSection.value === id ? null : id;
}
function chapterProgress(chapterId: string) {
  const ch = chapters.find(c => c.id === chapterId);
  if (!ch || ch.sections.length === 0) return 0;
  const done = ch.sections.filter(s => isDone(s.id)).length;
  return Math.round((done / ch.sections.length) * 100);
}
</script>

<style scoped>
.guide-root {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.guide-nav {
  display: flex;
  gap: 0;
  overflow-x: auto;
  padding: 0 16px;
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
  -webkit-overflow-scrolling: touch;
}
.guide-nav::-webkit-scrollbar { height: 0; }

.guide-nav__tab {
  flex-shrink: 0;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: color 150ms, border-color 150ms;
  display: flex; align-items: center; gap: 6px;
  white-space: nowrap;
}
.guide-nav__tab:hover { color: var(--text-primary); }
.guide-nav__tab--active {
  color: var(--amber);
  border-bottom-color: var(--amber);
}
.guide-nav__done { color: var(--success); font-size: 12px; }

.guide-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px 20px;
  -webkit-overflow-scrolling: touch;
}
.guide-content__title {
  font-size: 24px; font-weight: 700; color: var(--amber); margin-bottom: 6px;
}
.guide-content__progress {
  font-size: 12px; color: var(--text-muted); margin-bottom: 20px;
}

.guide-card {
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  margin-bottom: 10px;
  transition: border-color 200ms;
}
.guide-card--done { border-color: var(--success-border); }
.guide-card--open { border-color: var(--border-glow); }

.guide-card__header {
  display: flex; align-items: center; gap: 10px;
  width: 100%; padding: 14px 16px;
  cursor: pointer; text-align: left;
  transition: background 150ms;
}
.guide-card__header:hover { background: var(--accent-soft); }

.guide-card__status { font-size: 16px; flex-shrink: 0; }
.guide-card__title { flex: 1; font-size: 15px; font-weight: 500; }
.guide-card__arrow {
  font-size: 14px; color: var(--text-muted);
  transition: transform 200ms;
}
.guide-card__arrow--expanded { transform: rotate(90deg); }

.guide-card__body { padding: 0 16px 16px; }
.guide-card__text {
  font-size: 14px; color: var(--text-secondary); line-height: 1.8;
  white-space: pre-wrap; margin-bottom: 14px;
}
.guide-card__done-btn {
  padding: 6px 14px;
  font-size: 12px; color: var(--text-muted);
  background: var(--bg-panel-3);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: color 150ms, border-color 150ms;
}
.guide-card__done-btn:hover { color: var(--success); border-color: var(--success-border); }
.guide-card__done-btn--checked { color: var(--success); border-color: var(--success-border); }

/* expand transition */
.expand-enter-active { transition: max-height .25s ease, opacity .2s ease; overflow: hidden; }
.expand-leave-active { transition: max-height .2s ease, opacity .15s ease; overflow: hidden; }
.expand-enter-from, .expand-leave-to { max-height: 0; opacity: 0; }
.expand-enter-to, .expand-leave-from { max-height: 600px; opacity: 1; }
</style>
