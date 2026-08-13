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
                  <span v-if="r.w" class="cal-week-num">{{ r.w }}</span>
                  <span v-if="r.mark === 'exam'" class="cal-week-mark cal-week-mark--exam">▲</span>
                  <span v-else-if="r.mark === 'labor'" class="cal-week-mark cal-week-mark--labor">●</span>
                </td>
                <td class="cal-month">{{ r.m }}</td>
                <td v-for="(d, j) in r.days" :key="j" :class="cellClass(d)">
                  <span v-if="cellDay(d) != null" class="cal-day">{{ cellDay(d) }}</span>
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
                  <span v-if="r.w" class="cal-week-num">{{ r.w }}</span>
                  <span v-if="r.mark === 'exam'" class="cal-week-mark cal-week-mark--exam">▲</span>
                  <span v-else-if="r.mark === 'labor'" class="cal-week-mark cal-week-mark--labor">●</span>
                </td>
                <td class="cal-month">{{ r.m }}</td>
                <td v-for="(d, j) in r.days" :key="j" :class="cellClass(d)">
                  <span v-if="cellDay(d) != null" class="cal-day">{{ cellDay(d) }}</span>
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
        <p class="cal-legend__row"><span class="cal-tag cal-tag--staff">黄</span> 教职工开学日</p>
        <p class="cal-legend__row"><span class="cal-tag cal-tag--class">绿</span> 学生上课日</p>
        <p class="cal-legend__row"><span class="cal-tag cal-tag--holiday">蓝</span> 放假日</p>
        <p class="cal-legend__row"><span class="cal-tag cal-tag--grad">红</span> 毕业典礼</p>
        <p class="cal-legend__row"><span class="cal-mark cal-mark--exam">▲</span> 复习考试周</p>
        <p class="cal-legend__row"><span class="cal-mark cal-mark--labor">●</span> 劳动实践周</p>
        <p class="cal-legend__row"><span class="cal-tag cal-tag--spring">◇</span> 春节</p>
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
  s?: boolean; // 春节标记
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
    case 'staff': return 'cal-cell cal-cell--staff';
    case 'class': return 'cal-cell cal-cell--class';
    case 'holiday': return 'cal-cell cal-cell--holiday';
    case 'grad': return 'cal-cell cal-cell--grad';
    case 'spring': return 'cal-cell cal-cell--spring';
    default: return '';
  }
}

// ===== 第一学期（八、九月 ~ 二月）26 行 =====
const sem1: Row[] = [
  { w: 1, m: '八、九月', days: [30, 31, 1, 2, n(3, 'staff'), 4, 5] },
  { w: 1, m: '九月', days: [6, n(7, 'class'), 8, 9, 10, 11, 12] },
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
  { w: 17, m: '十二月、2027年一月', mark: 'exam', days: [27, 28, 29, 30, 31, 1, 2] },
  { w: 18, m: '一月', mark: 'exam', days: [3, 4, 5, 6, 7, 8, 9] },
  { w: 19, m: '一月', mark: 'exam', days: [10, 11, 12, 13, 14, 15, 16] },
  { w: 20, m: '一月', mark: 'exam', days: [17, 18, 19, 20, 21, 22, 23] },
  { w: 21, m: '一、二月', days: [24, n(25, 'holiday'), 26, 27, 28, 29, 30] },
  { w: 22, m: '二月', days: [31, 1, 2, 3, 4, n(5, 'spring', true), 6] },
  { w: 23, m: '放寒假', days: [7, 8, 9, 10, 11, 12, 13] },
  { w: 24, m: '二月', days: [14, 15, 16, 17, 18, 19, 20] },
  { w: 25, m: '二月', days: [21, 22, 23, 24, n(25, 'staff'), 26, 27] },
];

