<template>
  <div class="guide-root">
    <!-- Chapter tabs (sticky) -->
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
      <div class="guide-content__progress-row">
        <p class="guide-content__progress">
          已完成 {{ chapterProgress(activeChapter) }}%
        </p>
        <button
          v-if="chapterProgress(activeChapter) > 0 && chapterProgress(activeChapter) < 100"
          class="guide-content__mark-all"
          @click="markChapterDone"
        >全部标记完成</button>
      </div>

      <div
        v-for="(sec, idx) in currentChapter?.sections ?? []"
        :key="sec.id"
        class="guide-card"
        :class="{ 'guide-card--done': isDone(sec.id), 'guide-card--open': openSection === sec.id }"
      >
        <button class="guide-card__header" @click="toggleSection(sec.id)">
          <span class="guide-card__status">{{ isDone(sec.id) ? '✅' : '⬜' }}</span>
          <span class="guide-card__title">{{ sec.title }}</span>
          <span class="guide-card__arrow" :class="{ 'guide-card__arrow--expanded': openSection === sec.id }">▸</span>
        </button>

        <Transition name="expand">
          <div v-if="openSection === sec.id" class="guide-card__body">
            <p class="guide-card__text">{{ sec.content }}</p>
            <div class="guide-card__footer">
              <button
                class="guide-card__done-btn"
                :class="{ done: isDone(sec.id) }"
                @click.stop="toggleDone(sec.id)"
              >
                {{ isDone(sec.id) ? '✅ 已完成' : '✔ 标记完成' }}
              </button>
              <button
                v-if="nextSection(sec.id)"
                class="guide-card__next-btn"
                @click.stop="goNext(sec.id)"
              >
                下一节：{{ nextSection(sec.id)?.title }} →
              </button>
            </div>
          </div>
        </Transition>
      </div>

      <!-- Chapter completion celebration -->
      <div v-if="chapterProgress(activeChapter) === 100" class="guide-chapter-done">
        <span class="guide-chapter-done__icon">🎉</span>
        <p>本章全部完成！{{ chapterDoneMsg }}</p>
        <button v-if="nextChapter" class="guide-chapter-done__next" @click="activeChapter = nextChapter.id">
          进入下一章：{{ nextChapter.title }} →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { questChapters } from '@/data/questData';
import { loadProgress, saveProgress } from '@/composables/useQuest';

const emit = defineEmits<{ allComplete: [] }>();

const chapters = questChapters;
const activeChapter = ref(chapters[0].id);
const openSection = ref<string | null>(null);
const progress = reactive(loadProgress());

const currentChapter = computed(() => chapters.find(c => c.id === activeChapter.value));

const nextChapter = computed(() => {
  const idx = chapters.findIndex(c => c.id === activeChapter.value);
  if (idx >= 0 && idx < chapters.length - 1) return chapters[idx + 1];
  return null;
});

const chapterDoneMsgs: Record<string, string> = {
  login: '装备已备齐、技能已分配，你已准备好进入大学冒险！',
  mainline: '主线任务全掌握，选课上课考试都不在话下！',
  sidequest: '支线剧情了解完毕，大学不止于课本！',
  items: '道具攻略已读，校园生活必备工具了然于心！',
  extra: '补缺篇完成，大学新生最后一块拼图就位！',
};

const chapterDoneMsg = computed(() => chapterDoneMsgs[activeChapter.value] ?? '继续加油！');

function isDone(id: string) { return progress.mainComplete.includes(id); }

