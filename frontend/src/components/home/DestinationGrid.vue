<template>
  <section class="dest">
    <header class="dest__header">
      <span class="dest__num">// DESTINATIONS</span>
      <h2 class="dest__title">目的地</h2>
    </header>

    <div class="dest__grid">
      <!-- 01 新手任务 — 左上 -->
      <button class="dcard dcard--01" @click="go(quests[0].route)">
        <span class="dcard__num">01</span>
        <div class="dcard__body">
          <span class="dcard__en">NEW QUEST</span>
          <h3 class="dcard__cn">新手任务</h3>
          <p class="dcard__desc">账号登录 · 关卡解锁 · 入学指南</p>
        </div>
        <span class="dcard__cta">EXPLORE →</span>
        <span class="dcard__shape dcard__shape--01" />
      </button>

      <!-- 02 攻略 — 右上 -->
      <button class="dcard dcard--02" @click="go(quests[1].route)">
        <span class="dcard__num">02</span>
        <div class="dcard__body">
          <span class="dcard__en">GUIDE</span>
          <h3 class="dcard__cn">攻略</h3>
          <p class="dcard__desc">全部指南 · 图文教程</p>
        </div>
        <span class="dcard__cta">EXPLORE →</span>
        <span class="dcard__shape dcard__shape--02" />
      </button>

      <!-- 03 资源中心 — 左下（01 下方） -->
      <button class="dcard dcard--03" @click="go(quests[2].route)">
        <span class="dcard__num">03</span>
        <div class="dcard__body">
          <span class="dcard__en">RESOURCE</span>
          <h3 class="dcard__cn">资源中心</h3>
          <p class="dcard__desc">网站 · 软件 · 学习资料</p>
        </div>
        <span class="dcard__cta">EXPLORE →</span>
        <span class="dcard__shape dcard__shape--03" />
      </button>

      <!-- 04 附录 — 右下（02 下方） -->
      <button class="dcard dcard--04" @click="go(quests[3].route)">
        <span class="dcard__num">04</span>
        <div class="dcard__body">
          <span class="dcard__en">APPENDIX</span>
          <h3 class="dcard__cn">附录</h3>
          <p class="dcard__desc">表格 · 政策 · 补充文档</p>
        </div>
        <span class="dcard__cta">EXPLORE →</span>
        <span class="dcard__shape dcard__shape--04" />
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const quests = [
  { route: '/quest' },
  { route: '/guides' },
  { route: '/resources' },
  { route: '/appendix' },
];

function go(route: string) {
  router.push(route);
}
</script>

<style scoped>
.dest {
  padding: 32px 32px 40px;
  max-width: 1120px;
  margin: 0 auto;
  width: 100%;
}

.dest__header {
  display: flex;
  align-items: baseline;
  gap: 14px;
  margin-bottom: 22px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-subtle);
}

.dest__num {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--amber);
}

.dest__title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 500;
  letter-spacing: 3px;
  color: var(--text-primary);
  text-transform: uppercase;
}

/* ---- 桌面端：田字格 2×2 ---- */
.dest__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

/* ---- 通用卡片：半透明玻璃面板，不遮死背景光晕 ---- */
.dcard {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px 22px;
  background: rgba(18, 18, 18, 0.72);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  border: 1px solid rgba(255, 217, 61, 0.14);
  color: var(--text-primary);
  text-align: left;
  transition: border-color 200ms, background 200ms, transform 200ms;
  overflow: hidden;
  min-height: 118px;
}

.dcard:hover {
  border-color: var(--amber);
  background: rgba(26, 26, 26, 0.85);
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

/* ---- 拼图式斜切角：四卡组成规整 2×2，角部斜切留出 X 形缝隙 ---- */
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

/* ---- 装饰几何图形 — 平面设计感 ---- */
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

.dcard--04 .dcard__shape--04::after {
  content: '';
  position: absolute;
  left: 0;
  top: 6px;
  width: 28px;
  height: 1.5px;
  background: var(--amber);
  opacity: 0.5;
}

/* ---- 响应式：小屏/移动端单列，不强制田字格 ---- */
@media (max-width: 767px) {
  .dest {
    padding: 24px 16px 28px;
  }

  .dest__header {
    margin-bottom: 14px;
  }

  .dest__title {
    font-size: 18px;
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
    font-size: 26px;
  }

  .dcard__cn {
    font-size: 18px;
  }
}
</style>