// ===== 第二学期（二月 ~ 八月）27 行 =====
const sem2: Row[] = [
  { w: 1, m: '二月', days: [21, n(22, 'class'), 23, 24, n(25, 'staff'), 26, 27] },
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
  { w: 16, m: '六月', days: [13, 14, 15, 16, 17, 18, n(19, 'grad')] },
  { w: 17, m: '六月', mark: 'exam', days: [20, 21, 22, 23, 24, 25, 26] },
  { w: 18, m: '六、七月', mark: 'exam', days: [27, 28, 29, 30, 1, 2, 3] },
  { w: 19, m: '七月', mark: 'labor', days: [4, 5, 6, 7, 8, 9, 10] },
  { w: 20, m: '七月', mark: 'labor', days: [11, 12, 13, 14, 15, 16, 17] },
  { w: 21, m: '七月', days: [18, n(19, 'grad'), 20, 21, 22, 23, 24] },
  { w: 22, m: '七月', days: [25, 26, 27, 28, 29, 30, 31] },
  { w: 23, m: '放暑假', days: [1, 2, 3, 4, 5, 6, 7] },
  { w: 24, m: '八月', days: [8, 9, 10, 11, 12, 13, 14] },
  { w: 25, m: '八月', days: [15, 16, 17, 18, 19, 20, 21] },
  { w: 26, m: '八月', days: [22, 23, 24, 25, n(26, 'staff'), 27, 28] },
];
</script>

<style scoped>
/* ===== 纯黑底白字 ===== */
.cal-root {
  height: 100vh;
  height: 100dvh;
  background: #000000;
  color: #ffffff;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.cal-topbar {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 0 clamp(12px, 2vw, 16px);
  height: var(--topbar-h);
  border-bottom: 1px solid #555555;
  background: #000000;
  flex-shrink: 0;
}

.cal-back {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  font-size: 14px;
  font-weight: 700;
  color: #ffffff;
  background: #000000;
  border: 1px solid #ffffff;
  cursor: pointer;
  transition: background 160ms;
}

.cal-back:hover {
  background: #ffffff;
  color: #000000;
}

.cal-topbar__title {
  flex: 1;
  font-family: var(--font-mono);
  font-size: clamp(13px, 2vw, 16px);
  font-weight: 700;
  letter-spacing: 2px;
  color: #ffffff;
}

