<template>
  <div class="gtl">
    <!-- 目标 Hero：返回 + 编号 + 标题 -->
    <header class="gtl__hero">
      <button class="gtl__back" @click="emit('back')">
        <NeonIcon name="back" :size="14" />
        <span>目标选择</span>
      </button>

      <div class="gtl__hero-main">
        <div class="gtl__hero-left">
          <span class="gtl__hero-num">{{ goal.num }}</span>
          <span class="gtl__hero-en">{{ goal.en }}</span>
        </div>
        <div class="gtl__hero-right">
          <h2 class="gtl__hero-title">{{ goal.title }}路线</h2>
          <p class="gtl__hero-desc">{{ goal.desc }}</p>
        </div>
      </div>
    </header>

    <!-- 学年时间线 -->
    <section
      v-for="stage in goal.stages"
      :key="stage.num"
      class="gtl__stage"
      :class="{ 'gtl__stage--empty': stage.nodes.length === 0 }"
    >
      <div class="gtl__stage-head">
        <span class="gtl__stage-num">YEAR {{ stage.num }}</span>
        <span class="gtl__stage-year">{{ stage.year }}</span>
        <span class="gtl__stage-en">{{ stage.en }}</span>
        <span class="gtl__stage-line" />
      </div>

      <div v-if="stage.nodes.length" class="gtl__nodes">
        <button
          v-for="node in stage.nodes"
          :key="node.id"
          class="gnode"
          @click="openNode(node)"
        >
          <span class="gnode__en">{{ node.en }}</span>
          <span class="gnode__title">{{ node.title }}</span>
          <span class="gnode__source">
            {{ node.source }}
            <NeonIcon v-if="node.skillTree" name="star" :size="11" class="gnode__tree-icon" />
          </span>
          <span v-if="node.skillTree" class="gnode__badge">技能树</span>
        </button>
      </div>
      <p v-else class="gtl__empty">该阶段内容规划中…</p>
    </section>

    <!-- 节点摘要弹窗：夜间 zzz 用 zenless-ui / 日间 ak 用原版 -->
    <Teleport v-if="theme.isZzz && activeNode" to="body">
      <z-modal
        :model-value="true"
        :title="activeNode.title"
        cancel-text="关闭"
        :confirm-text="activeNode.skillTree ? '进入技能树' : '查看原文'"
        @confirm="onModalConfirm"
        @cancel="closeNode"
        @close="closeNode"
      >
        <div class="gmodal">
          <p class="gmodal__en">{{ activeNode.en }} · {{ activeNode.source }}</p>
          <p class="gmodal__desc">{{ activeNode.desc }}</p>
          <p v-if="activeNode.skillTree" class="gmodal__tree-hint">
            该节点关联「项目实战技能树」，可在确认后进入
          </p>
        </div>
      </z-modal>
    </Teleport>
    <Teleport v-else-if="activeNode" to="body">
      <Transition name="modal">
        <div class="gmodal-mask" @click.self="closeNode">
          <div class="gmodal-panel" role="dialog" :aria-label="activeNode.title">
            <h3 class="gmodal-panel__title">{{ activeNode.title }}</h3>
            <p class="gmodal__en">{{ activeNode.en }} · {{ activeNode.source }}</p>
            <p class="gmodal__desc">{{ activeNode.desc }}</p>
            <div class="gmodal-panel__actions">
              <button class="gmodal-btn" @click="closeNode">关闭</button>
              <button class="gmodal-btn gmodal-btn--primary" @click="onModalConfirm">
                {{ activeNode.skillTree ? '进入技能树' : '查看原文' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import { useThemeStore } from '@/stores/themeStore';
import type { RoadmapGoal, RoadmapNode } from '@/data/roadmapData';

defineProps<{ goal: RoadmapGoal }>();
const emit = defineEmits<{ back: []; enterSkillTree: [] }>();

const theme = useThemeStore();
const activeNode = ref<RoadmapNode | null>(null);

function openNode(node: RoadmapNode) {
  activeNode.value = node;
}
function closeNode() {
  activeNode.value = null;
}
function onModalConfirm() {
  const node = activeNode.value;
  if (!node) return;
  if (node.skillTree) {
    activeNode.value = null;
    emit('enterSkillTree');
  } else {
    window.open(node.url, '_blank', 'noopener');
  }
}
</script>

<style scoped>
/* ===== Hero ===== */
.gtl__hero {
  margin-bottom: clamp(20px, 3vw, 30px);
}
.gtl__back {
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
.gtl__back:hover { color: var(--amber); }

.gtl__hero-main {
  display: flex;
  align-items: stretch;
  gap: clamp(14px, 2.5vw, 22px);
  margin-top: 10px;
}
.gtl__hero-left {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 8px 16px;
  background: var(--amber);
  clip-path: var(--clip-sm);
  min-width: 92px;
}
.gtl__hero-num {
  font-family: var(--font-display);
  font-size: clamp(36px, 6vw, 52px);
  line-height: 0.95;
  color: var(--on-amber);
}
.gtl__hero-en {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.22em;
  color: var(--on-amber-muted);
}
.gtl__hero-right {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
  border-left: 2px solid var(--border-subtle);
  padding-left: clamp(12px, 2vw, 20px);
}
.gtl__hero-title {
  margin: 0;
  font-size: clamp(20px, 3.6vw, 28px);
  font-weight: 800;
  letter-spacing: 0.1em;
  color: var(--text-primary);
}
.gtl__hero-desc {
  margin: 0;
  font-size: clamp(12px, 1.8vw, 13px);
  color: var(--text-secondary);
}

/* ===== 学年区块 ===== */
.gtl__stage {
  margin-bottom: clamp(18px, 3vw, 28px);
}
.gtl__stage-head {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 12px;
}
.gtl__stage-num {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.3em;
  color: var(--amber);
  font-weight: 700;
}
.gtl__stage-year {
  font-size: clamp(16px, 2.6vw, 20px);
  font-weight: 800;
  letter-spacing: 0.14em;
  color: var(--text-primary);
}
.gtl__stage-en {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.26em;
  color: var(--text-muted);
}
.gtl__stage-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, var(--amber-strong), transparent);
}

/* ===== 节点网格 ===== */
.gtl__nodes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 12px;
}
.gnode {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 5px;
  padding: 14px 16px;
  text-align: left;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-sm);
  cursor: pointer;
  transition: border-color 180ms, background 180ms, transform 180ms;
}
.gnode:hover {
  border-color: var(--border-glow);
  background: var(--accent-soft);
  transform: translateY(-2px);
}
.gnode__en {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.24em;
  color: var(--text-muted);
}
.gnode__title {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--text-primary);
}
.gnode__source {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: var(--text-secondary);
}
.gnode__tree-icon {
  color: var(--amber);
}
.gnode__badge {
  position: absolute;
  top: 0;
  right: 0;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
  padding: 3px 10px;
  background: var(--amber);
  color: var(--on-amber);
  clip-path: var(--clip-sm);
}

