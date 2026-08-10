<template>
  <div class="map-wrap">
    <div class="map-hint">🗺️ 示意地图 · 非精确地理位置 · 点击地点开始探索</div>

    <!-- First-visit guide overlay -->
    <Transition name="fade">
      <div v-if="showGuideOverlay" class="map-guide-overlay" @click="dismissGuide">
        <div class="map-guide-card" @click.stop>
          <span class="map-guide-card__icon">📍</span>
          <h3>欢迎来到大地图</h3>
          <p>校园里有 <strong>9 个探索地点</strong>等待发现。<br>点击地图上的发光标记，了解每个地点的详细信息。</p>
          <p class="map-guide-card__tip">💡 小提示：从南门出发，一路向北探索</p>
          <button class="map-guide-card__btn" @click="dismissGuide">开始探索！</button>
        </div>
      </div>
    </Transition>

    <svg viewBox="0 0 640 460" class="map-svg" preserveAspectRatio="xMidYMid meet">
      <defs>
        <!-- Glow filters -->
        <filter id="glow">
          <feGaussianBlur stdDeviation="2.5" result="blur"/>
          <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <filter id="glow-amber">
          <feGaussianBlur stdDeviation="3" result="blur"/>
          <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <!-- Zone gradients -->
        <linearGradient id="zone-teaching" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#378ADD" stop-opacity=".08"/>
          <stop offset="100%" stop-color="#378ADD" stop-opacity=".03"/>
        </linearGradient>
        <linearGradient id="zone-living" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#EF9F27" stop-opacity=".08"/>
          <stop offset="100%" stop-color="#EF9F27" stop-opacity=".03"/>
        </linearGradient>
        <linearGradient id="zone-sports" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#4ECCA3" stop-opacity=".08"/>
          <stop offset="100%" stop-color="#4ECCA3" stop-opacity=".03"/>
        </linearGradient>
        <!-- Lake gradient -->
        <radialGradient id="lake-grad" cx="50%" cy="50%" r="55%">
          <stop offset="0%" stop-color="#1A4D7A" stop-opacity=".9"/>
          <stop offset="60%" stop-color="#153A5E" stop-opacity=".7"/>
          <stop offset="100%" stop-color="#0F2D4A" stop-opacity=".4"/>
        </radialGradient>
        <!-- Pulse for unexplored -->
        <radialGradient id="pulse-unexplored">
          <stop offset="0%" stop-color="var(--amber)" stop-opacity=".5"/>
          <stop offset="100%" stop-color="var(--amber)" stop-opacity="0"/>
        </radialGradient>
      </defs>

      <!-- Background + grid -->
      <rect width="640" height="460" fill="var(--bg-primary)"/>
      <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
        <path d="M 24 0 L 0 0 0 24" fill="none" stroke="var(--border-subtle)" stroke-width=".3" opacity=".2"/>
      </pattern>
      <rect width="640" height="460" fill="url(#grid)"/>

      <!-- === ZONES === -->
      <!-- Teaching zone (east of lake) -->
      <path d="M 310 100 L 520 100 L 520 270 L 360 270 L 310 220 Z" fill="url(#zone-teaching)" stroke="#378ADD" stroke-width=".8" stroke-dasharray="6,4" opacity=".6"/>
      <text x="420" y="120" fill="#378ADD" font-size="9" font-family="var(--font-display)" opacity=".5" letter-spacing="3">教学区</text>

      <!-- Living zone (north) -->
      <path d="M 80 30 L 500 30 L 500 100 L 310 100 L 80 60 Z" fill="url(#zone-living)" stroke="#EF9F27" stroke-width=".8" stroke-dasharray="6,4" opacity=".6"/>
      <text x="200" y="48" fill="#EF9F27" font-size="9" font-family="var(--font-display)" opacity=".5" letter-spacing="3">生活区</text>

      <!-- Sports zone (east) -->
      <rect x="470" y="270" width="150" height="130" rx="6" fill="url(#zone-sports)" stroke="#4ECCA3" stroke-width=".8" stroke-dasharray="6,4" opacity=".6"/>
      <text x="545" y="290" fill="#4ECCA3" font-size="9" font-family="var(--font-display)" opacity=".5" letter-spacing="3">运动区</text>

      <!-- === ROAD NETWORK === -->
      <!-- Main roads with intersections -->
      <g opacity=".2">
        <!-- South-North main road -->
        <path d="M 200 440 L 200 360 L 260 300 L 260 220 L 320 180 L 320 100 L 380 100 L 380 30" fill="none" stroke="var(--amber)" stroke-width="2.5"/>
        <!-- East-West road across teaching zone -->
        <path d="M 260 300 L 320 300 L 380 280 L 480 280 L 520 300" fill="none" stroke="var(--amber)" stroke-width="2"/>
        <!-- Road to south gate -->
        <path d="M 300 400 L 300 440" fill="none" stroke="var(--amber)" stroke-width="2"/>
        <!-- Road to west buildings -->
        <path d="M 160 240 L 80 220 L 50 240" fill="none" stroke="var(--amber)" stroke-width="1.8"/>
        <!-- Road around lake -->
        <path d="M 260 220 L 200 240 L 160 260 L 260 300" fill="none" stroke="var(--amber)" stroke-width="1.5" opacity=".6"/>
      </g>

      <!-- Intersection dots -->
      <g fill="var(--amber)" opacity=".3">
        <circle cx="260" cy="300" r="2.5"/>
        <circle cx="320" cy="180" r="2.5"/>
        <circle cx="380" cy="100" r="2.5"/>
        <circle cx="480" cy="280" r="2.5"/>
        <circle cx="200" cy="360" r="2.5"/>
      </g>

      <!-- === MIRROR LAKE (center) === -->
      <g filter="url(#glow)">
        <ellipse cx="260" cy="240" rx="75" ry="48" fill="url(#lake-grad)" stroke="#2A6DA8" stroke-width="1.5">
          <animate attributeName="rx" values="75;77;75" dur="4s" repeatCount="indefinite"/>
          <animate attributeName="ry" values="48;49;48" dur="4s" repeatCount="indefinite"/>
        </ellipse>
      </g>
      <text x="260" y="244" text-anchor="middle" fill="#4A9ACC" font-size="11" font-family="var(--font-display)" opacity=".6">镜 湖</text>

      <!-- Bridges across lake -->
      <g opacity=".5" stroke="#4A9ACC" stroke-width="1.8">
        <!-- Boya Bridge -->
        <line x1="210" y1="214" x2="195" y2="200"/>
        <line x1="310" y1="214" x2="325" y2="200"/>
      </g>
      <text x="180" y="196" fill="#4A9ACC" font-size="7" opacity=".4">博雅桥</text>
      <text x="328" y="196" fill="#4A9ACC" font-size="7" opacity=".4">博文桥</text>

      <!-- === BUILDINGS (sorted north→south) === -->

      <!-- 2.2 快递站 (NE corner, T11 style building) -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.2') }" @click="clickLoc(locs[1])">
        <rect x="450" y="50" width="52" height="30" rx="5" fill="var(--bg-panel)" stroke="var(--border-glow)" stroke-width="1.2" class="loc__rect"/>
        <line x1="460" y1="50" x2="460" y2="80" stroke="var(--border-subtle)" stroke-width=".8" opacity=".4"/>
        <line x1="476" y1="50" x2="476" y2="80" stroke="var(--border-subtle)" stroke-width=".8" opacity=".4"/>
        <line x1="492" y1="50" x2="492" y2="80" stroke="var(--border-subtle)" stroke-width=".8" opacity=".4"/>
        <text x="476" y="72" text-anchor="middle" fill="var(--text-secondary)" font-size="10" font-weight="500">2.2 快递站</text>
        <circle cx="502" cy="50" r="4" :fill="isExplored('2.2') ? 'var(--success)' : 'var(--amber)'" :class="{ 'pulse-dot': !isExplored('2.2') }"/>
      </g>

      <!-- 2.5 实验室 (NW, research cluster) -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.5') }" @click="clickLoc(locs[4])">
        <rect x="55" y="85" width="70" height="24" rx="4" fill="var(--bg-panel)" stroke="var(--border-glow)" stroke-width="1.2" class="loc__rect"/>
        <!-- Wing shapes to suggest lab building -->
        <rect x="40" y="95" width="15" height="14" rx="3" fill="var(--bg-panel-2)" stroke="var(--border-subtle)" stroke-width=".8"/>
        <rect x="125" y="95" width="15" height="14" rx="3" fill="var(--bg-panel-2)" stroke="var(--border-subtle)" stroke-width=".8"/>
        <text x="90" y="102" text-anchor="middle" fill="var(--text-secondary)" font-size="10" font-weight="500">2.5 实验室</text>
        <circle cx="40" cy="85" r="4" :fill="isExplored('2.5') ? 'var(--success)' : 'var(--amber)'" :class="{ 'pulse-dot': !isExplored('2.5') }"/>
      </g>

      <!-- 2.8 图书馆 (east of lake, main landmark) -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.8') }" @click="clickLoc(locs[7])">
        <!-- L-shaped building with tower -->
        <rect x="340" y="130" width="72" height="22" rx="4" fill="var(--bg-panel)" stroke="var(--amber)" stroke-width="1.8" class="loc__rect"/>
        <rect x="340" y="152" width="30" height="20" rx="4" fill="var(--bg-panel-2)" stroke="var(--amber)" stroke-width="1.2"/>
        <!-- Tower -->
        <rect x="345" y="115" width="10" height="15" rx="2" fill="var(--amber-soft)" stroke="var(--amber)" stroke-width="1"/>
        <text x="390" y="145" text-anchor="middle" fill="var(--amber)" font-size="11" font-weight="600">2.8 图书馆</text>
        <circle cx="412" cy="130" r="5" :fill="isExplored('2.8') ? 'var(--success)' : 'var(--amber)'" :filter="isExplored('2.8') ? '' : 'url(#glow-amber)'" :class="{ 'pulse-dot': !isExplored('2.8') }"/>
      </g>

      <!-- 2.1 图书馆北侧 -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.1') }" @click="clickLoc(locs[0])">
        <rect x="310" y="95" width="55" height="32" rx="4" fill="var(--bg-panel)" stroke="var(--border-glow)" stroke-width="1.2" class="loc__rect"/>
        <text x="337" y="116" text-anchor="middle" fill="var(--text-secondary)" font-size="10" font-weight="500">2.1 图书馆北侧</text>
        <circle cx="310" cy="95" r="4" :fill="isExplored('2.1') ? 'var(--success)' : 'var(--amber)'" :class="{ 'pulse-dot': !isExplored('2.1') }"/>
      </g>

      <!-- 2.7 教学楼 (cluster east of lake) -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.7') }" @click="clickLoc(locs[6])">
        <!-- Three connected blocks -->
        <rect x="370" y="195" width="42" height="18" rx="3" fill="var(--bg-panel)" stroke="var(--border-glow)" stroke-width="1" class="loc__rect"/>
        <rect x="416" y="195" width="42" height="18" rx="3" fill="var(--bg-panel)" stroke="var(--border-glow)" stroke-width="1" class="loc__rect"/>
        <rect x="393" y="218" width="42" height="14" rx="3" fill="var(--bg-panel-2)" stroke="var(--border-subtle)" stroke-width="1"/>
        <text x="435" y="210" text-anchor="middle" fill="var(--text-secondary)" font-size="10" font-weight="500">2.7 教学楼</text>
        <circle cx="370" cy="195" r="4" :fill="isExplored('2.7') ? 'var(--success)' : 'var(--amber)'" :class="{ 'pulse-dot': !isExplored('2.7') }"/>
      </g>

      <!-- 2.3 校友会 (east) -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.3') }" @click="clickLoc(locs[2])">
        <rect x="490" y="165" width="50" height="28" rx="4" fill="var(--bg-panel)" stroke="var(--border-glow)" stroke-width="1.2" class="loc__rect"/>
        <text x="515" y="184" text-anchor="middle" fill="var(--text-secondary)" font-size="10" font-weight="500">2.3 校友会</text>
        <circle cx="540" cy="165" r="4" :fill="isExplored('2.3') ? 'var(--success)' : 'var(--amber)'" :class="{ 'pulse-dot': !isExplored('2.3') }"/>
      </g>

      <!-- 2.4 知识产权大楼 (west) -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.4') }" @click="clickLoc(locs[3])">
        <!-- Tall building silhouette -->
        <rect x="65" y="195" width="22" height="40" rx="4" fill="var(--bg-panel)" stroke="var(--border-glow)" stroke-width="1.2" class="loc__rect"/>
        <rect x="95" y="210" width="40" height="25" rx="4" fill="var(--bg-panel-2)" stroke="var(--border-glow)" stroke-width="1"/>
        <text x="115" y="230" text-anchor="middle" fill="var(--text-secondary)" font-size="9" font-weight="500">2.4 知识产权</text>
        <circle cx="65" cy="195" r="4" :fill="isExplored('2.4') ? 'var(--success)' : 'var(--amber)'" :class="{ 'pulse-dot': !isExplored('2.4') }"/>
      </g>

      <!-- 2.6 镜湖 (already drawn, pin overlay) -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.6') }" @click="clickLoc(locs[5])">
        <rect x="220" y="195" width="55" height="22" rx="4" fill="var(--bg-panel)" stroke="var(--amber)" stroke-width="1.2" class="loc__rect" opacity=".85"/>
        <text x="247" y="210" text-anchor="middle" fill="var(--amber)" font-size="10" font-weight="500">2.6 镜湖</text>
        <circle cx="260" cy="240" r="6" fill="none" stroke="var(--amber)" stroke-width="1.5" opacity=".6">
          <animate attributeName="r" values="6;11;6" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values=".6;.2;.6" dur="2s" repeatCount="indefinite"/>
        </circle>
      </g>

      <!-- 2.9 操场 (southeast) -->
      <g class="loc" :class="{ 'loc--done': isExplored('2.9') }" @click="clickLoc(locs[8])">
        <!-- Track oval -->
        <ellipse cx="510" cy="310" rx="55" ry="30" fill="none" stroke="#4ECCA3" stroke-width="1.5" opacity=".4"/>
        <ellipse cx="510" cy="310" rx="48" ry="24" fill="none" stroke="#4ECCA3" stroke-width=".8" opacity=".2"/>
        <!-- Label -->
        <rect x="475" y="340" width="70" height="22" rx="4" fill="var(--bg-panel)" stroke="var(--border-glow)" stroke-width="1" class="loc__rect"/>
        <text x="510" y="355" text-anchor="middle" fill="var(--text-secondary)" font-size="10" font-weight="500">2.9 操场</text>
        <circle cx="455" cy="310" r="4" :fill="isExplored('2.9') ? 'var(--success)' : 'var(--amber)'" :class="{ 'pulse-dot': !isExplored('2.9') }"/>
      </g>

      <!-- === South Gate + exploration guide line === -->
      <!-- Guide line from south gate to first stop -->
      <g v-if="!hasExploredAny">
        <path d="M 300 420 L 300 380 L 260 340" fill="none" stroke="var(--amber)" stroke-width="2" stroke-dasharray="6,3" opacity=".5">
          <animate attributeName="stroke-dashoffset" from="18" to="0" dur="1.5s" repeatCount="indefinite"/>
        </path>
      </g>

      <!-- South Gate marker -->
      <g>
        <rect x="265" y="408" width="70" height="24" rx="6" fill="var(--bg-panel)" stroke="var(--border-glow)" stroke-width="1.2"/>
        <text x="300" y="424" text-anchor="middle" fill="var(--text-secondary)" font-size="11" font-weight="600">🚩 南门入口</text>
        <polygon points="300,445 292,435 308,435" fill="var(--amber)" opacity=".4">
          <animate attributeName="opacity" values=".4;.7;.4" dur="1.5s" repeatCount="indefinite"/>
        </polygon>
      </g>

      <!-- Compass -->
      <text x="610" y="24" text-anchor="middle" fill="var(--text-muted)" font-size="16" font-weight="700" opacity=".5">N</text>
      <line x1="610" y1="28" x2="610" y2="48" stroke="var(--text-muted)" stroke-width="1.5" opacity=".4"/>
      <polygon points="610,52 604,42 616,42" fill="var(--text-muted)" opacity=".4"/>
    </svg>

    <!-- Info popup with next-location flow -->
    <Transition name="fade">
      <div v-if="popup" class="map-popup" @click="popup = null">
        <div class="map-popup__card" @click.stop>
          <div class="map-popup__header">
            <span class="map-popup__num">{{ popup.id }}</span>
            <h3>{{ popup.name }}</h3>
          </div>
          <p>{{ popup.desc }}</p>
          <div class="map-popup__actions">
            <button
              class="map-popup__explore-btn"
              :class="{ done: isExplored(popup.id) }"
              @click="toggleExplore(popup.id)"
            >
              {{ isExplored(popup.id) ? '✅ 已探索' : '📍 标记已探索' }}
            </button>
            <button
              v-if="nextLoc"
              class="map-popup__next-btn"
              @click="goNext"
            >
              下一个地点 → {{ nextLoc.name }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { loadProgress, saveProgress } from '@/composables/useQuest';

const props = defineProps<{ showGuideOverlay?: boolean }>();
const emit = defineEmits<{ dismissGuide: [] }>();

const locs = [
  { id: '2.1', name: '图书馆北侧', desc: '自主学习空间 / 研修间预约 / 自助借还' },
  { id: '2.2', name: '快递站', desc: 'T11 架空层 · 菜鸟驿站 · 取件码自助取件' },
  { id: '2.3', name: '校友会', desc: '校友联络 · 捐赠事务 · 校友活动中心' },
  { id: '2.4', name: '知识产权大楼', desc: '知识产权学院 · 专利检索中心 · 学术报告厅' },
  { id: '2.5', name: '实验室', desc: '物联网/大数据/网络安全实验室 · A类竞赛孵化核心场地' },
  { id: '2.6', name: '镜湖', desc: '校园中心湖 · 散步发呆好去处 · 博雅桥/博文桥连接两岸' },
  { id: '2.7', name: '教学楼', desc: '主要上课区域 · 多媒体教室 · 自习室 · 机房' },
  { id: '2.8', name: '图书馆', desc: '惠全楼图书馆 · 自习/借阅/研讨间 · 开放至 22:00' },
  { id: '2.9', name: '操场', desc: '田径场 · 篮球场 · 体测场地 · 运动会举办地' },
];

const progress = reactive(loadProgress());
const popup = ref<{ id: string; name: string; desc: string } | null>(null);
const exploredOrder = ref<string[]>([]);

const hasExploredAny = computed(() => progress.explored.length > 0);

const nextLoc = computed(() => {
  if (!popup.value) return null;
  const idx = locs.findIndex(l => l.id === popup.value!.id);
  const remaining = locs.slice(idx + 1).filter(l => !isExplored(l.id));
  if (remaining.length > 0) return remaining[0];
  const before = locs.slice(0, idx).filter(l => !isExplored(l.id));
  return before.length > 0 ? before[0] : null;
});

function isExplored(id: string) { return progress.explored.includes(id); }

function clickLoc(loc: { id: string; name: string; desc: string }) {
  popup.value = loc;
}

function toggleExplore(id: string) {
  const idx = progress.explored.indexOf(id);
  if (idx >= 0) {
    progress.explored.splice(idx, 1);
    exploredOrder.value = exploredOrder.value.filter(x => x !== id);
  } else {
    progress.explored.push(id);
    exploredOrder.value.push(id);
  }
  saveProgress({ ...progress });
}

function goNext() {
  if (nextLoc.value) {
    popup.value = nextLoc.value;
  }
}

function dismissGuide() {
  emit('dismissGuide');
}
</script>

<style scoped>
.map-wrap {
  position: relative;
  padding: clamp(8px, 1.5vw, 12px);
}
.map-hint {
  text-align: center;
  font-size: clamp(10px, 1.5vw, 11px);
  color: var(--text-muted);
  opacity: .5;
  margin-bottom: clamp(8px, 1.5vw, 12px);
  font-family: var(--font-display);
  letter-spacing: 2px;
}
.map-svg {
  width: 100%;
  height: auto;
  max-height: calc(100vh - 220px);
  max-height: calc(100dvh - 220px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-primary);
}

/* ---- Location states ---- */
.loc { cursor: pointer; }
.loc__rect { transition: stroke 200ms, fill 200ms; }
.loc:hover .loc__rect { stroke: var(--amber); fill: var(--amber-soft); }
.loc--done .loc__rect { stroke: var(--success-border); fill: var(--success-soft); }
.loc--done text { fill: var(--success) !important; }

/* Pulse animation for unexplored dots */
.pulse-dot {
  animation: pulse-ring 2s ease-in-out infinite;
}
@keyframes pulse-ring {
  0%, 100% { r: 4; opacity: 1; }
  50% { r: 7; opacity: .4; }
}

/* ---- Guide Overlay ---- */
.map-guide-overlay {
  position: fixed; inset: 0;
  background: var(--mask-strong);
  display: flex; align-items: center; justify-content: center;
  z-index: 120;
  padding: 20px;
}
.map-guide-card {
  background: var(--bg-panel);
  border: 1px solid var(--amber);
  border-radius: var(--radius-lg);
  padding: clamp(20px, 3vw, 28px);
  max-width: 380px;
  text-align: center;
  box-shadow: 0 4px 32px var(--amber-glow);
}
.map-guide-card__icon { font-size: clamp(32px, 5vw, 40px); display: block; margin-bottom: 12px; }
.map-guide-card h3 {
  font-size: clamp(16px, 2.5vw, 20px); color: var(--amber); margin-bottom: 10px;
}
.map-guide-card p {
  font-size: clamp(13px, 2vw, 14px); color: var(--text-secondary); line-height: 1.7; margin-bottom: 6px;
}
.map-guide-card__tip {
  color: var(--text-muted) !important;
  font-size: clamp(11px, 1.8vw, 12px) !important;
}
.map-guide-card__btn {
  margin-top: 16px;
  padding: clamp(8px, 1.5vw, 10px) clamp(20px, 4vw, 28px);
  background: var(--amber);
  color: var(--on-amber);
  border-radius: var(--radius-md);
  font-size: clamp(14px, 2vw, 16px);
  font-weight: 700;
  cursor: pointer;
  transition: opacity 200ms, transform 150ms;
}
.map-guide-card__btn:hover { opacity: .9; transform: translateY(-1px); }

/* ---- Popup ---- */
.map-popup {
  position: fixed; inset: 0;
  background: var(--mask-overlay);
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
  padding: 20px;
}
.map-popup__card {
  background: var(--bg-panel);
  border: 1px solid var(--border-glow);
  border-radius: var(--radius-lg);
  padding: clamp(18px, 3vw, 24px);
  max-width: 360px;
  width: 100%;
  text-align: center;
}
.map-popup__header {
  display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 10px;
}
.map-popup__num {
  font-family: var(--font-display); font-size: 11px; color: var(--amber);
  border: 1px solid var(--amber-glow); border-radius: var(--radius-sm); padding: 2px 8px;
}
.map-popup__card h3 {
  font-size: clamp(16px, 2.5vw, 18px); color: var(--amber);
}
.map-popup__card p {
  font-size: clamp(13px, 2vw, 14px); color: var(--text-secondary); line-height: 1.7; margin-bottom: 14px;
}
.map-popup__actions {
  display: flex; flex-direction: column; gap: 8px;
}
.map-popup__explore-btn {
  padding: 8px 14px;
  font-size: clamp(11px, 1.8vw, 12px); color: var(--text-muted);
  background: var(--bg-panel-3);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: color 150ms, border-color 150ms;
}
.map-popup__explore-btn:hover { color: var(--success); border-color: var(--success-border); }
.map-popup__explore-btn.done { color: var(--success); border-color: var(--success-border); }
.map-popup__next-btn {
  padding: 8px 14px;
  font-size: clamp(12px, 2vw, 14px); font-weight: 600; color: var(--amber);
  background: var(--amber-soft);
  border: 1px solid var(--amber-glow);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 150ms, transform 150ms;
}
.map-popup__next-btn:hover { background: var(--amber-mid); transform: translateX(2px); }

/* ---- Transitions ---- */
.fade-enter-active { transition: opacity .25s ease; }
.fade-leave-active { transition: opacity .2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ---- Mobile ---- */
@media (max-width: 480px) {
  .map-wrap { padding: 4px; }
  .map-svg { border-radius: var(--radius-md); }
}
</style>
