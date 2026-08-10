<template>
  <div class="quest-root">
    <!-- Top bar -->
    <header class="quest-topbar">
      <button class="quest-topbar__back" @click="$router.push('/')">
        <NeonIcon name="back" :size="20" />
        <span class="quest-topbar__back-label">返回</span>
      </button>
      <span class="quest-topbar__title">🎮 新手任务</span>
      <span class="quest-topbar__ver">v2.0</span>
    </header>

    <!-- === PHASE 1: Login splash === -->
    <QuestLogin v-if="phase === 'login'" @done="onLoginDone" />

    <!-- === PHASE 2: Level select === -->
    <div v-else-if="phase === 'levels'" class="levels-root">
      <div class="levels-header">
        <h2>选择关卡</h2>
        <p>完成当前关卡以解锁下一关</p>
      </div>
      <div class="levels-grid">
        <button
          v-for="(ch, idx) in chapters"
          :key="ch.id"
          class="level-card"
          :class="{
            'level-card--unlocked': idx < unlockIndex,
            'level-card--current': idx === currentLevel,
            'level-card--locked': idx > currentLevel,
            'level-card--done': chapterProgress(ch.id) === 100,
          }"
          :disabled="idx > currentLevel"
          @click="enterChapter(idx)"
        >
          <div class="level-card__inner">
            <span class="level-card__icon">{{ ch.icon }}</span>
            <span class="level-card__num">关卡 {{ idx + 1 }}</span>
            <span class="level-card__title">{{ ch.title }}</span>
            <div class="level-card__progress">
              <div class="level-card__bar">
                <div class="level-card__fill" :style="{ width: chapterProgress(ch.id) + '%' }" />
              </div>
              <span>{{ chapterProgress(ch.id) }}%</span>
            </div>
            <span v-if="idx > currentLevel" class="level-card__lock">🔒</span>
            <span v-else-if="chapterProgress(ch.id) === 100" class="level-card__done">✅</span>
          </div>
        </button>
      </div>
    </div>

    <!-- === PHASE 3: Chapter reader === -->
    <div v-else class="reader-root">
      <!-- Chapter header -->
      <div class="reader-top">
        <button class="reader-top__back" @click="phase = 'levels'">
          <span>← 返回关卡选择</span>
        </button>
        <div class="reader-top__meta">
          <span class="reader-top__icon">{{ activeChapter?.icon }}</span>
          <span class="reader-top__title">{{ activeChapter?.title }}</span>
        </div>
        <div class="reader-top__progress">
          已完成 {{ chapterProgress(activeChapter?.id ?? '') }}%
        </div>
      </div>

      <!-- Sections -->
      <div class="reader-sections">
        <div
          v-for="(sec, idx) in activeChapter?.sections ?? []"
          :key="sec.id"
          class="reader-section"
          :class="{ 'reader-section--done': isDone(sec.id) }"
        >
          <div class="reader-section__header">
            <span class="reader-section__num">{{ idx + 1 }}</span>
            <h3 class="reader-section__title">{{ sec.title }}</h3>
          </div>
          <div class="reader-section__body" v-html="renderMarkdown(sec.content)" />
          <div class="reader-section__footer">
            <button
              class="reader-section__check"
              :class="{ done: isDone(sec.id) }"
              @click="toggleDone(sec.id)"
            >
              <span class="reader-section__check-icon">{{ isDone(sec.id) ? '✓' : '○' }}</span>
              <span>{{ isDone(sec.id) ? '已完成' : '标记完成' }}</span>
            </button>
          </div>
        </div>

        <!-- Chapter complete banner -->
        <div v-if="chapterProgress(activeChapter?.id ?? '') === 100" class="reader-done">
          <span class="reader-done__icon">🎊</span>
          <p>本章全部完成！</p>
          <button v-if="!isLastChapter" class="reader-done__next" @click="goNextChapter">
            进入下一关：{{ chapters[currentLevel + 1]?.title }} →
          </button>
          <button v-else class="reader-done__all" @click="phase = 'levels'">
            返回关卡选择
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import QuestLogin from '@/components/quest/QuestLogin.vue';
import { loadProgress, saveProgress } from '@/composables/useQuest';
import { questChapters } from '@/data/questData';
import { renderMarkdown } from '@/composables/useMarkdown';

