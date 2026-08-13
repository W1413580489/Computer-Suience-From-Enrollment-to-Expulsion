<template>
  <div class="cal-root">
    <header class="cal-topbar">
      <button class="cal-back" @click="$router.push('/')">
        <NeonIcon name="back" :size="20" />
        <span>返回主页</span>
      </button>
      <span class="cal-topbar__title">📅 校历 · ACADEMIC CALENDAR</span>
    </header>

    <div class="cal-body">
      <header class="cal-intro">
        <span class="cal-intro__num">// ACADEMIC YEAR 2026-2027</span>
        <h1 class="cal-intro__title">2026-2027 学年校历</h1>
        <p class="cal-intro__sub">CAMPUS · JNU XKZ</p>
      </header>

      <!-- 第一学期 -->
      <section class="cal-semester">
        <h2 class="cal-semester__title">// 01 第一学期（二十周）</h2>
        <div class="cal-table-wrap">
          <table class="cal-table">
            <thead>
              <tr>
                <th class="cal-th-week">周次</th>
                <th class="cal-th-month">月份</th>
                <th>日</th>
                <th>一</th>
                <th>二</th>
                <th>三</th>
                <th>四</th>
                <th>五</th>
                <th>六</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(r, i) in sem1"
                :key="'s1-' + i"
                :class="{ 'cal-mark-exam': r.mark === 'exam', 'cal-mark-labor': r.mark === 'labor' }"
              >
                <td class="cal-week">
                  <span v-if="r.w">{{ r.w }}<em v-if="r.mark === 'exam'">▲</em><em v-else-if="r.mark === 'labor'">●</em></span>
                </td>
                <td class="cal-month">{{ r.m }}</td>
                <td v-for="(d, j) in r.days" :key="j" :class="cellClass(d)">
                  <span v-if="cellDay(d) != null">{{ cellDay(d) }}</span>
                  <span v-if="d && d.s" class="cal-marker">◇</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- 第二学期 -->
      <section class="cal-semester">
        <h2 class="cal-semester__title">// 02 第二学期（二十周）</h2>
        <div class="cal-table-wrap">
          <table class="cal-table">
            <thead>
              <tr>
                <th class="cal-th-week">周次</th>
                <th class="cal-th-month">月份</th>
                <th>日</th>
                <th>一</th>
                <th>二</th>
                <th>三</th>
                <th>四</th>
                <th>五</th>
                <th>六</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(r, i) in sem2"
                :key="'s2-' + i"
                :class="{ 'cal-mark-exam': r.mark === 'exam', 'cal-mark-labor': r.mark === 'labor' }"
              >
                <td class="cal-week">
                  <span v-if="r.w">{{ r.w }}<em v-if="r.mark === 'exam'">▲</em><em v-else-if="r.mark === 'labor'">●</em></span>
                </td>
                <td class="cal-month">{{ r.m }}</td>
                <td v-for="(d, j) in r.days" :key="j" :class="cellClass(d)">
                  <span v-if="cellDay(d) != null">{{ cellDay(d) }}</span>
                  <span v-if="d && d.s" class="cal-marker">◇</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- 附记 / 图例 -->
      <section class="cal-legend">
        <p class="cal-legend__title">附记：</p>
        <p class="cal-legend__row"><span class="cal-swatch cal-staff"></span> 教职工开学日</p>
        <p class="cal-legend__row"><span class="cal-swatch cal-class"></span> 学生上课日</p>
        <p class="cal-legend__row"><span class="cal-swatch cal-holiday"></span> 放假日</p>
        <p class="cal-legend__row"><span class="cal-swatch cal-grad"></span> 毕业典礼</p>
        <p class="cal-legend__row"><span class="cal-swatch cal-mark-exam-sw"></span> ▲ 复习考试周</p>
        <p class="cal-legend__row"><span class="cal-swatch cal-mark-labor-sw"></span> ● 劳动实践周</p>
        <p class="cal-legend__row"><span class="cal-swatch cal-spring"></span> ◇ 春节</p>
        <p class="cal-legend__note">（二）节假日放假以国家和学校规定为准</p>
        <p class="cal-legend__note">（三）如有调整，以学校文件为准</p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import NeonIcon from '@/components/common/NeonIcon.vue';