.cal-body {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: clamp(24px, 4vw, 40px) clamp(12px, 3vw, 24px) 60px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* ---- Intro ---- */
.cal-intro {
  text-align: center;
  padding: 16px 0 8px;
}

.cal-intro__num {
  font-family: var(--font-mono);
  font-size: 13px;
  letter-spacing: 3px;
  color: #aaaaaa;
}

.cal-intro__title {
  font-size: clamp(32px, 6vw, 56px);
  font-weight: 900;
  letter-spacing: 4px;
  color: #ffffff;
  margin: 8px 0;
}

.cal-intro__sub {
  font-family: var(--font-mono);
  font-size: 13px;
  letter-spacing: 5px;
  color: #888888;
}

/* ---- Semester ---- */
.cal-semester__title {
  font-size: clamp(20px, 3vw, 28px);
  font-weight: 800;
  letter-spacing: 3px;
  color: #ffffff;
  margin-bottom: 14px;
  padding-bottom: 8px;
  border-bottom: 1px solid #555555;
}

.cal-table-wrap {
  overflow-x: auto;
  border: 1px solid #444444;
  background: #000000;
}

.cal-table {
  width: 100%;
  min-width: 880px;
  border-collapse: collapse;
  background: #000000;
  font-size: clamp(15px, 1.8vw, 20px);
}

.cal-table th,
.cal-table td {
  border: 1px solid #444444;
  padding: 12px 6px;
  text-align: center;
  vertical-align: middle;
  color: #ffffff;
  font-variant-numeric: tabular-nums;
}

.cal-table thead th {
  background: #111111;
  font-size: clamp(14px, 1.6vw, 18px);
  font-weight: 800;
  letter-spacing: 2px;
  color: #ffffff;
  padding: 14px 6px;
}

.cal-th-week {
  width: 76px;
}

.cal-th-month {
  width: 140px;
}

/* ---- 周次列：周号 + ▲● 符号 ---- */
.cal-week {
  background: #111111;
  color: #ffffff;
}

.cal-week-num {
  display: inline-block;
  font-weight: 900;
  font-size: clamp(15px, 1.7vw, 19px);
  margin-right: 2px;
}

.cal-week-mark {
  display: inline-block;
  font-style: normal;
  font-weight: 800;
  font-size: clamp(13px, 1.5vw, 16px);
}

.cal-week-mark--exam {
  color: #FFD93D;
}

.cal-week-mark--labor {
  color: #00F0FF;
}

/* ---- 月份列 ---- */
.cal-month {
  font-size: clamp(13px, 1.5vw, 16px);
  color: #cccccc;
  background: #111111;
  letter-spacing: 1px;
}

/* ---- 考试/实践周：整行弱背景 ---- */
.cal-mark-exam {
  background: rgba(255, 217, 61, 0.05);
}

.cal-mark-labor {
  background: rgba(0, 240, 255, 0.05);
}

/* ---- 特殊日：低饱和度背景色覆盖格子 ---- */
.cal-cell {
  position: relative;
  background-color: transparent;
}

.cal-cell .cal-day {
  position: relative;
  z-index: 1;
}

.cal-cell--staff {
  background-color: rgba(255, 217, 61, 0.32);
  color: #ffffff;
  font-weight: 800;
}

.cal-cell--class {
  background-color: rgba(78, 204, 163, 0.32);
  color: #ffffff;
  font-weight: 700;
}

.cal-cell--holiday {
  background-color: rgba(77, 141, 255, 0.32);
  color: #ffffff;
  font-weight: 700;
}

.cal-cell--grad {
  background-color: rgba(255, 45, 149, 0.32);
  color: #ffffff;
  font-weight: 800;
}

.cal-cell--spring {
  background-color: rgba(77, 141, 255, 0.32);
  color: #ffffff;
  font-weight: 700;
}

.cal-marker {
  display: inline-block;
  margin-left: 3px;
  font-size: 0.75em;
  color: #ffffff;
  font-weight: 700;
}

/* ---- 图例 ---- */
.cal-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 24px;
  background: #000000;
  border: 1px solid #444444;
}

.cal-legend__title {
  font-size: 16px;
  font-weight: 800;
  letter-spacing: 2px;
  color: #ffffff;
  margin-bottom: 6px;
}

.cal-legend__row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  color: #ffffff;
}

.cal-tag {
  display: inline-block;
  width: 28px;
  height: 24px;
  flex-shrink: 0;
  text-align: center;
  line-height: 24px;
  font-size: 14px;
  font-weight: 800;
  color: #ffffff;
  border: 1px solid #444444;
}

.cal-tag--staff { background: rgba(255, 217, 61, 0.5); }
.cal-tag--class { background: rgba(78, 204, 163, 0.5); }
.cal-tag--holiday { background: rgba(77, 141, 255, 0.5); }
.cal-tag--grad { background: rgba(255, 45, 149, 0.5); }
.cal-tag--spring { background: rgba(77, 141, 255, 0.5); }

.cal-mark {
  display: inline-block;
  width: 28px;
  height: 24px;
  flex-shrink: 0;
  text-align: center;
  line-height: 24px;
  font-size: 16px;
  font-weight: 800;
  color: #ffffff;
  border: 1px solid #444444;
}

.cal-mark--exam { background: rgba(255, 217, 61, 0.18); color: #FFD93D; }
.cal-mark--labor { background: rgba(0, 240, 255, 0.18); color: #00F0FF; }

.cal-legend__note {
  font-size: 14px;
  color: #888888;
  margin-top: 4px;
}

@media (max-width: 640px) {
  .cal-back span {
    display: none;
  }
}
</style>