type Phase = 'login' | 'levels' | 'reading';

const chapters = questChapters; // 4 chapters, 补缺篇 deleted
const progress = reactive(loadProgress());
const phase = ref<Phase>(progress.hasSeenIntro ? 'levels' : 'login');
const readingIdx = ref(0);

const currentLevel = computed(() => {
  // Find first chapter not 100% completed
  for (let i = 0; i < chapters.length; i++) {
    if (chapterProgress(chapters[i].id) < 100) return i;
  }
  return Math.min(chapters.length - 1, 3);
});

const unlockIndex = computed(() => {
  // Chapters 1 & 2: serial unlock. Chapters 3 & 4: unlock together after 2
  if (chapterProgress('login') < 100) return 1;
  if (chapterProgress('mainline') < 100) return 2;
  return 4; // all unlocked
});

const isLastChapter = computed(() => readingIdx.value >= chapters.length - 1);

const activeChapter = computed(() => chapters[readingIdx.value] ?? null);

function chapterProgress(id: string) {
  const ch = chapters.find(c => c.id === id);
  if (!ch || ch.sections.length === 0) return 0;
  const done = ch.sections.filter(s => isDone(s.id)).length;
  return Math.round((done / ch.sections.length) * 100);
}

function isDone(id: string) { return progress.mainComplete.includes(id); }

function toggleDone(id: string) {
  const idx = progress.mainComplete.indexOf(id);
  if (idx >= 0) progress.mainComplete.splice(idx, 1);
  else progress.mainComplete.push(id);
  saveProgress({ ...progress });
}

function onLoginDone() {
  progress.hasSeenIntro = true;
  saveProgress({ ...progress });
  phase.value = 'levels';
}

function enterChapter(idx: number) {
  readingIdx.value = idx;
  phase.value = 'reading';
}

function goNextChapter() {
  if (readingIdx.value < chapters.length - 1) {
    readingIdx.value++;
  }
}
</script>

<style scoped>
/* === ROOT === */
.quest-root {
  height: 100vh;
  height: 100dvh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  overflow: hidden;
}

/* === TOP BAR === */
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

/* === LEVEL SELECT === */
.levels-root {
  flex: 1; overflow-y: auto;
  padding: clamp(20px, 4vw, 32px) clamp(16px, 3vw, 24px);
  -webkit-overflow-scrolling: touch;
}
.levels-header {
  text-align: center; margin-bottom: clamp(24px, 4vw, 36px);
}
.levels-header h2 {
  font-size: clamp(22px, 3.5vw, 28px); font-weight: 700; color: var(--amber); margin-bottom: 8px;
}
.levels-header p {
  font-size: clamp(13px, 2vw, 15px); color: var(--text-secondary);
}

.levels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));
  gap: clamp(12px, 2vw, 16px);
  max-width: 640px;
  margin: 0 auto;
}

.level-card {
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: border-color 200ms, transform 150ms, box-shadow 200ms;
  text-align: left; overflow: hidden;
}
.level-card:hover:not(:disabled) { transform: translateY(-2px); }
.level-card:disabled { opacity: .35; cursor: not-allowed; }
.level-card--current { border-color: var(--amber); box-shadow: 0 0 12px var(--amber-glow); }
.level-card--done { border-color: var(--success-border); background: var(--success-soft); }
.level-card--unlocked:hover { border-color: var(--accent-bright); }