type DayType = 'staff' | 'class' | 'holiday' | 'grad' | 'spring';
interface Day {
  d: number;
  t?: DayType;
  s?: boolean; // 春节标记（◇）
}
type Cell = number | Day | null;

interface Row {
  w?: number;
  m: string;
  days: Cell[];
  mark?: 'exam' | 'labor';
}

function n(d: number, t?: DayType, s?: boolean): Day {
  return { d, t, s };
}

function cellDay(d: Cell): number | null {
  if (d == null) return null;
  return typeof d === 'number' ? d : d.d;
}

function cellClass(d: Cell): string {
  if (d == null) return '';
  if (typeof d === 'number') return '';
  switch (d.t) {
    case 'staff': return 'cal-cell-staff';
    case 'class': return 'cal-cell-class';
    case 'holiday': return 'cal-cell-holiday';
    case 'grad': return 'cal-cell-grad';
    case 'spring': return 'cal-cell-spring';
    default: return '';
  }
}

// 第一学期（八、九月 ~ 二月）
const sem1: Row[] = [
  { w: 1, m: '八、九月', days: [null, 30, 31, 1, n(2, 'staff'), n(3, 'class'), 4, 5] },
  { w: 1, m: '九月', days: [6, n(7, 'class'), n(8, 'class'), n(9, 'class'), n(10, 'class'), n(11, 'class'), 12] },
  { w: 2, m: '九月', days: [13, 14, 15, 16, 17, 18, 19] },
  { w: 3, m: '九月', days: [20, 21, 22, 23, 24, 25, 26] },
  { w: 4, m: '九、十月', days: [27, 28, 29, 30, 1, 2, 3] },
  { w: 5, m: '十月', days: [4, 5, 6, 7, 8, 9, 10] },
  { w: 6, m: '十月', days: [11, 12, 13, 14, 15, 16, 17] },
  { w: 7, m: '十月', days: [18, 19, 20, 21, 22, 23, 24] },
  { w: 8, m: '十月', days: [25, 26, 27, 28, 29, 30, 31] },
  { w: 9, m: '十一月', days: [1, 2, 3, 4, 5, 6, 7] },
  { w: 10, m: '十一月', days: [8, 9, 10, 11, 12, 13, 14] },
  { w: 11, m: '十一月', days: [15, 16, 17, 18, 19, 20, 21] },
  { w: 12, m: '十一月', days: [22, 23, 24, 25, 26, 27, 28] },
  { w: 13, m: '十一、十二月', days: [29, 30, 1, 2, 3, 4, 5] },
  { w: 14, m: '十二月', days: [6, 7, 8, 9, 10, 11, 12] },
  { w: 15, m: '十二月', days: [13, 14, 15, 16, 17, 18, 19] },
  { w: 16, m: '十二月', days: [20, 21, 22, 23, 24, 25, 26] },
  { w: 17, m: '十二月、2027年一月', days: [27, 28, 29, 30, 31, 1, 2] },
  { w: 18, m: '一月', mark: 'exam', days: [3, 4, 5, 6, 7, 8, 9] },
  { w: 19, m: '一月', mark: 'exam', days: [10, 11, 12, 13, 14, 15, 16] },
  { w: 20, m: '一月', mark: 'exam', days: [17, 18, 19, 20, 21, 22, 23] },
  { w: 21, m: '一、二月', days: [24, n(25, 'holiday'), 26, 27, 28, 29, 30] },
  { w: 22, m: '二月', days: [31, 1, 2, 3, 4, { d: 5, t: 'spring', s: true }, null] },
  { w: 23, m: '放寒假', days: [7, 8, 9, 10, 11, 12, 13] },
  { w: 24, m: '二月', days: [14, 15, 16, 17, 18, 19, 20] },
  { w: 25, m: '二月', days: [21, 22, 23, 24, n(25, 'staff'), 26, 27] },
];

