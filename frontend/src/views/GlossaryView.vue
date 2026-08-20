<template>
  <PageShell title="黑话辞典" subtitle="GLOSSARY · 校园术语百科" active-key="glossary">
    <div v-if="loading" class="loading">SYSTEM LOADING…</div>
    <div v-else-if="error" class="error">加载失败：{{ error }}</div>
    <div v-else class="glossary">
      <!-- 搜索框：夜间 zzz 用 zenless-ui 输入框 / 日间 ak 原版 -->
      <z-input
        v-if="theme.isZzz"
        v-model="query"
        class="glossary__zsearch"
        placeholder="搜术语或拼音…"
        prefix-icon="search"
        clearable
      />
      <div v-else class="glossary__search">
        <NeonIcon name="search" :size="16" class="glossary__search-icon" />
        <input
          v-model="query"
          class="glossary__search-input"
          placeholder="搜术语或拼音…"
          type="text"
        />
        <button v-if="query" class="glossary__search-clear" @click="query = ''">
          <NeonIcon name="close" :size="14" />
        </button>
      </div>

      <!-- 分类筛选 -->
      <div class="glossary__cats">
        <!-- 夜间 zzz：zenless-ui 按钮组 -->
        <template v-if="theme.isZzz">
          <z-button
            size="mini"
            :type="activeCat === 'all' ? 'primary' : 'default'"
            @click="activeCat = 'all'"
          >全部</z-button>
          <z-button
            v-for="c in data.categories"
            :key="c.key"
            size="mini"
            :type="activeCat === c.key ? 'primary' : 'default'"
            @click="activeCat = c.key"
          >{{ c.label }}</z-button>
        </template>
        <!-- 日间 ak：原版分类 -->
        <template v-else>
          <button
            class="glossary__cat"
            :class="{ 'glossary__cat--active': activeCat === 'all' }"
            @click="activeCat = 'all'"
          >
            全部
          </button>
          <button
            v-for="c in data.categories"
            :key="c.key"
            class="glossary__cat"
            :class="{ 'glossary__cat--active': activeCat === c.key }"
            @click="activeCat = c.key"
          >
            {{ c.label }}
          </button>
        </template>
      </div>

      <!-- 术语卡片 -->
      <div class="glossary__list">
        <!-- 夜间 zzz：zenless-ui 折叠面板 -->
        <z-collapse
          v-if="theme.isZzz"
          :model-value="openTerm ?? undefined"
          accordion
          class="glossary__zcollapse"
          @change="onCollapseChange"
        >
          <z-collapse-item
            v-for="t in filteredTerms"
            :key="t.term"
            :name="t.term"
            :data-term="t.term"
          >
            <template #title>
              <span class="glossary__term">{{ t.term }}</span>
              <span class="glossary__pinyin">{{ t.pinyin }}</span>
            </template>
            <p class="glossary__definition">{{ t.definition }}</p>
            <div v-if="t.related && t.related.length" class="glossary__related">
              <span class="glossary__related-label">相关：</span>
              <z-tag
                v-for="r in t.related"
                :key="r"
                class="glossary__zrelated"
                @click="jumpTo(r)"
              >{{ r }}</z-tag>
            </div>
          </z-collapse-item>
        </z-collapse>
        <!-- 日间 ak：原版卡片 -->
        <template v-else>
          <button
            v-for="t in filteredTerms"
            :key="t.term"
            class="glossary__card"
            :class="{ 'glossary__card--open': openTerm === t.term }"
            :data-term="t.term"
            @click="toggle(t.term)"
          >
            <div class="glossary__card-head">
              <span class="glossary__term">{{ t.term }}</span>
              <span class="glossary__pinyin">{{ t.pinyin }}</span>
              <NeonIcon
                name="arrow-right"
                :size="14"
                class="glossary__card-arrow"
                :class="{ 'glossary__card-arrow--up': openTerm === t.term }"
              />
            </div>
            <div v-if="openTerm === t.term" class="glossary__card-body">
              <p class="glossary__definition">{{ t.definition }}</p>
              <div v-if="t.related && t.related.length" class="glossary__related">
                <span class="glossary__related-label">相关：</span>
                <button
                  v-for="r in t.related"
                  :key="r"
                  class="glossary__related-tag"
                  @click.stop="jumpTo(r)"
                >{{ r }}</button>
              </div>
            </div>
          </button>
        </template>
      </div>

      <p v-if="!filteredTerms.length" class="empty">没有找到「{{ query }}」相关术语</p>
    </div>
  </PageShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import PageShell from '@/components/common/PageShell.vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import { useThemeStore } from '@/stores/themeStore';

const theme = useThemeStore();

interface GlossaryCategory {
  key: string;
  label: string;
  icon: string;
}
interface GlossaryTerm {
  term: string;
  pinyin: string;
  category: string;
  definition: string;
  related: string[];
}
interface GlossaryData {
  categories: GlossaryCategory[];
  terms: GlossaryTerm[];
}

const data = ref<GlossaryData>({ categories: [], terms: [] });
const loading = ref(true);
const error = ref('');
const query = ref('');
const activeCat = ref('all');
const openTerm = ref<string | null>(null);

