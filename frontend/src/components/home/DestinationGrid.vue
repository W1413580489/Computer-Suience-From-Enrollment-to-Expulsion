<template>
  <section class="dest">
    <header class="dest__header">
      <span class="dest__num">// DESTINATIONS</span>
      <h2 class="dest__title">四大目的地</h2>
    </header>

    <div class="dest__grid">
      <!-- 01 入学指南 — 左对齐，宽 -->
      <button class="dcard dcard--01" @click="go(quests[0].route)">
        <span class="dcard__num">01</span>
        <div class="dcard__body">
          <span class="dcard__en">NEW STUDENT</span>
          <h3 class="dcard__cn">入学指南</h3>
          <p class="dcard__desc">新生报到 · 学院制度 · 培养方案</p>
        </div>
        <span class="dcard__cta">EXPLORE →</span>
        <span class="dcard__shape dcard__shape--01" />
      </button>

      <!-- 02 学业规划 — 右对齐，偏移 -->
      <button class="dcard dcard--02" @click="go(quests[1].route)">
        <span class="dcard__num">02</span>
        <div class="dcard__body">
          <span class="dcard__en">ACADEMIC / FUTURE</span>
          <h3 class="dcard__cn">学业规划</h3>
          <p class="dcard__desc">课程 · 成绩 · 保研 · 考研 · 就业</p>
        </div>
        <span class="dcard__cta">EXPLORE →</span>
        <span class="dcard__shape dcard__shape--02" />
      </button>

      <!-- 03 资源中心 — 居中，窄 -->
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

      <!-- 04 校园生活 — 右对齐，宽 -->
      <button class="dcard dcard--04" @click="go(quests[3].route)">
        <span class="dcard__num">04</span>
        <div class="dcard__body">
          <span class="dcard__en">CAMPUS LIFE</span>
          <h3 class="dcard__cn">校园生活</h3>
          <p class="dcard__desc">社团 · 活动 · 地图 · 学院资讯</p>
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
  padding: 24px 24px 32px;
  max-width: 920px;
  margin: 0 auto;
  width: 100%;
}

.dest__header {
  display: flex;
  align-items: baseline;
  gap: 14px;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.dest__num {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--amber);
}

.dest__title {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 500;
  letter-spacing: 3px;
  color: var(--text-primary);
  text-transform: uppercase;
}

/* ---- 不对称网格 ---- */
.dest__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* ---- 通用卡片 ---- */
.dcard {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 22px 24px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  text-align: left;
  transition: border-color 200ms, background 200ms, transform 200ms;
  overflow: hidden;
  min-height: 140px;
}

.dcard:hover {
  border-color: var(--amber);
  background: var(--bg-panel-2);
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
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--text-muted);
  text-transform: uppercase;
}

.dcard__cn {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--text-primary);
}

.dcard__desc {
  font-size: 12px;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
  margin-top: 2px;
}

.dcard__cta {
  margin-top: auto;
  font-family: var(--font-mono);
  font-size: 11px;
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

/* ---- 不对称位移 ---- */
.dcard--01 {
  clip-path: polygon(var(--cut-lg) 0, 100% 0, 100% 100%, 0 100%, 0 var(--cut-lg));
  margin-right: 24px;
}

.dcard--02 {
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - var(--cut-lg)), calc(100% - var(--cut-lg)) 100%, 0 100%);
  margin-top: 32px;
  margin-left: 24px;
  text-align: right;
  align-items: flex-end;
}

.dcard--02 .dcard__body {
  align-items: flex-end;
}

.dcard--03 {
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% 100%, 0 100%, 0 var(--cut-md));
  grid-column: 1 / -1;
  max-width: 70%;
  margin: 0 auto;
  text-align: center;
  align-items: center;
}

.dcard--03 .dcard__body {
  align-items: center;
}

.dcard--04 {
  clip-path: polygon(0 0, 100% 0, 100% 100%, calc(100% - var(--cut-lg)) 100%, 0 calc(100% - var(--cut-lg)));
  grid-column: 1 / -1;
  margin-left: auto;
  max-width: 75%;
  text-align: right;
  align-items: flex-end;
}

.dcard--04 .dcard__body {
  align-items: flex-end;
}

/* ---- 装饰几何图形 — 平面设计感 ---- */
.dcard__shape {
  position: absolute;
  pointer-events: none;
  z-index: 1;
  opacity: 0.5;
}

.dcard__shape--01 {
  top: 16px;
  right: 16px;
  width: 40px;
  height: 40px;
  border: 1.5px solid var(--amber);
  clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%);
}

.dcard__shape--02 {
  top: 16px;
  left: 16px;
  width: 36px;
  height: 36px;
  border: 1.5px solid var(--neon-cyan);
  transform: rotate(45deg);
  opacity: 0.4;
}

.dcard__shape--03 {
  top: 50%;
  right: 20px;
  transform: translateY(-50%);
  width: 3px;
  height: 50px;
  background: var(--amber);
  opacity: 0.6;
}

.dcard__shape--04 {
  bottom: 16px;
  left: 16px;
  width: 50px;
  height: 1.5px;
  background: var(--amber);
}

.dcard--04 .dcard__shape--04::after {
  content: '';
  position: absolute;
  left: 0;
  top: 6px;
  width: 30px;
  height: 1.5px;
  background: var(--amber);
  opacity: 0.5;
}

/* ---- 响应式 ---- */
@media (max-width: 767px) {
  .dest {
    padding: 16px 16px 24px;
  }

  .dest__header {
    margin-bottom: 16px;
  }

  .dest__title {
    font-size: 18px;
  }

  .dest__grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .dcard {
    min-height: 110px;
    padding: 18px 20px;
  }

  .dcard--01,
  .dcard--02,
  .dcard--03,
  .dcard--04 {
    margin: 0;
    max-width: 100%;
    text-align: left;
    align-items: flex-start;
  }

  .dcard--02 .dcard__body,
  .dcard--03 .dcard__body,
  .dcard--04 .dcard__body {
    align-items: flex-start;
  }

  .dcard--03 {
    grid-column: auto;
  }

  .dcard--04 {
    grid-column: auto;
  }

  .dcard__num {
    font-size: 28px;
  }

  .dcard__cn {
    font-size: 18px;
  }
}
</style>
