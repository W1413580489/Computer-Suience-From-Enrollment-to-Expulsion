<template>
  <PageShell title="成长路线图" subtitle="ROADMAP · 先定目标，再走时间线" active-key="roadmap">
    <div class="roadmap">
      <!-- 阶段一：目标选择轮播 -->
      <Transition name="phase-zoom" mode="out-in">
        <GoalCarousel
          v-if="phase === 'select'"
          :goals="goals"
          @select="onSelectGoal"
        />

        <!-- 阶段二：目标专属时间线 -->
        <GoalTimeline
          v-else-if="phase === 'timeline' && activeGoal"
          :key="activeGoal.id"
          :goal="activeGoal"
          @back="phase = 'select'"
          @enter-skill-tree="phase = 'skilltree'"
        />

        <!-- 阶段三：项目实战技能树 -->
        <SkillTreePanel
          v-else
          @back="phase = 'timeline'"
        />
      </Transition>
    </div>
  </PageShell>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import PageShell from '@/components/common/PageShell.vue';
import GoalCarousel from '@/components/roadmap/GoalCarousel.vue';
import GoalTimeline from '@/components/roadmap/GoalTimeline.vue';
import SkillTreePanel from '@/components/roadmap/SkillTreePanel.vue';
import { roadmapGoals, type RoadmapGoal } from '@/data/roadmapData';
import { useAchievementStore } from '@/stores/achievementStore';

const goals = roadmapGoals;
const phase = ref<'select' | 'timeline' | 'skilltree'>('select');
const activeGoal = ref<RoadmapGoal | null>(null);

// 成就映射：目标ID → 成就ID
const goalAchievements: Record<string, string> = {
  career: 'love_working',
  kaoyan: 'study_spring',
  baoyan: 'poetry_zhang',
  startup: 'mountain_pressure',
};

// 点击目标卡片 → 卡片展开动画（GoalCarousel 内部处理）→ 进入时间线
function onSelectGoal(goal: RoadmapGoal) {
  activeGoal.value = goal;
  phase.value = 'timeline';
  scrollToTop();
  // 成就：首次点击对应路线
  const achId = goalAchievements[goal.id];
  if (achId) useAchievementStore().unlock(achId);
}

function scrollToTop() {
  const body = document.querySelector('.hud-page-body');
  if (body) body.scrollTop = 0;
}
</script>

<style scoped>
.roadmap {
  min-height: 50vh;
}

/* 阶段切换：缩放 + 透明度（模拟卡片展开进入） */
.phase-zoom-enter-active {
  transition: opacity 260ms ease, transform 260ms cubic-bezier(0.22, 1, 0.36, 1);
}
.phase-zoom-leave-active {
  transition: opacity 160ms ease, transform 160ms ease;
}
.phase-zoom-enter-from {
  opacity: 0;
  transform: scale(1.045);
}
.phase-zoom-leave-to {
  opacity: 0;
  transform: scale(0.985);
}
</style>
