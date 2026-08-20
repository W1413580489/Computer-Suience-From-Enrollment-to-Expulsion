<template>
  <section class="dest" id="destinations">
    <SectionHeader num="01" title="目的地" en="DESTINATIONS" />

    <div class="dest__grid">
      <!-- 01 年级驱动卡片 — 左上 -->
      <div
        v-if="userStore.isLoggedIn && userStore.isSoftware"
        class="dcard dcard--01"
        role="button"
        tabindex="0"
        @click="openGradeUrl"
        @keydown.enter="openGradeUrl"
      >
        <span class="dcard__num">01</span>
        <div class="dcard__body">
          <span class="dcard__en">{{ gradeCard.en }}</span>
          <h3 class="dcard__cn">{{ gradeCard.title }}</h3>
          <p class="dcard__desc">{{ gradeCard.desc }}</p>
        </div>
        <z-button v-if="theme.isZzz" size="mini" class="dcard__zcta" @click.stop="openGradeUrl">EXPLORE</z-button>
        <span v-else class="dcard__cta">EXPLORE →</span>
        <span class="dcard__shape dcard__shape--01" />
      </div>
      <!-- 01 默认（游客/硬件/其他类） -->
      <div v-else class="dcard dcard--01" role="button" tabindex="0" @click="go(quests[0].route)" @keydown.enter="go(quests[0].route)">
        <span class="dcard__num">01</span>
        <div class="dcard__body">
          <span class="dcard__en">NEW QUEST</span>
          <h3 class="dcard__cn">新手任务</h3>
          <p class="dcard__desc">账号登录 · 关卡解锁 · 入学指南</p>
        </div>
        <z-button v-if="theme.isZzz" size="mini" class="dcard__zcta" @click.stop="go(quests[0].route)">EXPLORE</z-button>
        <span v-else class="dcard__cta">EXPLORE →</span>
        <span class="dcard__shape dcard__shape--01" />
      </div>

      <!-- 02 攻略 — 右上 -->
      <div class="dcard dcard--02" role="button" tabindex="0" @click="go(quests[1].route)" @keydown.enter="go(quests[1].route)">
        <span class="dcard__num">02</span>
        <div class="dcard__body">
          <span class="dcard__en">GUIDE</span>
          <h3 class="dcard__cn">攻略</h3>
          <p class="dcard__desc">全部指南 · 图文教程</p>
        </div>
        <z-button v-if="theme.isZzz" size="mini" class="dcard__zcta" @click.stop="go(quests[1].route)">EXPLORE</z-button>
        <span v-else class="dcard__cta">EXPLORE →</span>
        <span class="dcard__shape dcard__shape--02" />
      </div>

      <!-- 03 资源中心 — 左下 -->
      <div class="dcard dcard--03" role="button" tabindex="0" @click="go(quests[2].route)" @keydown.enter="go(quests[2].route)">
        <span class="dcard__num">03</span>
        <div class="dcard__body">
          <span class="dcard__en">RESOURCE</span>
          <h3 class="dcard__cn">资源中心</h3>
          <p class="dcard__desc">网站 · 软件 · 学习资料</p>
        </div>
        <z-button v-if="theme.isZzz" size="mini" class="dcard__zcta" @click.stop="go(quests[2].route)">EXPLORE</z-button>
        <span v-else class="dcard__cta">EXPLORE →</span>
        <span class="dcard__shape dcard__shape--03" />
      </div>

      <!-- 04 附录 — 右下 -->
      <div class="dcard dcard--04" role="button" tabindex="0" @click="go(quests[3].route)" @keydown.enter="go(quests[3].route)">
        <span class="dcard__num">04</span>
        <div class="dcard__body">
          <span class="dcard__en">APPENDIX</span>
          <h3 class="dcard__cn">附录</h3>
          <p class="dcard__desc">表格 · 政策 · 补充文档</p>
        </div>
        <z-button v-if="theme.isZzz" size="mini" class="dcard__zcta" @click.stop="go(quests[3].route)">EXPLORE</z-button>
        <span v-else class="dcard__cta">EXPLORE →</span>
        <span class="dcard__shape dcard__shape--04" />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import SectionHeader from './SectionHeader.vue';
import { useThemeStore } from '@/stores/themeStore';
import { useUserStore } from '@/stores/userStore';
import { gradeCardContent } from '@/data/gradeContent';

const router = useRouter();
const theme = useThemeStore();
const userStore = useUserStore();