onMounted(async () => {
  try {
    const res = await fetch('/api/glossary');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    data.value = await res.json();
  } catch (e) {
    error.value = e instanceof Error ? e.message : '加载失败';
  } finally {
    loading.value = false;
  }
});

const filteredTerms = computed(() => {
  let list = data.value.terms;
  if (activeCat.value !== 'all') {
    list = list.filter((t) => t.category === activeCat.value);
  }
  const q = query.value.trim().toLowerCase();
  if (q) {
    list = list.filter(
      (t) =>
        t.term.toLowerCase().includes(q) ||
        t.pinyin.toLowerCase().includes(q) ||
        t.definition.toLowerCase().includes(q),
    );
  }
  return list;
});

function toggle(term: string) {
  openTerm.value = openTerm.value === term ? null : term;
}

// z-collapse accordion：change 回传数组（0 或 1 项）
function onCollapseChange(val: string | number | Array<string | number>) {
  if (Array.isArray(val)) {
    openTerm.value = val.length ? String(val[0]) : null;
  } else if (val !== undefined && val !== null && val !== '') {
    openTerm.value = String(val);
  } else {
    openTerm.value = null;
  }
}

function jumpTo(term: string) {
  const target = data.value.terms.find((t) => t.term === term);
  if (!target) {
    query.value = term;
    openTerm.value = null;
    return;
  }
  activeCat.value = target.category;
  query.value = '';
  openTerm.value = term;
  setTimeout(() => {
    const el = document.querySelector(`[data-term="${term}"]`);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, 50);
}
</script>

<style scoped>
.glossary {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* zenless-ui 搜索框 */
.glossary__zsearch {
  width: 100%;
}

/* zenless-ui 折叠面板标题排版 */
.glossary__zcollapse :deep(.z-collapse-item__title) {
  display: flex;
  align-items: baseline;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

/* zenless-ui 相关术语标签可点击 */
.glossary__zrelated {
  cursor: pointer;
}

/* 搜索框 */
.glossary__search {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-sm);
  position: relative;
}

.glossary__search-icon {
  color: var(--text-muted);
  flex-shrink: 0;
}

.glossary__search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 14px;
  font-family: var(--font-body);
}

.glossary__search-input::placeholder {
  color: var(--text-muted);
}

.glossary__search-clear {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  color: var(--text-muted);
  border-radius: 50%;
  transition: color 200ms, background 200ms;
}

.glossary__search-clear:hover {
  color: var(--text-primary);
  background: var(--bg-panel-2);
}

/* 分类标签 */
.glossary__cats {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.glossary__cat {
  padding: 6px 14px;
  font-size: 12px;
  font-family: var(--font-mono);
  letter-spacing: 1px;
  color: var(--text-muted);
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-sm);
  transition: color 200ms, border-color 200ms, background 200ms;
}

.glossary__cat:hover {
  color: var(--amber);
  border-color: var(--amber);
}

.glossary__cat--active {
  color: var(--on-amber);
  background: var(--amber);
  border-color: var(--amber);
}

/* 术语列表 */
.glossary__list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.glossary__card {
  text-align: left;
  padding: 14px 18px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-md);
  color: var(--text-primary);
  transition: border-color 200ms, box-shadow 200ms;
}

.glossary__card:hover {
  border-color: var(--amber);
  box-shadow: 0 0 12px var(--amber-glow);
}

.glossary__card--open {
  border-color: var(--amber);
}

.glossary__card-head {
  display: flex;
  align-items: center;
  gap: 12px;
}

.glossary__term {
  font-size: 16px;
  font-weight: 700;
  color: var(--amber);
  font-family: var(--font-display);
  letter-spacing: 1px;
}

.glossary__pinyin {
  flex: 1;
  font-size: 12px;
  font-family: var(--font-mono);
  color: var(--text-muted);
  letter-spacing: 1px;
}

.glossary__card-arrow {
  color: var(--text-muted);
  flex-shrink: 0;
  transition: transform 200ms, color 200ms;
}

.glossary__card-arrow--up {
  transform: rotate(-90deg);
  color: var(--amber);
}

.glossary__card--open .glossary__card-arrow {
  color: var(--amber);
}

.glossary__card-body {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-subtle);
}

.glossary__definition {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.glossary__related {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.glossary__related-label {
  font-size: 12px;
  color: var(--text-muted);
}

.glossary__related-tag {
  padding: 3px 10px;
  font-size: 12px;
  color: var(--amber);
  border: 1px solid var(--amber);
  border-radius: 12px;
  transition: background 200ms;
}

.glossary__related-tag:hover {
  background: var(--amber-soft);
}

.loading,
.error,
.empty {
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
  padding: 32px 0;
}

.error {
  color: var(--danger);
}

@media (max-width: 767px) {
  .glossary__search {
    padding: 12px 14px;
  }
  .glossary__search-input {
    font-size: 16px;
  }
  .glossary__card {
    padding: 12px 14px;
  }
  .glossary__term {
    font-size: 15px;
  }
  .glossary__definition {
    font-size: 14px;
  }
}
</style>
