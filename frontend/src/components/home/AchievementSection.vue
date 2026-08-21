<template>
  <section class="ach">
    <SectionHeader num="05" title="成就系统" en="ACHIEVEMENTS" />

    <!-- 缓存提示 -->
    <div class="ach__notice">
      <NeonIcon name="info" :size="14" />
      <span>清除浏览器缓存后，成就数据也会消失</span>
    </div>

    <!-- 票据网格 -->
    <div v-if="unlocked.length > 0" class="ach__grid">
      <div
        v-for="a in pagedItems"
        :key="a.id"
        class="ach__ticket"
        :class="`ach__ticket--${theme.isZzz ? 'zzz' : 'ak'}`"
      >
        <!-- 主区 -->
        <div class="ach__ticket-main">
          <div class="ach__ticket-badges">
            <span class="ach__badge" :class="`ach__badge--${a.badgeColor}`">{{ a.badge }}</span>
            <span class="ach__badge ach__badge--dark">ACHIEVED</span>
          </div>
          <h3 class="ach__ticket-title">{{ a.title }}</h3>
          <p class="ach__ticket-desc">{{ a.desc }}</p>
          <div class="ach__ticket-foot">
            <span class="ach__ticket-date">解锁于 {{ formatDate(a.id) }}</span>
          </div>
        </div>
        <!-- 票根 -->
        <div class="ach__ticket-stub">
          <span class="ach__ticket-stub-label">{{ a.stubLabel }}</span>
        </div>
      </div>

      <!-- 空槽位（不足 3 个时占位） -->
      <div
        v-for="n in emptySlots"
        :key="`empty-${n}`"
        class="ach__ticket ach__ticket--empty"
        :class="`ach__ticket--${theme.isZzz ? 'zzz' : 'ak'}`"
      >
        <div class="ach__ticket-main ach__ticket-main--empty">
          <span class="ach__ticket-empty-text">— EMPTY SLOT —</span>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="ach__empty">
      <NeonIcon name="info" :size="32" />
      <p>暂未获得任何成就，探索网站以解锁</p>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="ach__pagination">
      <button
        class="ach__page-btn"
        :disabled="page === 1"
        aria-label="上一页"
        @click="page--"
      >
        <NeonIcon name="arrow-left" :size="16" />
      </button>
      <span class="ach__page-indicator">{{ page }} / {{ totalPages }}</span>
      <button
        class="ach__page-btn"
        :disabled="page === totalPages"
        aria-label="下一页"
        @click="page++"
      >
        <NeonIcon name="arrow-right" :size="16" />
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import SectionHeader from './SectionHeader.vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import { useThemeStore } from '@/stores/themeStore';
import {
  getUnlockedAchievements,
  subscribeAchievements,
  type AchievementDef,
} from '@/data/achievements';

const theme = useThemeStore();

const unlocked = ref<AchievementDef[]>([]);
const unlockedAtMap = ref<Record<string, string>>({});
const page = ref(1);

const PAGE_SIZE = 3;

const totalPages = computed(() => Math.max(1, Math.ceil(unlocked.value.length / PAGE_SIZE)));

const pagedItems = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE;
  return unlocked.value.slice(start, start + PAGE_SIZE);
});

const emptySlots = computed(() => {
  if (unlocked.value.length === 0) return 0;
  return Math.max(0, PAGE_SIZE - pagedItems.value.length);
});