// 第二学期（二月 ~ 八月）
const sem2: Row[] = [
  { w: 1, m: '二月', days: [null, 21, n(22, 'class'), n(23, 'class'), n(24, 'class'), n(25, 'staff'), 26, 27] },
  { w: 1, m: '二、三月', days: [28, n(1, 'class'), 2, 3, 4, 5, 6] },
  { w: 2, m: '三月', days: [7, 8, 9, 10, 11, 12, 13] },
  { w: 3, m: '三月', days: [14, 15, 16, 17, 18, 19, 20] },
  { w: 4, m: '三月', days: [21, 22, 23, 24, 25, 26, 27] },
  { w: 5, m: '三、四月', days: [28, 29, 30, 31, 1, 2, 3] },
  { w: 6, m: '四月', days: [4, 5, 6, 7, 8, 9, 10] },
  { w: 7, m: '四月', days: [11, 12, 13, 14, 15, 16, 17] },
  { w: 8, m: '四月', days: [18, 19, 20, 21, 22, 23, 24] },
  { w: 9, m: '四、五月', days: [25, 26, 27, 28, 29, 30, 1] },
  { w: 10, m: '五月', days: [2, 3, 4, 5, 6, 7, 8] },
  { w: 11, m: '五月', days: [9, 10, 11, 12, 13, 14, 15] },
  { w: 12, m: '五月', days: [16, 17, 18, 19, 20, 21, 22] },
  { w: 13, m: '五月', days: [23, 24, 25, 26, 27, 28, 29] },
  { w: 14, m: '五、六月', days: [30, 31, 1, 2, 3, 4, 5] },
  { w: 15, m: '六月', days: [6, 7, 8, 9, 10, 11, 12] },
  { w: 16, m: '六月', days: [13, 14, 15, 16, 17, n(18, 'grad'), 19] },
  { w: 17, m: '六月', mark: 'exam', days: [20, 21, 22, 23, 24, 25, 26] },
  { w: 18, m: '六、七月', mark: 'exam', days: [27, 28, 29, 30, 1, 2, 3] },
  { w: 19, m: '七月', mark: 'labor', days: [4, 5, 6, 7, 8, 9, 10] },
  { w: 20, m: '七月', mark: 'labor', days: [11, 12, 13, 14, 15, 16, 17] },
  { w: 21, m: '七月', days: [18, n(19, 'grad'), 20, 21, 22, 23, 24] },
  { w: 22, m: '七月', days: [25, 26, 27, 28, 29, 30, 31] },
  { w: 23, m: '放暑假', days: [1, 2, 3, 4, 5, 6, 7] },
  { w: 24, m: '八月', days: [8, 9, 10, 11, 12, 13, 14] },
  { w: 25, m: '八月', days: [15, 16, 17, 18, 19, 20, 21] },
  { w: 26, m: '八月', days: [22, 23, 24, n(25, 'staff'), 26, 27, 28] },
];
</script>

<style scoped>
.cal-root {
  min-height: 100vh;
  min-height: 100dvh;
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
}

.cal-topbar {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 0 clamp(12px, 2vw, 16px);
  height: var(--topbar-h);
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-panel);
  flex-shrink: 0;
}

.cal-back {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  font-size: 14px;
  font-weight: 700;
  color: var(--amber);
  border: 1px solid var(--amber);
  background: var(--amber-soft);
  cursor: pointer;
  transition: background 160ms;
  clip-path: var(--clip-sm);
}

.cal-back:hover {
  background: var(--amber-mid);
}

.cal-topbar__title {
  flex: 1;
  font-family: var(--font-mono);
  font-size: clamp(13px, 2vw, 15px);
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--text-primary);
}

