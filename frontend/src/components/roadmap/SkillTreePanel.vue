<template>
  <div class="stree">
    <!-- 顶栏：返回 + 标题 + 进度 -->
    <header class="stree__head">
      <button class="stree__back" @click="emit('back')">
        <NeonIcon name="back" :size="14" />
        <span>返回时间线</span>
      </button>

      <div class="stree__title-row">
        <div class="stree__title-block">
          <h2 class="stree__title">项目实战技能树</h2>
          <span class="stree__title-en">SKILL TREE · 邪修学习指南</span>
        </div>
        <div class="stree__progress">
          <z-progress v-if="theme.isZzz" :percent="progressPercent" />
          <div v-else class="stree__progress-ak">
            <div class="stree__progress-ak-bar" :style="{ width: progressPercent + '%' }" />
          </div>
          <span class="stree__progress-num">{{ doneCount }}/{{ totalCount }}</span>
        </div>
      </div>
    </header>

    <!-- 技能链 -->
    <div class="stree__chain">
      <div
        v-for="(node, i) in nodes"
        :key="node.id"
        class="snode"
        :class="{
          'snode--locked': !isUnlocked(i),
          'snode--done': isNodeDone(node),
        }"
      >
        <!-- 连接线 -->
        <span v-if="i > 0" class="snode__link" :class="{ 'snode__link--lit': isNodeDone(nodes[i - 1]) }">
          <NeonIcon v-if="isNodeDone(nodes[i - 1])" name="arrow-right" :size="12" class="snode__link-icon" />
        </span>

        <div class="snode__card">
          <div class="snode__head">
            <span class="snode__num">{{ node.num }}</span>
            <div class="snode__head-text">
              <span class="snode__title">{{ node.title }}</span>
              <span class="snode__en">{{ node.en }}</span>
            </div>
            <span v-if="isNodeDone(node)" class="snode__state snode__state--done">完成</span>
            <span v-else-if="!isUnlocked(i)" class="snode__state snode__state--locked">
              <NeonIcon name="lock" :size="12" />
              锁定
            </span>
            <span v-else class="snode__state">进行中</span>
          </div>

          <p class="snode__desc">{{ node.desc }}</p>

          <!-- 验收标准 -->
          <div class="snode__checks">
            <template v-if="theme.isZzz">
              <z-checkbox
                v-for="c in node.checks"
                :key="node.id + c"
                :model-value="checked.has(node.id + '::' + c)"
                :disabled="!isUnlocked(i)"
                @update:model-value="toggleCheck(node, c)"
              >{{ c }}</z-checkbox>
            </template>
            <template v-else>
              <button
                v-for="c in node.checks"
                :key="node.id + c"
                class="snode__check-ak"
                :class="{ 'snode__check-ak--on': checked.has(node.id + '::' + c) }"
                :disabled="!isUnlocked(i)"
                @click="toggleCheck(node, c)"
              >
                <span class="snode__check-box" aria-hidden="true" />
                <span>{{ c }}</span>
              </button>
            </template>
          </div>

          <a
            v-if="isUnlocked(i)"
            class="snode__src"
            :href="node.url"
            target="_blank"
            rel="noopener"
          >
            查看原文
            <NeonIcon name="external" :size="12" />
          </a>
        </div>
      </div>
    </div>

    <!-- 完成提示 -->
    <div v-if="progressPercent === 100" class="stree__complete">
      <span class="stree__complete-en">ALL CLEAR</span>
      <span class="stree__complete-cn">八个关卡全部通关，你已经具备独立交付完整项目的能力</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive } from 'vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import { useThemeStore } from '@/stores/themeStore';
import { skillTree as nodes } from '@/data/roadmapData';

const emit = defineEmits<{ back: [] }>();

const theme = useThemeStore();

/* ---- 进度持久化（localStorage） ---- */
const LS_KEY = 'xkz_roadmap_skilltree_v1';
const checked = reactive(new Set<string>());

onMounted(() => {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (raw) (JSON.parse(raw) as string[]).forEach((k) => checked.add(k));
  } catch { /* 忽略 */ }
});

function persist() {
  try {
    localStorage.setItem(LS_KEY, JSON.stringify([...checked]));
  } catch { /* 忽略 */ }
}

function toggleCheck(node: (typeof nodes)[number], check: string) {
  const key = node.id + '::' + check;
  if (checked.has(key)) checked.delete(key);
  else checked.add(key);
  persist();
}

/* ---- 解锁与完成 ---- */
function isNodeDone(node: (typeof nodes)[number]): boolean {
  return node.checks.every((c) => checked.has(node.id + '::' + c));
}