function toggleDone(id: string) {
  const idx = progress.mainComplete.indexOf(id);
  if (idx >= 0) progress.mainComplete.splice(idx, 1);
  else progress.mainComplete.push(id);
  saveProgress({ ...progress });
  checkAllComplete();
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

function nextSection(currentId: string) {
  const ch = currentChapter.value;
  if (!ch) return null;
  const idx = ch.sections.findIndex(s => s.id === currentId);
  if (idx < 0 || idx >= ch.sections.length - 1) return null;
  return ch.sections[idx + 1];
}

function goNext(currentId: string) {
  const next = nextSection(currentId);
  if (next) {
    openSection.value = next.id;
  }
}

function markChapterDone() {
  const ch = currentChapter.value;
  if (!ch) return;
  for (const sec of ch.sections) {
    if (!isDone(sec.id)) {
      progress.mainComplete.push(sec.id);
    }
  }
  saveProgress({ ...progress });
  checkAllComplete();
}

function checkAllComplete() {
  const all = chapters.flatMap(c => c.sections);
  if (all.every(s => isDone(s.id))) {
    emit('allComplete');
  }
}
</script>

<style scoped>
.guide-root {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* ---- Chapter Nav (sticky) ---- */
.guide-nav {
  display: flex;
  gap: 0;
  overflow-x: auto;
  padding: 0 clamp(12px, 2vw, 16px);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
  position: sticky;
  top: 0;
  background: var(--bg-primary);
  z-index: 10;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.guide-nav::-webkit-scrollbar { height: 0; }

.guide-nav__tab {
  flex-shrink: 0;
  padding: clamp(10px, 1.5vw, 12px) clamp(10px, 2vw, 16px);
  font-size: clamp(12px, 2vw, 14px);
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

/* ---- Content ---- */
.guide-content {
  flex: 1;
  overflow-y: auto;
  padding: clamp(16px, 3vw, 24px) clamp(14px, 2.5vw, 20px);
  -webkit-overflow-scrolling: touch;
}
.guide-content__title {
  font-size: clamp(20px, 3.5vw, 24px); font-weight: 700; color: var(--amber); margin-bottom: 6px;
}
.guide-content__progress-row {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: clamp(14px, 2.5vw, 20px);
}
.guide-content__progress {
  font-size: clamp(11px, 1.5vw, 12px); color: var(--text-muted);
}
.guide-content__mark-all {
  font-size: clamp(11px, 1.5vw, 12px); color: var(--amber);
  cursor: pointer; transition: opacity 150ms;
}
.guide-content__mark-all:hover { opacity: .7; }

/* ---- Cards ---- */
.guide-card {
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  margin-bottom: clamp(8px, 1.5vw, 10px);
  transition: border-color 200ms;
}
.guide-card--done { border-color: var(--success-border); }
.guide-card--open { border-color: var(--border-glow); }

.guide-card__header {
  display: flex; align-items: center; gap: clamp(8px, 1.5vw, 10px);
  width: 100%; padding: clamp(12px, 2vw, 14px) clamp(12px, 2vw, 16px);
  cursor: pointer; text-align: left;
  transition: background 150ms;
}
.guide-card__header:hover { background: var(--accent-soft); }
.guide-card__status { font-size: clamp(14px, 2vw, 16px); flex-shrink: 0; }
.guide-card__title { flex: 1; font-size: clamp(14px, 2vw, 15px); font-weight: 500; }
.guide-card__arrow {
  font-size: clamp(12px, 2vw, 14px); color: var(--text-muted);
  transition: transform 200ms;
}
.guide-card__arrow--expanded { transform: rotate(90deg); }

.guide-card__body { padding: 0 clamp(12px, 2vw, 16px) clamp(12px, 2vw, 16px); }
.guide-card__text {
  font-size: clamp(13px, 2vw, 14px); color: var(--text-secondary);
  line-height: 1.8; white-space: pre-wrap; margin-bottom: 14px;
}
.guide-card__footer {
  display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
}
.guide-card__done-btn {
  padding: 6px 14px;
  font-size: clamp(11px, 1.5vw, 12px); color: var(--text-muted);
  background: var(--bg-panel-3);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: color 150ms, border-color 150ms;
}
.guide-card__done-btn:hover { color: var(--success); border-color: var(--success-border); }
.guide-card__done-btn.done { color: var(--success); border-color: var(--success-border); }
.guide-card__next-btn {
  padding: 6px 14px;
  font-size: clamp(11px, 1.5vw, 13px); font-weight: 600; color: var(--amber);
  background: var(--amber-soft);
  border: 1px solid var(--amber-glow);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 150ms, transform 150ms;
}
.guide-card__next-btn:hover { background: var(--amber-mid); transform: translateX(2px); }

/* ---- Chapter Done ---- */
.guide-chapter-done {
  text-align: center;
  padding: clamp(20px, 4vw, 32px) clamp(16px, 3vw, 20px);
  background: var(--success-soft);
  border: 1px solid var(--success-border);
  border-radius: var(--radius-lg);
  margin-top: clamp(12px, 2vw, 16px);
}
.guide-chapter-done__icon { font-size: clamp(28px, 4vw, 36px); display: block; margin-bottom: 8px; }
.guide-chapter-done p {
  font-size: clamp(13px, 2vw, 15px); color: var(--success); margin-bottom: 10px;
}
.guide-chapter-done__next {
  padding: 8px 18px;
  font-size: clamp(12px, 2vw, 14px); font-weight: 600; color: var(--amber);
  background: var(--amber-soft);
  border: 1px solid var(--amber-glow);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 150ms;
}
.guide-chapter-done__next:hover { background: var(--amber-mid); }

/* ---- Expand transition ---- */
.expand-enter-active { transition: max-height .25s ease, opacity .2s ease; overflow: hidden; }
.expand-leave-active { transition: max-height .2s ease, opacity .15s ease; overflow: hidden; }
.expand-enter-from, .expand-leave-to { max-height: 0; opacity: 0; }
.expand-enter-to, .expand-leave-from { max-height: 800px; opacity: 1; }

/* ---- Mobile ---- */
@media (max-width: 480px) {
  .guide-nav { gap: 0; }
  .guide-nav__tab { padding: 10px 12px; font-size: 12px; }
}
</style>