.gtl__empty {
  margin: 0;
  padding: 18px 16px;
  font-size: 13px;
  color: var(--text-muted);
  border: 1px dashed var(--border-subtle);
}

/* ===== zzz 弹窗内容 ===== */
.gmodal__en {
  margin: 0 0 8px;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.18em;
  color: var(--text-muted);
}
.gmodal__desc {
  margin: 0;
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-secondary);
}
.gmodal__tree-hint {
  margin: 10px 0 0;
  font-size: 12px;
  color: var(--amber);
}

/* ===== ak 原版弹窗 ===== */
.gmodal-mask {
  position: fixed;
  inset: 0;
  background: var(--mask-strong);
  z-index: 140;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.gmodal-panel {
  width: min(380px, 100%);
  background: var(--bg-panel);
  border: 1px solid var(--border-glow);
  clip-path: var(--clip-md);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.gmodal-panel__title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
}
.gmodal-panel__actions {
  display: flex;
  gap: 10px;
  margin-top: 8px;
}
.gmodal-btn {
  flex: 1;
  min-height: 44px;
  clip-path: var(--clip-sm);
  border: 1px solid var(--border-subtle);
  background: none;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
}
.gmodal-btn:hover { border-color: var(--accent-primary); color: var(--accent-bright); }
.gmodal-btn--primary {
  background: var(--amber);
  border-color: var(--amber);
  color: var(--on-amber);
  font-weight: 700;
}
.gmodal-btn--primary:hover { filter: brightness(1.1); color: var(--on-amber); }

.modal-enter-active,
.modal-leave-active { transition: opacity 200ms; }
.modal-enter-from,
.modal-leave-to { opacity: 0; }

/* ===== 移动端 ===== */
@media (max-width: 640px) {
  .gtl__nodes {
    grid-template-columns: 1fr;
  }
}
</style>