const quests = [
  { route: '/quest' },
  { route: '/guides' },
  { route: '/resources' },
  { route: '/appendix' },
];

const gradeCard = computed(() => {
  if (!userStore.user) return gradeCardContent[1];
  return gradeCardContent[userStore.user.grade] ?? gradeCardContent[1];
});

function go(route: string) {
  router.push(route);
}

function openGradeUrl() {
  if (gradeCard.value.url) {
    window.open(gradeCard.value.url, '_blank', 'noopener');
  }
}
</script>

<style scoped>
.dest {
  padding: 40px 32px 80px;
  max-width: 1120px;
  margin: 0 auto;
  width: 100%;
}

/* ---- 田字格 2×2 ---- */
.dest__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

/* ---- 卡片：半透明玻璃面板（背景/描边随主题切换） ---- */
.dcard {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px 22px;
  background: var(--card-surface);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  border: 1px solid var(--card-border);
  color: var(--text-primary);
  text-align: left;
  cursor: pointer;
  transition: border-color 200ms, background 200ms, transform 200ms;
  overflow: hidden;
  min-height: 118px;
}

/* zenless-ui CTA：贴底左对齐 */
.dcard__zcta {
  margin-top: auto;
  align-self: flex-start;
  position: relative;
  z-index: 2;
}

.dcard:hover {
  border-color: var(--amber);
  background: var(--card-surface-hover);
  transform: translateY(-3px);
}

.dcard:active {
  transform: translateY(0);
}

.dcard__num {
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 900;
  line-height: 1;
  color: var(--amber);
  opacity: 0.9;
}

.dcard__body {
  display: flex;
  flex-direction: column;
  gap: 3px;
  position: relative;
  z-index: 2;
}

.dcard__en {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--text-muted);
  text-transform: uppercase;
}

.dcard__cn {
  font-size: 23px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--text-primary);
}

.dcard__desc {
  font-size: 13.5px;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
  margin-top: 2px;
}

.dcard__cta {
  margin-top: auto;
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--amber);
  opacity: 0.7;
  transition: opacity 200ms, transform 200ms;
  position: relative;
  z-index: 2;
}

.dcard:hover .dcard__cta {
  opacity: 1;
  transform: translateX(4px);
}

/* 拼图式斜切角：四卡角部斜切留 X 形缝隙 */
.dcard--01 {
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% 100%, 0 100%, 0 var(--cut-md));
}

.dcard--02 {
  clip-path: polygon(0 0, calc(100% - var(--cut-md)) 0, 100% var(--cut-md), 100% 100%, 0 100%);
}

.dcard--03 {
  clip-path: polygon(0 0, 100% 0, 100% 100%, var(--cut-md) 100%, 0 calc(100% - var(--cut-md)));
}

.dcard--04 {
  clip-path: polygon(0 0, 100% 0, calc(100% - var(--cut-md)) 100%, 0 100%);
}

/* ---- 装饰几何图形 ---- */
.dcard__shape {
  position: absolute;
  pointer-events: none;
  z-index: 1;
  opacity: 0.5;
}

.dcard__shape--01 {
  top: 14px;
  right: 14px;
  width: 36px;
  height: 36px;
  border: 1.5px solid var(--amber);
  clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%);
}

.dcard__shape--02 {
  top: 14px;
  right: 14px;
  width: 32px;
  height: 32px;
  border: 1.5px solid var(--neon-cyan);
  transform: rotate(45deg);
  opacity: 0.4;
}

.dcard__shape--03 {
  bottom: 14px;
  right: 18px;
  width: 3px;
  height: 44px;
  background: var(--amber);
  opacity: 0.6;
}

.dcard__shape--04 {
  bottom: 14px;
  right: 14px;
  width: 46px;
  height: 1.5px;
  background: var(--amber);
}

/* ---- 响应式 ---- */
@media (max-width: 767px) {
  .dest {
    padding: 48px 16px;
  }

  .dest__grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .dcard {
    min-height: 104px;
    padding: 16px 18px;
  }

  .dcard--01,
  .dcard--02,
  .dcard--03,
  .dcard--04 {
    clip-path: polygon(var(--cut-sm) 0, 100% 0, 100% calc(100% - var(--cut-sm)), calc(100% - var(--cut-sm)) 100%, 0 100%, 0 var(--cut-sm));
  }

  .dcard__num {
    font-size: 28px;
  }

  .dcard__cn {
    font-size: 19px;
  }
}
</style>