.level-card__inner {
  padding: clamp(18px, 3vw, 24px);
  display: flex; flex-direction: column; align-items: center; text-align: center; gap: 6px;
  position: relative;
}
.level-card__icon { font-size: clamp(28px, 4vw, 36px); }
.level-card__num {
  font-family: var(--font-display);
  font-size: clamp(10px, 1.5vw, 11px); color: var(--text-muted);
  letter-spacing: 2px;
}
.level-card__title {
  font-size: clamp(15px, 2.2vw, 17px); font-weight: 600;
}
.level-card__progress {
  display: flex; align-items: center; gap: 8px;
  width: 100%; margin-top: 6px;
}
.level-card__bar {
  flex: 1; height: 4px; background: var(--bg-panel-3);
  border-radius: 2px; overflow: hidden;
}
.level-card__fill {
  height: 100%; background: var(--amber);
  border-radius: 2px; transition: width .4s ease;
}
.level-card--done .level-card__fill { background: var(--success); }
.level-card__progress span {
  font-size: clamp(10px, 1.5vw, 11px); color: var(--text-muted);
  min-width: 32px; text-align: right;
}
.level-card__lock { position: absolute; top: 12px; right: 14px; font-size: 16px; }
.level-card__done { position: absolute; top: 12px; right: 14px; font-size: 18px; }

/* === READER === */
.reader-root {
  flex: 1; display: flex; flex-direction: column;
  overflow: hidden;
}
.reader-top {
  flex-shrink: 0;
  padding: clamp(10px, 2vw, 14px) clamp(14px, 2.5vw, 20px);
  border-bottom: 1px solid var(--border-subtle);
  display: flex; align-items: center; gap: 14px;
  background: var(--bg-primary);
}
.reader-top__back {
  font-size: clamp(12px, 2vw, 14px); color: var(--text-muted);
  cursor: pointer; transition: color 150ms; white-space: nowrap;
}
.reader-top__back:hover { color: var(--amber); }
.reader-top__meta {
  display: flex; align-items: center; gap: 8px; flex: 1;
}
.reader-top__icon { font-size: clamp(18px, 2.5vw, 22px); }
.reader-top__title {
  font-size: clamp(15px, 2.2vw, 17px); font-weight: 600; color: var(--amber);
}
.reader-top__progress {
  font-size: clamp(11px, 1.5vw, 12px); color: var(--text-muted);
  white-space: nowrap;
}

.reader-sections {
  flex: 1; overflow-y: auto;
  padding: clamp(20px, 3vw, 28px) clamp(16px, 3vw, 24px);
  -webkit-overflow-scrolling: touch;
}

/* Section cards */
.reader-section {
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  margin-bottom: clamp(16px, 3vw, 24px);
  overflow: hidden;
  transition: border-color 200ms;
}
.reader-section--done { border-color: var(--success-border); }
.reader-section__header {
  display: flex; align-items: center; gap: clamp(10px, 2vw, 14px);
  padding: clamp(14px, 2vw, 18px) clamp(16px, 2.5vw, 20px);
  border-bottom: 1px solid var(--border-subtle);
}
.reader-section__num {
  font-family: var(--font-display);
  font-size: clamp(12px, 1.8vw, 14px); color: var(--amber);
  border: 1px solid var(--amber-glow);
  border-radius: var(--radius-sm);
  width: clamp(28px, 4vw, 32px); height: clamp(28px, 4vw, 32px);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.reader-section__title {
  font-size: clamp(16px, 2.5vw, 19px); font-weight: 600;
}

.reader-section__body {
  padding: clamp(16px, 2.5vw, 24px) clamp(16px, 2.5vw, 20px) clamp(10px, 2vw, 14px);
  font-size: clamp(13px, 2vw, 15px);
  line-height: 1.85;
  color: var(--text-secondary);
}

/* Markdown rendering within section body */
.reader-section__body :deep(h1),
.reader-section__body :deep(h2),
.reader-section__body :deep(h3),
.reader-section__body :deep(h4) {
  color: var(--text-primary);
  margin: 1em 0 .5em;
  line-height: 1.3;
}
.reader-section__body :deep(h2) {
  font-size: clamp(16px, 2.5vw, 18px);
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 6px;
}
.reader-section__body :deep(h3) {
  font-size: clamp(14px, 2.2vw, 16px);
  color: var(--amber);
}
.reader-section__body :deep(h4) {
  font-size: clamp(13px, 2vw, 14px);
  color: var(--text-primary);
}
.reader-section__body :deep(p) {
  margin-bottom: .8em;
}
.reader-section__body :deep(strong) {
  color: var(--text-primary);
  font-weight: 600;
}
.reader-section__body :deep(em) {
  font-style: italic;
  color: var(--text-muted);
}
.reader-section__body :deep(code) {
  font-family: var(--font-mono);
  font-size: .88em;
  background: var(--bg-panel-3);
  padding: 1px 6px;
  border-radius: 3px;
}
.reader-section__body :deep(a) {
  color: var(--text-link);
  text-decoration: underline;
  text-underline-offset: 2px;
}
.reader-section__body :deep(a:hover) { color: var(--accent-bright); }

.reader-section__body :deep(blockquote) {
  border-left: 3px solid var(--amber);
  padding: clamp(8px, 1.5vw, 12px) clamp(12px, 2vw, 16px);
  margin: .8em 0;
  background: var(--amber-soft);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-size: .95em;
  color: var(--text-secondary);
}
.reader-section__body :deep(blockquote strong) { color: var(--amber); }

.reader-section__body :deep(hr) {
  border: none;
  border-top: 1px solid var(--border-subtle);
  margin: 1.2em 0;
}

.reader-section__body :deep(ul),
.reader-section__body :deep(ol) {
  padding-left: clamp(16px, 3vw, 22px);
  margin: .6em 0;
}
.reader-section__body :deep(li) {
  margin-bottom: .3em;
}

.reader-section__body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: .8em 0;
  font-size: .92em;
  display: block;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.reader-section__body :deep(th),
.reader-section__body :deep(td) {
  border: 1px solid var(--border-subtle);
  padding: clamp(6px, 1vw, 8px) clamp(8px, 1.5vw, 12px);
  text-align: left;
  white-space: nowrap;
}
.reader-section__body :deep(th) {
  background: var(--bg-panel-3);
  color: var(--text-primary);
  font-weight: 600;
}

.reader-section__body :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-md);
  margin: .8em 0;
  display: block;
  border: 1px solid var(--border-subtle);
}

