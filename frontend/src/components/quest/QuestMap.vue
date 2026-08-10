<template>
  <div class="map-wrap">
    <div class="map-hint">示意地图 · 非精确地理位置</div>
    <svg viewBox="0 0 600 420" class="map-svg">
      <defs>
        <!-- Glow filter -->
        <filter id="glow">
          <feGaussianBlur stdDeviation="2.5" result="blur"/>
          <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <filter id="glow-amber">
          <feGaussianBlur stdDeviation="3" result="blur"/>
          <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <!-- Pulse animation for explored locations -->
        <radialGradient id="pulse">
          <stop offset="0%" stop-color="var(--amber)" stop-opacity=".6"/>
          <stop offset="100%" stop-color="var(--amber)" stop-opacity="0"/>
        </radialGradient>
      </defs>

      <!-- Background grid -->
      <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
        <path d="M 20 0 L 0 0 0 20" fill="none" stroke="var(--border-subtle)" stroke-width=".4" opacity=".3"/>
      </pattern>
      <rect width="600" height="420" fill="var(--bg-primary)"/>
      <rect width="600" height="420" fill="url(#grid)"/>

      <!-- === Mirror Lake (center anchor) === -->
      <ellipse cx="300" cy="240" rx="90" ry="50" fill="#1A3D5C" stroke="#2A6DA8" stroke-width="1.5" opacity=".8"/>
      <text x="300" y="244" text-anchor="middle" fill="#4A9ACC" font-size="10" font-family="var(--font-display)" opacity=".7">镜 湖</text>

      <!-- Bridges -->
      <line x1="250" y1="215" x2="240" y2="200" stroke="#4A9ACC" stroke-width="1" opacity=".5"/>
      <line x1="350" y1="215" x2="360" y2="200" stroke="#4A9ACC" stroke-width="1" opacity=".5"/>

      <!-- Roads (glow lines) -->
      <path d="M 80 300 L 220 300 L 220 260 L 210 240" fill="none" stroke="var(--amber-glow)" stroke-width="1" opacity=".25"/>
      <path d="M 300 190 L 300 120 L 380 120 L 380 200" fill="none" stroke="var(--amber-glow)" stroke-width="1" opacity=".25"/>
      <path d="M 300 290 L 300 350 L 480 350 L 480 280" fill="none" stroke="var(--amber-glow)" stroke-width="1" opacity=".25"/>

      <!-- === Locations === -->
      <!-- 2.1 图书馆北侧 -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.1') }" @click="clickLoc({ id: '2.1', name: '图书馆北侧', desc: '自主学习空间 / 研修间预约 / 自助借还' })">
        <rect x="215" y="130" width="55" height="35" rx="4" fill="var(--bg-panel)" stroke="var(--border-glow)" stroke-width="1" class="loc__rect"/>
        <text x="242" y="152" text-anchor="middle" fill="var(--text-secondary)" font-size="11">2.1 图书馆北侧</text>
        <circle cx="270" cy="130" r="4" fill="var(--amber)"/>
      </g>

      <!-- 2.2 快递站 -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.2') }" @click="clickLoc({ id: '2.2', name: '快递站', desc: 'T11架空层 · 菜鸟驿站 · 取件码自助' })">
        <rect x="430" y="70" width="55" height="35" rx="4" fill="var(--bg-panel)" stroke="var(--border-glow)" stroke-width="1" class="loc__rect"/>
        <text x="457" y="92" text-anchor="middle" fill="var(--text-secondary)" font-size="11">2.2 快递站</text>
        <circle cx="430" cy="70" r="4" fill="var(--amber)"/>
      </g>

      <!-- 2.3 校友会 -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.3') }" @click="clickLoc({ id: '2.3', name: '校友会', desc: '校友联络 · 捐赠事务 · 校友活动中心' })">
        <rect x="460" y="170" width="55" height="35" rx="4" fill="var(--bg-panel)" stroke="var(--border-glow)" stroke-width="1" class="loc__rect"/>
        <text x="487" y="192" text-anchor="middle" fill="var(--text-secondary)" font-size="11">2.3 校友会</text>
        <circle cx="515" cy="170" r="4" fill="var(--amber)"/>
      </g>

      <!-- 2.4 知识产权大楼 -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.4') }" @click="clickLoc({ id: '2.4', name: '知识产权大楼', desc: '知识产权学院 · 专利检索中心 · 学术报告厅' })">
        <rect x="80" y="230" width="65" height="35" rx="4" fill="var(--bg-panel)" stroke="var(--border-glow)" stroke-width="1" class="loc__rect"/>
        <text x="112" y="252" text-anchor="middle" fill="var(--text-secondary)" font-size="10">2.4 知识产权</text>
        <circle cx="80" cy="230" r="4" fill="var(--amber)"/>
      </g>

      <!-- 2.5 实验室 -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.5') }" @click="clickLoc({ id: '2.5', name: '实验室', desc: '物联网/大数据/网络安全实验室 · A类竞赛孵化的核心场地' })">
        <rect x="60" y="110" width="55" height="35" rx="4" fill="var(--bg-panel)" stroke="var(--border-glow)" stroke-width="1" class="loc__rect"/>
        <text x="87" y="132" text-anchor="middle" fill="var(--text-secondary)" font-size="11">2.5 实验室</text>
        <circle cx="60" cy="110" r="4" fill="var(--amber)"/>
      </g>

      <!-- 2.6 镜湖 (already drawn as center piece) -->
      <!-- Pin on lake to mark it as explorable -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.6') }" @click="clickLoc({ id: '2.6', name: '镜湖', desc: '校园中心湖 · 散步发呆好去处 · 博雅桥/博文桥连接两岸' })">
        <rect x="245" y="205" width="55" height="25" rx="4" fill="var(--bg-panel)" stroke="var(--amber)" stroke-width="1" class="loc__rect"/>
        <text x="272" y="222" text-anchor="middle" fill="var(--amber)" font-size="10">2.6 镜湖</text>
        <circle cx="300" cy="240" r="6" fill="none" stroke="var(--amber)" stroke-width="1.5" opacity=".6">
          <animate attributeName="r" values="6;10;6" dur="2s" repeatCount="indefinite"/>
        </circle>
      </g>

      <!-- 2.7 教学楼 -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.7') }" @click="clickLoc({ id: '2.7', name: '教学楼', desc: '主要上课区域 · 多媒体教室 · 自习室 · 机房' })">
        <rect x="370" y="200" width="55" height="35" rx="4" fill="var(--bg-panel)" stroke="var(--border-glow)" stroke-width="1" class="loc__rect"/>
        <text x="397" y="222" text-anchor="middle" fill="var(--text-secondary)" font-size="11">2.7 教学楼</text>
        <circle cx="370" cy="200" r="4" fill="var(--amber)"/>
      </g>

      <!-- 2.8 图书馆 -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.8') }" @click="clickLoc({ id: '2.8', name: '图书馆', desc: '惠全楼图书馆 · 自习/借阅/研讨间 · 开放至22:00' })">
        <rect x="370" y="140" width="55" height="35" rx="4" fill="var(--bg-panel)" stroke="var(--amber)" stroke-width="1.5" class="loc__rect"/>
        <text x="397" y="162" text-anchor="middle" fill="var(--amber)" font-size="11">2.8 图书馆</text>
        <circle cx="425" cy="140" r="5" fill="var(--amber)" filter="url(#glow-amber)"/>
      </g>

      <!-- 2.9 操场 -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.9') }" @click="clickLoc({ id: '2.9', name: '操场', desc: '田径场 · 篮球场 · 体测场地 · 运动会举办地' })">
        <rect x="460" y="290" width="55" height="35" rx="4" fill="var(--bg-panel)" stroke="var(--border-glow)" stroke-width="1" class="loc__rect"/>
        <text x="487" y="312" text-anchor="middle" fill="var(--text-secondary)" font-size="11">2.9 操场</text>
        <ellipse cx="515" cy="255" rx="35" ry="20" fill="none" stroke="var(--border-subtle)" stroke-width="1" opacity=".5"/>
      </g>

      <!-- South Gate marker -->
      <text x="300" y="395" text-anchor="middle" fill="var(--text-muted)" font-size="10" opacity=".5">▼ 南门 / 公交站 ▼</text>

      <!-- Compass -->
      <text x="560" y="22" text-anchor="middle" fill="var(--text-muted)" font-size="18">N</text>
      <line x1="560" y1="26" x2="560" y2="50" stroke="var(--text-muted)" stroke-width="1" opacity=".4"/>
      <polygon points="560,50 555,42 565,42" fill="var(--text-muted)" opacity=".4"/>
    </svg>

    <!-- Info popup -->
    <div v-if="popup" class="map-popup" @click="popup = null">
      <div class="map-popup__card" @click.stop>
        <h3>{{ popup.name }}</h3>
        <p>{{ popup.desc }}</p>
        <span class="map-popup__tag" :class="{ 'map-popup__tag--done': isExplored(popup.id) }">
          {{ isExplored(popup.id) ? '✅ 已探索' : '📍 标记已探索' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { loadProgress, saveProgress } from '@/composables/useQuest';

const progress = reactive(loadProgress());
const popup = ref<{ id: string; name: string; desc: string } | null>(null);

function isExplored(id: string) { return progress.explored.includes(id); }
function clickLoc(loc: { id: string; name: string; desc: string }) {
  if (!isExplored(loc.id)) {
    progress.explored.push(loc.id);
    saveProgress({ ...progress });
  }
  popup.value = loc;
}
</script>

<style scoped>
.map-wrap {
  position: relative;
}
.map-hint {
  text-align: center;
  font-size: 11px;
  color: var(--text-muted);
  opacity: .5;
  margin-bottom: 12px;
  font-family: var(--font-display);
  letter-spacing: 2px;
}
.map-svg {
  width: 100%;
  height: auto;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-primary);
}
.loc { cursor: pointer; }
.loc__rect { transition: stroke 200ms, fill 200ms; }
.loc:hover .loc__rect { stroke: var(--amber); fill: var(--amber-soft); }
.loc--done .loc__rect { stroke: var(--success-border); fill: var(--success-soft); }
.loc--done text { fill: var(--success) !important; }

.map-popup {
  position: fixed; inset: 0;
  background: var(--mask-overlay);
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
}
.map-popup__card {
  background: var(--bg-panel);
  border: 1px solid var(--border-glow);
  border-radius: var(--radius-lg);
  padding: 24px;
  max-width: 320px;
  text-align: center;
}
.map-popup__card h3 {
  font-size: 18px; color: var(--amber); margin-bottom: 10px;
}
.map-popup__card p {
  font-size: 14px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 14px;
}
.map-popup__tag {
  font-size: 12px; color: var(--text-muted);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm); padding: 4px 10px;
}
.map-popup__tag--done { color: var(--success); border-color: var(--success-border); }
</style>