// 关卡解锁：上一节点全部验收通过才解锁（首节点始终解锁）
function isUnlocked(i: number): boolean {
  if (i === 0) return true;
  return isNodeDone(nodes[i - 1]);
}

const doneCount = computed(() => nodes.filter((n) => isNodeDone(n)).length);
const totalCount = nodes.length;
const progressPercent = computed(() =>
  Math.round((doneCount.value / totalCount) * 100)
);
</script>

<style scoped>
/* ===== 顶栏 ===== */
.stree__head { margin-bottom: clamp(18px, 3vw, 26px); }
.stree__back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 0;
  transition: color 160ms;
}
.stree__back:hover { color: var(--amber); }

.stree__title-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 10px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-subtle);
}
.stree__title { margin: 0; font-size: clamp(20px, 3.4vw, 26px); font-weight: 800; letter-spacing: 0.1em; }
.stree__title-en {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.26em;
  color: var(--text-muted);
}
.stree__progress {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 180px;
  flex: 1;
  max-width: 320px;
}
.stree__progress-num {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  color: var(--amber);
  white-space: nowrap;
}
.stree__progress-ak {
  flex: 1;
  height: 6px;
  background: var(--surface-glass);
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-sm);
  overflow: hidden;
}
.stree__progress-ak-bar {
  height: 100%;
  background: var(--amber);
  transition: width 400ms ease;
}

/* ===== 技能链 ===== */
.stree__chain {
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-width: 720px;
}

.snode__link {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 18px;
  margin-left: 34px;
  border-left: 2px dashed var(--border-subtle);
  position: relative;
  transition: border-color 300ms;
}
.snode__link--lit {
  border-left-color: var(--amber);
}
.snode__link-icon {
  position: absolute;
  left: -7px;
  top: 50%;
  transform: translateY(-50%) rotate(90deg);
  color: var(--amber);
}

.snode__card {
  padding: 16px 18px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-sm);
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: border-color 250ms, opacity 250ms;
}

/* 锁定态 */
.snode--locked .snode__card {
  opacity: 0.45;
  border-style: dashed;
}

/* 完成态 */
.snode--done .snode__card {
  border-color: var(--amber-strong);
  background: linear-gradient(135deg, var(--amber-soft), var(--bg-panel) 55%);
}

.snode__head {
  display: flex;
  align-items: center;
  gap: 12px;
}
.snode__num {
  font-family: var(--font-display);
  font-size: clamp(26px, 4vw, 34px);
  line-height: 1;
  color: var(--amber);
  min-width: 40px;
}
.snode--locked .snode__num { color: var(--text-muted); }
.snode__head-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}
.snode__title { font-size: 16px; font-weight: 800; letter-spacing: 0.06em; }
.snode__en {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.24em;
  color: var(--text-muted);
}
.snode__state {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--text-muted);
  padding: 3px 10px;
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-sm);
  white-space: nowrap;
}
.snode__state--done {
  color: var(--on-amber);
  background: var(--amber);
  border-color: var(--amber);
}
.snode__state--locked { color: var(--text-muted); }

.snode__desc {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
}

/* 验收标准 */
.snode__checks {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 12px;
  background: var(--bg-primary);
  border-left: 2px solid var(--border-subtle);
}
.snode--done .snode__checks { border-left-color: var(--amber); }

.snode__check-ak {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12.5px;
  color: var(--text-secondary);
  background: none;
  border: none;
  padding: 2px 0;
  text-align: left;
  cursor: pointer;
  transition: color 150ms;
}
.snode__check-ak:disabled { cursor: not-allowed; opacity: 0.6; }
.snode__check-ak--on { color: var(--text-primary); }
.snode__check-box {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-sm);
  background: var(--surface-glass);
  transition: background 150ms, border-color 150ms;
}
.snode__check-ak--on .snode__check-box {
  background: var(--amber);
  border-color: var(--amber);
  box-shadow: inset 0 0 0 2px var(--bg-primary);
}

.snode__src {
  align-self: flex-end;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--amber);
  text-decoration: none;
  letter-spacing: 0.08em;
}
.snode__src:hover { text-decoration: underline; }

/* ===== 全部完成 ===== */
.stree__complete {
  margin-top: 22px;
  padding: 18px;
  text-align: center;
  border: 1px solid var(--border-glow);
  background: var(--accent-mid);
  clip-path: var(--clip-md);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.stree__complete-en {
  font-family: var(--font-display);
  font-size: 24px;
  letter-spacing: 0.3em;
  color: var(--amber);
}
.stree__complete-cn {
  font-size: 13px;
  color: var(--text-primary);
}

/* ===== 移动端 ===== */
@media (max-width: 640px) {
  .stree__title-row { flex-direction: column; align-items: stretch; }
  .stree__progress { max-width: none; }
}
</style>