/* Section footer */
.reader-section__footer {
  padding: clamp(8px, 1.5vw, 12px) clamp(16px, 2.5vw, 20px) clamp(14px, 2vw, 18px);
  display: flex; justify-content: center;
}
.reader-section__check {
  display: flex; align-items: center; gap: 8px;
  padding: clamp(8px, 1.5vw, 10px) clamp(16px, 3vw, 24px);
  font-size: clamp(13px, 2vw, 15px); font-weight: 600; color: var(--text-muted);
  background: var(--bg-panel-3);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 200ms;
}
.reader-section__check:hover {
  color: var(--success); border-color: var(--success-border);
  background: var(--success-soft);
}
.reader-section__check.done {
  color: var(--success); border-color: var(--success-border);
  background: var(--success-soft);
}
.reader-section__check-icon {
  font-size: clamp(16px, 2.5vw, 20px);
  font-weight: 700;
  transition: transform 200ms;
}
.reader-section__check.done .reader-section__check-icon {
  transform: scale(1.2);
}

/* Chapter done banner */
.reader-done {
  text-align: center;
  padding: clamp(20px, 4vw, 32px);
  background: var(--success-soft);
  border: 1px solid var(--success-border);
  border-radius: var(--radius-lg);
  margin-top: 8px;
}
.reader-done__icon { font-size: clamp(32px, 5vw, 42px); display: block; margin-bottom: 8px; }
.reader-done p {
  font-size: clamp(14px, 2.2vw, 16px); color: var(--success); font-weight: 600; margin-bottom: 14px;
}
.reader-done__next,
.reader-done__all {
  padding: 10px 24px;
  font-size: clamp(13px, 2vw, 15px); font-weight: 600; color: var(--amber);
  background: var(--amber-soft);
  border: 1px solid var(--amber-glow);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 150ms, transform 150ms;
}
.reader-done__next:hover,
.reader-done__all:hover { background: var(--amber-mid); transform: translateX(2px); }

/* Mobile */
@media (max-width: 640px) {
  .quest-topbar__back-label { display: none; }
  .levels-grid { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
  .reader-section__body :deep(table) { font-size: .82em; }
  .reader-section__footer { padding: 8px 12px 12px; }
}
</style>