function formatDate(id: string): string {
  const iso = unlockedAtMap.value[id];
  if (!iso) return '';
  const d = new Date(iso);
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${mm}-${dd}`;
}

function refresh() {
  // 读取 localStorage 原始数据获取解锁时间
  try {
    const raw = localStorage.getItem('xkz_achievements');
    if (raw) {
      const store = JSON.parse(raw);
      unlockedAtMap.value = Object.fromEntries(
        Object.entries(store).map(([k, v]: [string, any]) => [k, v.unlockedAt ?? '']),
      );
    }
  } catch {
    // ignore
  }
  const prevCount = unlocked.value.length;
  unlocked.value = getUnlockedAchievements();
  // 如果新解锁了成就，回到第一页查看最新
  if (unlocked.value.length > prevCount) {
    page.value = 1;
  }
  // 防止页码越界
  if (page.value > totalPages.value) {
    page.value = totalPages.value;
  }
}

let unsubscribe: (() => void) | null = null;

onMounted(() => {
  refresh();
  unsubscribe = subscribeAchievements(refresh);
});

onUnmounted(() => {
  if (unsubscribe) unsubscribe();
});

// 暴露刷新方法供父组件触发
defineExpose({ refresh });
</script>

<style scoped>
.ach {
  padding: 32px 32px 64px;
  max-width: 1120px;
  margin: 0 auto;
  width: 100%;
}

/* 缓存提示 */
.ach__notice {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  margin-bottom: 24px;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-muted);
  background: var(--amber-deep-soft);
  border-left: 2px solid var(--amber);
  clip-path: var(--clip-sm);
}

/* ====== 票据网格 ====== */
.ach__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

/* ====== 票据卡片 ====== */
.ach__ticket {
  display: flex;
  overflow: hidden;
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
}

/* ZZZ 夜间 */
.ach__ticket--zzz {
  background: var(--bg-panel);
  border-bottom: 2px solid var(--amber);
}

/* AK 日间：浅色玻璃卡 + 发丝红描边 + 柔和阴影，对齐其他模块 */
.ach__ticket--ak {
  background: var(--card-surface);
  border: 1px solid var(--card-border);
  border-bottom: 3px solid var(--amber-deep);
  box-shadow: var(--shadow-card);
}

/* 主区 */
.ach__ticket-main {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
}

/* 票根 */
.ach__ticket-stub {
  width: 64px;
  padding: 20px 12px;
  background: var(--bg-panel-2);
  border-left: 2px dashed var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: center;
}

.ach__ticket--ak .ach__ticket-stub {
  background: var(--bg-panel-3);
  border-left: 2px dashed var(--border-subtle);
}

.ach__ticket-stub-label {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-muted);
  writing-mode: vertical-rl;
  text-orientation: mixed;
  letter-spacing: 0.2em;
  font-weight: 700;
}

/* 徽章 */
.ach__ticket-badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.ach__badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  clip-path: polygon(var(--cut-sm) 0, 100% 0, 100% calc(100% - var(--cut-sm)), calc(100% - var(--cut-sm)) 100%, 0 100%, 0 var(--cut-sm));
}

.ach__badge--yellow { background: var(--amber); color: var(--on-amber); }
.ach__badge--cyan { background: var(--neon-cyan); color: #0A0A0A; }
.ach__badge--magenta { background: var(--neon-magenta); color: #0A0A0A; }
.ach__badge--dark { background: var(--bg-panel-3); color: var(--text-secondary); border: 1px solid var(--border-subtle); }

/* AK 日间：亮色徽章的青/青绿偏中色调，文字用白保证可读 */
.ach__ticket--ak .ach__badge--cyan,
.ach__ticket--ak .ach__badge--magenta {
  color: #FFFFFF;
}

/* AK 日间：深色徽章用浅灰底板 + 发丝描边，文字为中灰 */
.ach__ticket--ak .ach__badge--dark {
  background: var(--bg-panel-3);
  color: var(--text-secondary);
  border: 1px solid var(--border-subtle);
}

/* 标题 */
.ach__ticket-title {
  font-family: var(--font-display);
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  line-height: 1.3;
}

.ach__ticket--ak .ach__ticket-title {
  color: var(--text-primary);
}

/* 描述 */
.ach__ticket-desc {
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-secondary);
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.ach__ticket--ak .ach__ticket-desc {
  color: var(--text-secondary);
}

/* 底部日期 */
.ach__ticket-foot {
  display: flex;
  justify-content: flex-start;
}

.ach__ticket-date {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 0.1em;
}

.ach__ticket--ak .ach__ticket-date {
  color: var(--text-muted);
}

/* 空槽位 */
.ach__ticket--empty {
  opacity: 0.4;
}

.ach__ticket-main--empty {
  align-items: center;
  justify-content: center;
}

.ach__ticket-empty-text {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 0.3em;
}

/* 空状态 */
.ach__empty {
  padding: 48px 16px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.ach__empty p {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

/* 分页 */
.ach__pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}

.ach__page-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--bg-panel-2);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  cursor: pointer;
  clip-path: var(--clip-sm);
  transition: all 200ms;
}

.ach__page-btn:hover:not(:disabled) {
  background: var(--amber);
  color: var(--on-amber);
  border-color: var(--amber);
}

.ach__page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.ach__page-indicator {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--text-secondary);
  letter-spacing: 0.15em;
  min-width: 60px;
  text-align: center;
}

/* ====== 响应式：手机端纵向 ====== */
@media (max-width: 767px) {
  .ach {
    padding: 24px 16px 48px;
  }

  .ach__grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  /* 手机端隐藏空槽位 */
  .ach__ticket--empty {
    display: none;
  }

  .ach__ticket-title {
    font-size: 16px;
  }
}
</style>
