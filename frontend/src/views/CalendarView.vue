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
  s?: boolean;
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
/* 纯黑底白字：取消所有切角、霓虹、彩色 */
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
  width: 64px;
}

.cal-th-month {
  width: 140px;
}

.cal-week {
  font-weight: 900;
  color: #ffffff;
  background: #111111;
  font-size: clamp(15px, 1.7vw, 19px);
}

.cal-week em {
  display: inline-block;
  margin-left: 3px;
  font-style: normal;
  font-weight: 700;
}

.cal-month {
  font-size: clamp(13px, 1.5vw, 16px);
  color: #cccccc;
  background: #111111;
  letter-spacing: 1px;
}

.cal-mark-exam {
  background: #1a1a1a;
}

.cal-mark-labor {
  background: #0d0d0d;
}

.cal-mark-exam .cal-week em { color: #ffffff; }
.cal-mark-labor .cal-week em { color: #ffffff; }

/* 特殊日：保留色彩标记（黄绿蓝红），但用文字色而非背景色突出 */
.cal-cell-staff { color: #FFD93D; font-weight: 800; }
.cal-cell-class { color: #4ECCA3; font-weight: 700; }
.cal-cell-holiday { color: #4D8DFF; font-weight: 700; }
.cal-cell-grad { color: #FF2D95; font-weight: 800; }
.cal-cell-spring { color: #4D8DFF; font-weight: 700; }

.cal-marker {
  display: inline-block;
  margin-left: 2px;
  font-size: 0.7em;
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
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  text-align: center;
  line-height: 24px;
  font-size: 13px;
  font-weight: 700;
  color: #000000;
  border: 1px solid #444444;
}

.cal-tag--staff { background: #FFD93D; }
.cal-tag--class { background: #4ECCA3; }
.cal-tag--holiday { background: #4D8DFF; color: #ffffff; }
.cal-tag--grad { background: #FF2D95; color: #ffffff; }
.cal-tag--spring { background: #4D8DFF; color: #ffffff; }

.cal-mark {
  display: inline-block;
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  text-align: center;
  line-height: 24px;
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  border: 1px solid #444444;
}

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