.cal-body {
  flex: 1;
  max-width: 1100px;
  width: 100%;
  margin: 0 auto;
  padding: clamp(24px, 4vw, 40px) clamp(12px, 3vw, 24px) 48px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

/* ---- Intro ---- */
.cal-intro {
  text-align: center;
  padding: 16px 0 8px;
}

.cal-intro__num {
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 3px;
  color: var(--amber);
}

.cal-intro__title {
  font-family: var(--font-display);
  font-size: clamp(28px, 5vw, 40px);
  font-weight: 900;
  letter-spacing: 0.05em;
  color: var(--text-primary);
  margin: 6px 0;
}

.cal-intro__sub {
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 4px;
  color: var(--text-secondary);
}

/* ---- Semester ---- */
.cal-semester__title {
  font-family: var(--font-display);
  font-size: clamp(18px, 2.5vw, 22px);
  letter-spacing: 2px;
  color: var(--amber);
  margin-bottom: 12px;
}

.cal-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--border-subtle);
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
}

.cal-table {
  width: 100%;
  min-width: 720px;
  border-collapse: collapse;
  background: var(--bg-panel);
  font-size: clamp(11px, 1.4vw, 13px);
}

.cal-table th,
.cal-table td {
  border: 1px solid var(--border-subtle);
  padding: 7px 4px;
  text-align: center;
  vertical-align: middle;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.cal-table thead th {
  background: var(--bg-panel-2);
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--amber);
  padding: 10px 4px;
}

.cal-th-week {
  width: 56px;
}

.cal-th-month {
  width: 110px;
}

.cal-week {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 900;
  color: var(--amber);
  background: var(--bg-panel-2);
}

.cal-week em {
  display: inline-block;
  margin-left: 3px;
  font-style: normal;
  font-family: var(--font-body);
  font-size: 11px;
  color: var(--text-primary);
}

.cal-month {
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--bg-panel-2);
  letter-spacing: 1px;
}

.cal-mark-exam {
  background: rgba(255, 217, 61, 0.06);
}

.cal-mark-labor {
  background: rgba(0, 240, 255, 0.05);
}

.cal-mark-exam .cal-week em { color: var(--amber); }
.cal-mark-labor .cal-week em { color: var(--neon-cyan); }

/* ---- 特殊日配色 ---- */
.cal-cell-staff {
  background: #FFD93D !important;
  color: #0A0A0A !important;
  font-weight: 800;
}

.cal-cell-class {
  background: #4ECCA3 !important;
  color: #0A0A0A !important;
  font-weight: 700;
}

.cal-cell-holiday {
  background: #4D8DFF !important;
  color: #F5F5F5 !important;
  font-weight: 700;
}

.cal-cell-grad {
  background: #FF2D95 !important;
  color: #F5F5F5 !important;
  font-weight: 800;
}

.cal-cell-spring {
  background: #4D8DFF !important;
  color: #F5F5F5 !important;
  font-weight: 700;
}

.cal-marker {
  display: inline-block;
  margin-left: 2px;
  font-size: 10px;
}

/* ---- 图例 ---- */
.cal-legend {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 20px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
}

.cal-legend__title {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--amber);
  margin-bottom: 4px;
}

.cal-legend__row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text-primary);
}

.cal-swatch {
  display: inline-block;
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  border: 1px solid var(--ink);
}

.cal-staff { background: #FFD93D; }
.cal-class { background: #4ECCA3; }
.cal-holiday, .cal-spring { background: #4D8DFF; }
.cal-grad { background: #FF2D95; }

.cal-mark-exam-sw::before {
  content: '▲';
  font-size: 16px;
  color: var(--amber);
}
.cal-mark-labor-sw::before {
  content: '●';
  font-size: 16px;
  color: var(--neon-cyan);
}

.cal-legend__note {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}

/* ---- 响应式 ---- */
@media (max-width: 640px) {
  .cal-back-label {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    transition-duration: 0.01ms !important;
  }
}
</style>