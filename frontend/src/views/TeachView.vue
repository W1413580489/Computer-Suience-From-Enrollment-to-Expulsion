<template>
  <PageShell title="" subtitle="" active-key="teach" :wide="true">
    <div class="teach" :data-theme="theme.isZzz ? 'zzz' : 'ak'" :class="{ 'teach--noside': !sideOpen }">
      <!-- 课程选择屏（ZZZ 转盘） -->
      <div v-if="view === 'select'" class="teach__wheel">
        <div class="tw-stripe"></div>
        <div class="tw-tag">
          <div class="t1">课程选择</div>
          <div class="t2">COURSE SELECT</div>
          <div class="num">{{ String(wheelIndex + 1).padStart(2, '0') }}</div>
        </div>
        <button class="tw-arrow left" title="上一个" @click="moveWheel(-1)">
          <svg viewBox="0 0 24 24"><path d="M4 12 L13 4 L13 9 L21 9 L21 15 L13 15 L13 20 Z"/></svg>
        </button>
        <button class="tw-arrow right" title="下一个" @click="moveWheel(1)">
          <svg viewBox="0 0 24 24"><path d="M20 12 L11 4 L11 9 L3 9 L3 15 L11 15 L11 20 Z"/></svg>
        </button>
        <div class="tw-hint">← → 方向键 / 点击卡片直接进入 · 回车进入当前课程</div>
        <div class="tw-ring">
          <div
            v-for="(w, i) in wheelList"
            :key="w.course_id"
            class="tw-card"
            :class="{ front: w.front, blank: w.blank }"
            :style="{ transform: `translate(${w.x}px, ${w.y}px) scale(${w.scale})`, zIndex: Math.round((1 - Number(w.gray)) * 100), filter: `grayscale(${w.gray}) brightness(${w.bright})` }"
            @click="enterCourse(i)"
          >
            <div class="tw-deco"></div>
            <div class="tw-zz">ZZ·课</div>
            <div class="tw-bignum">{{ String(i + 1).padStart(2, '0') }}</div>
            <h2>{{ w.title }}</h2>
            <div class="tw-cn">{{ w.description }}</div>
            <div class="tw-prog" v-if="!w.blank">{{ w.doneCount }} / {{ w.total }} {{ w.done ? '· 已完成' : '' }}</div>
            <div class="tw-bar" v-if="!w.blank"><i :style="{ width: w.pct + '%' }"></i></div>
            <button class="tw-btn" @click.stop="enterCourse(i)">{{ w.progBtn }}</button>
          </div>
        </div>
        <div class="tw-foot">CHOOSE YOUR COURSE · 转动选择你的课程</div>
      </div>
      <template v-else>
      <!-- 左侧配置栏 -->
      <aside class="teach__side">
        <div class="teach__group">
          <label>API Key（BYOK · 仅存本机）</label>
          <div class="teach__keyrow">
            <input v-model="apiKey" :type="showKey ? 'text' : 'password'" placeholder="sk-..." autocomplete="off" />
            <button class="teach__ghost" :title="showKey ? '隐藏' : '显示'" @click="showKey = !showKey">👁</button>
          </div>
          <div class="teach__status">
            {{ apiKey.trim() ? '已保存到本机' : '未配置 Key（访问将返回 400）' }}
          </div>
        </div>

        <div class="teach__group">
          <label>模型</label>
          <select v-model="model">
            <option v-for="m in models" :key="m.model" :value="m.model">{{ m.label }}</option>
          </select>
        </div>

        <div class="teach__group">
          <label>课程</label>
          <select v-model="courseId" @change="onCourseChange">
            <option v-for="c in courses" :key="c.course_id" :value="c.course_id">{{ c.title }}</option>
          </select>
          <label style="margin-top:6px">教学任务</label>
          <select v-model="projectId" @change="onProjectChange">
            <option v-for="p in projects" :key="p.project_id" :value="p.project_id">{{ p.title }}</option>
        </select>
        <div class="teach__progress">
          <div class="teach__progress-row">
            <span>总进度</span>
            <span>{{ progStats.done }} / {{ progStats.total }}</span>
          </div>
          <div class="teach__progress-bar"><i :style="{ width: progStats.pct + '%' }"></i></div>
        </div>
        <select v-model="taskId" @change="onTaskChange">
          <template v-for="sg in stages" :key="sg.stage_id">
            <optgroup :label="sg.title">
              <option v-for="t in sg.tasks" :key="t.task_id" :value="t.task_id">{{ taskPrefix(t.task_id) }}{{ t.title }}</option>
            </optgroup>
          </template>
        </select>
        </div>

        <div class="teach__group">
          <label>模式</label>
          <div class="teach__modes">
            <button
              v-for="m in MODES"
              :key="m.id"
              class="teach__mode"
              :class="{ active: mode === m.id }"
              @click="mode = m.id"
            >
              <div class="t">{{ m.t }}</div>
              <div class="d">{{ m.d }}</div>
            </button>
          </div>
          <details class="teach__guide">
            <summary>📘 两个模式怎么用？</summary>
            <div class="teach__guide-body">
              <p><b>指导</b> → 拆任务、推进度、帮调试，全在一个对话里。遇到报错直接把报错贴进来，AI 会自动进入调试模式帮你定位；修好后自动回到推进节奏。</p>
              <p><b>验收</b> → 做完后提交，AI 对照验收标准逐条评审打分。有未通过项就切回「指导」按意见修改，改完重新提交。</p>
              <p class="tip">💡 切换模式不会丢失对话记录；AI 当前行为（拆解中/推进中/调试中）会显示在回复下方。</p>
            </div>
          </details>
        </div>

        <div class="teach__group">
          <label>GitHub 仓库链接</label>
          <input
            v-model="repoUrl"
            class="teach__repo"
            placeholder="https://github.com/用户名/仓库名"
            autocomplete="off"
          />
          <div class="teach__status">
            {{ repoUrl.trim() ? '已设置仓库地址' : '未配置（Reviewer 将跳过 CI/代码证据）' }}
          </div>
        </div>

        <div class="teach__student">
          <label>学生状态（localStorage）</label>
          <div class="teach__badge">进度：完成任务 {{ doneCount }} · 已尝试 {{ attemptedCount }} 个任务</div>
          <div class="teach__row2">
            <button class="teach__ghost" @click="resetStudent">重置学生进度</button>
            <button class="teach__ghost" @click="clearChat">清空对话</button>
          </div>
        </div>

      </aside>

      <!-- 右侧对话区 -->
      <main class="teach__main">
        <div class="teach__chathead">
          <p class="teach__task">{{ currentTaskTitle }}</p>
          <div class="teach__chips">
            <button class="teach__metachip teach__sidetoggle" :title="sideOpen ? '收起侧栏，放大对话区' : '展开侧栏'" @click="toggleSide">{{ sideOpen ? '⇤ 收起' : '⇥ 设置' }}</button>
            <span class="teach__metachip">{{ modeLabel }}</span>
            <span class="teach__metachip">总进度 {{ progStats.done }}/{{ progStats.total }}</span>
          </div>
        </div>

        <div ref="messagesEl" class="teach__messages">
          <div v-if="chat.length === 0" class="teach__welcome">
            <h2>{{ taskObjective || '👨‍🏫 AI 项目导师' }}</h2>
            <p>{{ taskObjective ? '请选择左侧的辅导模式，开始完成这个任务。' : '选择左侧课程与任务，输入你的进展 / 代码 / 报错，AI 会按 Hint Level 渐进辅导。' }}</p>
          </div>
          <div v-for="(msg, i) in chat" :key="i" class="teach__msg" :class="msg.role">
            <!-- 系统状态条（服务异常提示，不进入 AI 对话上下文） -->
            <div v-if="msg.role === 'system'" class="teach__sysmsg">{{ msg.text }}</div>
            <!-- 学生消息：纯文本 -->
            <div v-else-if="msg.role === 'user'" class="teach__bubble">{{ msg.payload }}</div>
            <!-- AI 消息：Markdown 渲染（marked → DOMPurify 消毒 → highlight.js） -->
            <div v-else class="teach__bubble md-body" v-html="renderAiMarkdown(msg.payload?.message || '(空回复)')"></div>

            <!-- AI 结构化附加信息 -->
            <template v-if="msg.role === 'assistant' && !msg.review">
              <div class="teach__meta">
                <span v-if="msg.payload.hint_level != null" class="teach__chip hint">提示 L{{ msg.payload.hint_level }}</span>
                <span v-if="msg.payload.hints_used != null" class="teach__chip">提示档 {{ msg.payload.hints_used }}/5</span>
                <span v-if="msg.payload.behavior_label" class="teach__chip behavior">{{ msg.payload.behavior_label }}</span>
                <span v-if="msg.payload.material_sources != null" class="teach__chip">参考源 {{ msg.payload.material_sources }}</span>
                <span v-if="msg.payload.latency_ms != null" class="teach__chip">{{ msg.payload.latency_ms }} ms</span>
                <span v-if="msg.payload.debug_state && msg.payload.debug_state.rounds" class="teach__chip">调试 {{ msg.payload.debug_state.rounds }}轮 · {{ msg.payload.debug_state.phase_desc }}</span>
                <span class="teach__fb">
                  <button title="有帮助" :class="{ on: msg.feedback === true }" @click="sendFb(msg, true)">👍</button>
                  <button title="没帮助" :class="{ on: msg.feedback === false }" @click="sendFb(msg, false)">👎</button>
                </span>
              </div>

              <div v-if="qualityLines(msg.payload).length" class="teach__kv">
                <div v-for="(l, j) in qualityLines(msg.payload)" :key="j" v-html="l"></div>
              </div>
              <div v-if="(msg.payload.quality_warnings || []).length" class="teach__warn">⚠ {{ msg.payload.quality_warnings.join('<br>') }}</div>

              <!-- mode_advice 推荐卡 -->
              <div v-if="msg.payload.mode_advice" class="teach__advice">
                <div class="a-tag">▶ 建议下一步</div>
                <div class="a-reason">{{ msg.payload.mode_advice.reason }}</div>
                <div class="a-actions">
                  <button class="teach__btn" @click="applyAdvice(msg.payload.mode_advice)">切到 {{ modeName(msg.payload.mode_advice.mode) }}</button>
                </div>
                <div v-if="msg.payload.mode_advice.task_id" class="a-next">
                  目标任务：{{ msg.payload.mode_advice.task_title }}{{ msg.payload.mode_advice.task_stage_title ? `（${msg.payload.mode_advice.task_stage_title}）` : '' }}
                </div>
              </div>
            </template>

            <!-- 评审卡 -->
            <template v-if="msg.role === 'assistant' && msg.review">
              <div class="teach__reviewcard">
                <div class="teach__reviewhead">
                  <b>⚖ 评审结论 · {{ msg.review.evaluation.status }} <span :style="{ color: stColor(msg.review.evaluation.status) }">{{ stMark(msg.review.evaluation.status) }}</span></b>
                  <span class="teach__chip" style="font-size: 16px">{{ msg.review.evaluation.score ?? '–' }} / 100</span>
                </div>
                <div v-if="evidLine(msg.review)" class="teach__evline" v-html="evidLine(msg.review)"></div>
                <div v-if="ciLine(msg.review)" class="teach__evline" v-html="ciLine(msg.review)"></div>
                <div v-for="c in msg.review.evaluation.criteria || []" :key="c.rubric_id" class="teach__critrow">
                  <span :style="{ color: stColor(c.status), fontWeight: 700 }">{{ stMark(c.status) }}</span>
                  <div class="teach__critbody">
                    <div class="teach__crittitle">{{ c.rubric_id }} · {{ c.reason }}</div>
                    <div v-if="c.evidence" class="teach__critev">依据：{{ c.evidence }}</div>
                  </div>
                </div>
                <div v-if="msg.review.evaluation.next_step" class="teach__nextstep"><b>下一步：</b>{{ msg.review.evaluation.next_step }}</div>
              </div>
            </template>
          </div>
          <div v-if="loading" class="teach__msg assistant">
            <div class="teach__bubble teach__loading"><i></i><i></i><i></i> AI 思考中…</div>
          </div>
        </div>

        <div class="teach__composer">
          <textarea
            v-model="input"
            rows="2"
            placeholder="描述你当前的进展、粘贴代码或报错…（Enter 发送，Shift+Enter 换行）"
            @keydown="onKeydown"
          ></textarea>
          <button class="teach__btn" :disabled="loading" @click="send">发送</button>
        </div>
      </main>
      </template>
    </div>
    <div v-if="toastMsg" class="teach__toast">{{ toastMsg }}</div>
  </PageShell>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import PageShell from '@/components/common/PageShell.vue';
import { useThemeStore } from '@/stores/themeStore';
import { useAchievementStore } from '@/stores/achievementStore';
import { renderAiMarkdown } from '@/composables/useAiMarkdown';

const theme = useThemeStore();

const MODES = [
  { id: 'tutor', t: '指导', d: '拆任务 · 推进度 · 帮调试' },
  { id: 'reviewer', t: '验收', d: '对照标准逐条评审' },
] as const;
const MODE_NAMES = MODES.reduce<Record<string, string>>((o, m) => { o[m.id] = m.t; return o; }, {});

// ---------- 状态 ----------
const LS_STATUS = 'xkz_ai_student';
const LS_API = 'xkz_ai_api_key';
const LS_REPO = 'xkz_ai_repo';

interface StudentState { session_id: string; name: string; skills: Record<string, unknown>; completed_tasks: string[]; attempt_count: Record<string, number>; timestamp: string }
function loadStudent(): StudentState {
  try {
    const raw = localStorage.getItem(LS_STATUS);
    if (raw) { const s = JSON.parse(raw); if (s && s.session_id) return s; }
  } catch { /* ignore */ }
  return { session_id: 's_' + Math.random().toString(16).slice(2, 10), name: '匿名学生', skills: {}, completed_tasks: [], attempt_count: {}, timestamp: new Date().toISOString() };
}

interface Project { project_id: string; title: string; description: string; stages: Stage[] }
interface Stage { stage_id: string; title: string; tasks: { task_id: string; title: string; objective: string }[] }
interface CourseInfo { course_id: string; title: string; description: string; projects: Project[] }
const courses = ref<CourseInfo[]>([]);
const courseId = ref('');
const view = ref<'select' | 'tutor'>('select');
const wheelIndex = ref(0);
const suggestedNext = ref<{ task_id: string; title: string; stage_title: string } | null>(null);
const LS_SEL = 'xkz_teach_sel';
function loadSel(): any { try { return JSON.parse(localStorage.getItem(LS_SEL) || '{}'); } catch { return {}; } }
function saveSel() {
  const s = loadSel(); const by = s.task_by_course || {};
  if (courseId.value) by[courseId.value] = taskId.value;
  localStorage.setItem(LS_SEL, JSON.stringify({ course_id: courseId.value, task_by_course: by }));
}
const projects = ref<Project[]>([]);
const projectId = ref('');
const stages = ref<Stage[]>([]);
const models = ref<{ model: string; label: string }[]>([]);
const mode = ref<string>('tutor');
const apiKey = ref(localStorage.getItem(LS_API) || '');
const repoUrl = ref(localStorage.getItem(LS_REPO) || '');
const model = ref('');
const taskId = ref('');
const depUrl = ref('');
const codeBlock = ref('');
const descr = ref('');
const input = ref('');
const loading = ref(false);
const showKey = ref(false);
const statsOpen = ref(false);
// 侧栏收起状态（localStorage 持久化：'0' = 收起）
const sideOpen = ref(localStorage.getItem('xkz_teach_side') !== '0');
function toggleSide() {
  sideOpen.value = !sideOpen.value;
  localStorage.setItem('xkz_teach_side', sideOpen.value ? '1' : '0');
}
const stats = ref<Record<string, unknown> | null>(null);
const messagesEl = ref<HTMLElement | null>(null);
const toastMsg = ref('');
let toastTimer: ReturnType<typeof setTimeout> | null = null;

interface ChatMsg { role: 'user' | 'assistant' | 'system'; payload?: any; text?: string; review?: any; feedback?: boolean }
const chat = ref<ChatMsg[]>([]);
const history = ref<{ role: string; content: string }[]>([]);
const student = ref<StudentState>(loadStudent());

watch(apiKey, v => localStorage.setItem(LS_API, v.trim()));
watch(repoUrl, v => localStorage.setItem(LS_REPO, v.trim()));

// 成就：首次配置 API Key
watch(apiKey, v => { if (v.trim()) useAchievementStore().unlock('green_fruit_2'); });
// 成就：进入验收模式
watch(mode, m => {
  if (m === 'reviewer') useAchievementStore().unlock('why_birds_fly');
});

// ---------- 计算属性 ----------
const currentStage = computed(() => {
  for (const sg of stages.value) {
    if (sg.tasks.some(t => t.task_id === taskId.value)) return sg.stage_id;
  }
  return '';
});
const taskObjective = computed(() => {
  for (const sg of stages.value) {
    const t = sg.tasks.find(t => t.task_id === taskId.value);
    if (t) return t.objective || '';
  }
  return '';
});
const currentTaskTitle = computed(() => {
  for (const sg of stages.value) {
    const t = sg.tasks.find(t => t.task_id === taskId.value);
    if (t) return `${t.title} — ${t.objective || ''}`;
  }
  return '选择任务开始';
});
const modeLabel = computed(() => MODE_NAMES[mode.value] || mode.value);
const doneCount = computed(() => (student.value.completed_tasks || []).length);
const attemptedCount = computed(() => Object.keys(student.value.attempt_count || {}).length);
const blockedTasks = computed(() => {
  const b = (stats.value as any)?.probably_blocked_tasks || {};
  return Object.keys(b).join(', ') || '';
});
const hintDist = computed(() => {
  const h = (stats.value as any)?.hint_distribution || {};
  return Object.entries(h).map(([k, v]) => `L${k}:${v}`).join(' · ');
});

function isStageDone(sg: Stage) {
  const done = new Set(student.value.completed_tasks || []);
  return sg.tasks.length > 0 && sg.tasks.every(t => done.has(t.task_id));
}

// ---------- 选课屏（ZZZ 转盘）与进度 ----------
const wheelList = computed(() => {
  const real = courses.value.map((c, i) => {
    const tasks = c.projects.flatMap(p => (p.stages || []).flatMap(sg => sg.tasks));
    const doneCount = tasks.filter(t => (student.value.completed_tasks || []).includes(t.task_id)).length;
    const total = tasks.length;
    return { c, course_id: c.course_id, title: c.title, description: c.description, blank: false,
      doneCount, total, pct: total ? Math.round(doneCount / total * 100) : 0,
      done: total > 0 && doneCount === total,
      progBtn: total > 0 && doneCount === total ? '重温课程' : (doneCount > 0 ? '继续学习' : '开始学习') };
  });
  // 少于 3 张时补空白卡垫位，保证转盘两侧始终有卡片可见
  const blanks = [];
  for (let k = 0; real.length + k < 3; k++) {
    blanks.push({ course_id: `blank_${k}`, title: '更多课程', description: '后续开放 · 敬请期待', blank: true,
      doneCount: 0, total: 0, pct: 0, done: false, progBtn: '敬请期待' });
  }
  const all = [...real, ...blanks];
  const n = Math.max(all.length, 3);
  return all.map((w, i) => {
    const angle = ((i - wheelIndex.value) * (360 / n));
    const rad = angle * Math.PI / 180;
    const RX = Math.min(window.innerWidth * 0.30, 480);
    const x = Math.round(Math.sin(rad) * RX);
    const y = Math.round((1 - Math.cos(rad)) * 110);
    const depth = (Math.cos(rad) + 1) / 2;
    return { ...w, i, x, y,
      scale: +(0.62 + depth * 0.5).toFixed(3),
      gray: ((1 - depth) * 0.85).toFixed(2),
      bright: (0.55 + depth * 0.45).toFixed(2),
      front: angle % 360 === 0 };
  });
});

function moveWheel(d: number) {
  const n = Math.max(wheelList.value.length, 3);
  wheelIndex.value = ((wheelIndex.value + d) % n + n) % n;
}

function enterCourse(i: number) {
  const w = wheelList.value[i];
  if (!w || w.blank) { toast('更多课程即将开放，敬请期待'); return; }
  const c = courses.value.find(x => x.course_id === w.course_id);
  if (!c || !c.projects.length) return;
  courseId.value = c.course_id;
  projects.value = c.projects;
  const saved = loadSel().task_by_course?.[c.course_id];
  loadProject(c.projects[0]);
  if (saved && stages.value.some(sg => sg.tasks.some(t => t.task_id === saved))) {
    taskId.value = saved;   // 恢复上次学到的任务
  }
  saveSel();
  view.value = 'tutor';
}

function onWheelKey(e: KeyboardEvent) {
  // 自守卫：转盘不在 DOM（侧栏视图/已卸载）时忽略按键，免去卸载清理
  if (!document.querySelector('.teach__wheel')) return;
  if (e.key === 'ArrowLeft') moveWheel(-1);
  if (e.key === 'ArrowRight') moveWheel(1);
  if (e.key === 'Enter') enterCourse(wheelIndex.value);
}

const progStats = computed(() => {
  const tasks = stages.value.flatMap(sg => sg.tasks);
  const done = tasks.filter(t => (student.value.completed_tasks || []).includes(t.task_id)).length;
  const total = tasks.length;
  return { done, total, pct: total ? Math.round(done / total * 100) : 0 };
});

function taskPrefix(task_id: string) {
  if (task_id === taskId.value) return '● ';
  if (suggestedNext.value?.task_id === task_id) return '▶ ';
  if ((student.value.completed_tasks || []).includes(task_id)) return '✓ ';
  return '○ ';
}

// ---------- 配置加载 ----------
function loadProject(p: Project | undefined) {
  stages.value = (p?.stages || []).map(sg => ({
    stage_id: sg.stage_id, title: sg.title, tasks: (sg.tasks || []).map(t => ({ task_id: t.task_id, title: t.title, objective: t.objective || '' })),
  }));
  const first = stages.value[0]?.tasks[0];
  taskId.value = first ? first.task_id : '';
  // 换项目 = 换学习路径：清空对话（会话按 任务 隔离）
  chat.value = [];
  history.value = [];
  saveSel();
}

onMounted(async () => {
  useAchievementStore().unlock('green_fruit_1');
  window.addEventListener('keydown', onWheelKey);
  try {
    const r = await fetch(`/api/ai/config`);
    const j = await r.json();
    if (!j.ok) throw new Error(j.error?.message || 'config 加载失败');
    const cfg = j.data;
    models.value = cfg.models || [];
    if (models.value.length) model.value = models.value[0].model;
    // 多课程：courses[].projects 携带各自的 stage/task 结构
    courses.value = (cfg.courses || []).map((c: any) => ({
      course_id: c.course_id, title: c.title, description: c.description || '',
      projects: (c.projects || []).map((p: any) => ({ project_id: p.project_id, title: p.title, description: p.description || '', stages: p.stages || [] })),
    }));
    if (!courses.value.length) {
      // 兼容旧引擎：只有扁平 projects
      courses.value = [{ course_id: 'course_001', title: '默认课程', description: '', projects: (cfg.projects || []).map((p: any) => ({ project_id: p.project_id, title: p.title, description: p.description || '', stages: p.stages || [] })) }];
    }
    // 转盘默认停在学生上次学的课程；停在选课屏等待选择
    const sel = loadSel();
    const idx = courses.value.findIndex(c => c.course_id === sel.course_id);
    wheelIndex.value = idx >= 0 ? idx : 0;
  } catch (e: any) {
    toast('无法连接引擎：' + e.message);
  }
});


function onCourseChange() {
  const c = courses.value.find(x => x.course_id === courseId.value);
  projects.value = c ? c.projects : [];
  if (projects.value.length) {
    projectId.value = projects.value[0].project_id;
    loadProject(projects.value[0]);
  } else {
    projectId.value = '';
    stages.value = [];
    chat.value = [];
    history.value = [];
  }
  toast(c ? `已切换到课程：${c.title}` : '');
}

function onProjectChange() {
  const p = projects.value.find(x => x.project_id === projectId.value);
  loadProject(p);
  toast(p ? `已切换到项目：${p.title}` : '');
}

function onTaskChange() {
  // 换任务 = 新会话：清空对话，避免上一个任务的上下文串味
  chat.value = [];
  history.value = [];
  suggestedNext.value = null;
  saveSel();
}

// ---------- 发送 ----------
function saveStudent() {
  student.value.timestamp = new Date().toISOString();
  localStorage.setItem(LS_STATUS, JSON.stringify(student.value));
}

async function send() {
  const text = input.value.trim();
  if (!text || loading.value) return;
  if (!taskId.value) { toast('请先选择一个任务'); return; }
  if (!apiKey.value.trim()) { toast('请先填写 DeepSeek API Key'); return; }

  useAchievementStore().unlock('green_fruit_3');

  input.value = '';
  pushMsg('user', text);
  loading.value = true;
  scrollToBottom();

  student.value.attempt_count = student.value.attempt_count || {};
  student.value.attempt_count[taskId.value] = (student.value.attempt_count[taskId.value] || 0) + 1;

  const body = {
    session_id: student.value.session_id, student: student.value,
    course_id: courseId.value, project_id: projectId.value,
    task_id: taskId.value, mode: mode.value, user_input: text,
    repo_url: repoUrl.value.trim() || null,
    api_key: apiKey.value.trim(), model: model.value, history: history.value.slice(-6),
  };

  try {
    const r = await fetch(`/api/ai/teach`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    });
    const j = await r.json();
    if (!j.ok) {
      const code = j.error?.code || '';
      const msg = j.error?.message || '未知错误';
      if (code === 'KEY_INVALID') { toast('API Key 无效或已过期'); pushSystem(msg); }
      else if (code === 'RATE_LIMITED') { toast('服务商限流，请稍后重试'); pushSystem(msg); }
      else if (code === 'ENGINE_ERROR' || code === 'PROVIDER_DOWN' || code === 'REVIEW_UNAVAILABLE') {
        pushSystem(msg + '\n（系统故障，与你提交的项目无关，请稍后重试）');
      }
      else toast(msg);
      return;
    }
    const d = j.data;
    pushMsg('assistant', d);
    saveStudent();
  } catch (e: any) {
    pushSystem('网络请求失败：' + e.message + '\n（网络/系统故障，与你提交的项目无关，请稍后重试）');
    toast('网络请求失败：' + e.message);
  } finally {
    loading.value = false;
    scrollToBottom();
  }
}

// 系统状态条：只渲染在聊天流里，绝不写入 history（避免污染 AI 对话上下文）
function pushSystem(text: string) {
  chat.value.push({ role: 'system', text });
  scrollToBottom();
}

function pushMsg(role: 'user' | 'assistant', payload: any, review?: any) {
  chat.value.push({ role, payload, review });
  if (role === 'user') history.value.push({ role: 'user', content: typeof payload === 'string' ? payload : payload.message });
  else history.value.push({ role: 'assistant', content: payload?.message || '' });
  if (history.value.length > 40) history.value = history.value.slice(-40);
}

function scrollToBottom() {
  nextTick(() => { if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight; });
}

// ---------- 评审链 ----------
const ST_REVIEW: Record<string, [string, string]> = {
  PASS: ['✓', 'var(--t-green)'], FAIL: ['✕', 'var(--t-red)'], NEED_REVIEW: ['?', 'var(--t-yellow)'],
};
function stMark(s: string) { return (ST_REVIEW[s] || ST_REVIEW.NEED_REVIEW)[0]; }
function stColor(s: string) { return (ST_REVIEW[s] || ST_REVIEW.NEED_REVIEW)[1]; }

async function doReview() {
  if (!taskId.value) { toast('请先选择一个任务'); return; }
  if (!apiKey.value.trim()) { toast('请先填写 DeepSeek API Key'); return; }
  loading.value = true;
  scrollToBottom();
  const body = {
    session_id: student.value.session_id, task_id: taskId.value,
    submission: {
      github_url: repoUrl.value.trim() || '',
      deployment_url: depUrl.value.trim() || '',
      code: codeBlock.value.trim() || '',
      description: descr.value.trim() || '',
    },
    api_key: apiKey.value.trim(), model: model.value,
  };
  try {
    const r = await fetch(`/api/ai/review`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    });
    const j = await r.json();
    if (!j.ok) {
      const code = j.error?.code || '';
      if (code === 'REVIEW_UNAVAILABLE' || code === 'ENGINE_ERROR' || code === 'PROVIDER_DOWN') {
        pushSystem(j.error?.message || '评审服务暂时不可用（系统故障，与你提交的项目无关）');
      } else { toast(j.error?.message || '评审失败'); }
      return;
    }
    chat.value.push({ role: 'assistant', payload: { message: `评审完成：${j.data.evaluation.status}（${j.data.score} 分）` }, review: j.data });
    if (j.data.passed && !student.value.completed_tasks.includes(taskId.value)) {
      student.value.completed_tasks.push(taskId.value);
      saveStudent();
      toast('🎉 评审判定通过，任务完成！');
      const nt = j.data.next_task;
      if (nt) {
        suggestedNext.value = nt;
        chat.value.push({ role: 'assistant', payload: { message: `✓ 验收通过！建议进入下一任务：${nt.title}（${nt.stage_title}）。点击下方按钮切换，或从任务下拉选择。`, mode_advice: { task_id: nt.task_id, mode: mode.value, title: nt.title } } });
      }
    } else {
      saveStudent();
      pushSystem('评审有未通过项：切回「指导」按评审意见逐条修改，改好后重新提交验收。（对话记录已保留，可直接继续讨论未通过的原因）');
    }
  } catch (e: any) {
    toast('网络请求失败：' + e.message);
  } finally {
    loading.value = false;
    scrollToBottom();
  }
}

function esc(s: unknown) {
  return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c] as string));
}
function evidLine(d: any) {
  const ev = d.evidence || {};
  if (!ev || ev.status === 'none') return '';
  let s = '';
  if (ev.status === 'ok') s = `代码证据 ✓ 已读取仓库 ${esc(ev.repo || '')}（${ev.file_count || 0} 个文件）`;
  else if (ev.status === 'error') s = `代码证据 ✕ 未能读取：${ev.error ? esc(ev.error) : '未知原因'}${ev.code ? `（${esc(ev.code)}）` : ''}`;
  else return '';
  return s;
}
function ciLine(d: any) {
  const ci = d.ci || {};
  if (!ci || ci.status !== 'ok') return '';
  if (!Array.isArray(ci.workflows) || !ci.workflows.length) {
    return 'CI：仓库无 GitHub Actions 工作流（运行/测试类需学生提交真实运行证据）';
  }
  const map: Record<string, [string, string]> = { success: ['✓', 'var(--t-green)'], failure: ['✕', 'var(--t-red)'], none: ['·', 'var(--t-yellow)'] };
  const chips = ci.workflows.map((w: any) => {
    const c = (w.conclusion || w.status || 'none').toLowerCase();
    const [m, cc] = map[c in map ? c : 'none'];
    return `CI[${esc(w.dimension)}] ${esc(w.name)} <span style="color:${cc};font-weight:700">${m}</span>`;
  }).join(' · ');
  return `CI 自动验收：${chips}`;
}

// ---------- 反馈 / 统计 ----------
function sendFb(msg: ChatMsg, accepted: boolean) {
  fetch(`/api/ai/feedback`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: student.value.session_id, task_id: taskId.value, accepted }),
  }).then(r => r.json()).then(j => {
    if (j.ok) {
      msg.feedback = accepted;
      toast(accepted ? '已记录：有帮助' : '已记录：没帮助');
    }
  }).catch(() => { /* ignore */ });
}

async function toggleStats() {
  statsOpen.value = !statsOpen.value;
  if (statsOpen.value && !stats.value) {
    try {
      const j = await (await fetch(`/api/ai/stats`)).json();
      if (j.ok) stats.value = j.data;
      else toast('统计加载失败');
    } catch (e: any) { toast('统计加载失败：' + e.message); }
  }
}

// ---------- 其他操作 ----------
function resetStudent() {
  student.value = { session_id: 's_' + Math.random().toString(16).slice(2, 10), name: '匿名学生', skills: {}, completed_tasks: [], attempt_count: {}, timestamp: new Date().toISOString() };
  saveStudent();
  useAchievementStore().unlock('great_discipline_officer');
  toast('已重置学生进度，新会话 ' + student.value.session_id);
}
function clearChat() {
  chat.value = [];
  history.value = [];
  useAchievementStore().unlock('traveler');
}
function applyAdvice(adv: any) {
  if (adv.task_id) {
    if (taskId.value !== adv.task_id) {
      taskId.value = adv.task_id;   // 触发清单/中间标题更新；对话按任务隔离
      chat.value = [];
      history.value = [];
    }
    suggestedNext.value = null;
    saveSel();
  }
  if (adv.mode) mode.value = adv.mode;
  toast(adv.title ? '已切换到任务：' + adv.title : '已切换到 ' + (MODE_NAMES[adv.mode] || adv.mode));
}
function qualityLines(p: any): string[] {
  const lines: string[] = [];
  const esc = (s: string) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c] as string));
  if (p.leading_question) lines.push(`<b>引导问题：</b>${esc(p.leading_question)}`);
  if (p.current_step) lines.push(`<b>当前只需做：</b>${esc(p.current_step)}`);
  if (p.suspected_cause) lines.push(`<b>疑似原因：</b>${esc(p.suspected_cause)}`);
  if (p.verify_steps && p.verify_steps.length) lines.push(`<b>排查步骤：</b>${p.verify_steps.map(esc).join(' → ')}`);
  if (p.diagnostic_question) lines.push(`<b>诊断反问：</b>${esc(p.diagnostic_question)}`);
  if (p.next_action) lines.push(`<b>下一步：</b>${esc(p.next_action)}`);
  if (p.hint_level_desc) lines.push(`<b>提示档：</b>${esc(p.hint_level_desc)}`);
  return lines;
}
function modeName(m: string) { return MODE_NAMES[m] || m; }

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
}

function toast(msg: string) {
  toastMsg.value = msg;
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toastMsg.value = ''; }, 3200);
}
</script>

<style scoped>
.teach {
  --t-bg: #1A1A1A; --t-bg2: #222222; --t-bg3: #2A2A2A; --t-line: #333333;
  --t-fg: #E8E8E8; --t-dim: #999999; --t-mut: #666666;
  --t-acc: #FFD93D; --t-acc-dim: #C9A800;
  --t-green: #4ECCA3; --t-yellow: #FFD93D; --t-red: #FF5D6C;
  display: flex; gap: 0; height: calc(100vh - 120px); min-height: 600px;
  border: 1px solid var(--t-line); border-radius: 14px; overflow: hidden;
  background: var(--t-bg);
  /* 突破父容器 .hud-page-container 的 max-width: 860px 限制 */
  width: calc(100vw - 48px);
  max-width: 1400px;
  margin: 0 auto;
}
/* 日间 ak 主题 — 统一红白色调 */
.teach[data-theme='ak'] {
  --t-bg: #fafafa; --t-bg2: #ffffff; --t-bg3: #ffffff; --t-line: #e8e8e8;
  --t-fg: #1a1a1a; --t-dim: #555555; --t-mut: #999999;
  --t-acc: #c0392b; --t-acc-dim: #a93226;
  --t-green: #34d399; --t-yellow: #fbbf24; --t-red: #f87171;
}

.teach * { box-sizing: border-box; }

/* ---------- 课程选择屏（ZZZ 转盘） ---------- */
.teach__wheel { position: relative; flex: 1; overflow: hidden; background: #0c0c0c; }
.tw-stripe { position: absolute; inset: -15%; background: repeating-linear-gradient(-55deg, transparent 0 180px, rgba(255,255,255,.025) 180px 183px); }
.tw-tag { position: absolute; left: 0; top: 40px; z-index: 50; background: #FFF100; color: #111; padding: 10px 30px 10px 18px; font-weight: 900; clip-path: polygon(0 0,100% 0,calc(100% - 24px) 100%,0 100%); }
.tw-tag .t1 { font-size: 17px; letter-spacing: 2px; }
.tw-tag .t2 { font-size: 10px; font-weight: 400; letter-spacing: 3px; opacity: .7; }
.tw-tag .num { font-size: 38px; line-height: 1.1; }
.tw-arrow { position: absolute; top: 46%; z-index: 60; width: 72px; height: 62px; background: #0a0a0a; border: 2px solid #4a4a4a; border-radius: 42% 58% 52% 48% / 58% 42% 58% 42%; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all .18s; }
.tw-arrow svg { width: 32px; height: 32px; fill: #fff; transition: fill .18s; }
.tw-arrow:hover { background: #FFF100; border-color: #FFF100; transform: scale(1.08); }
.tw-arrow:hover svg { fill: #111; }
.tw-arrow.right { right: 30px; transform: rotate(-8deg); }
.tw-arrow.right:hover { transform: rotate(-8deg) scale(1.08); }
.tw-arrow.left { left: 30px; transform: rotate(8deg); }
.tw-arrow.left:hover { transform: rotate(8deg) scale(1.08); }
.tw-hint { position: absolute; top: 18px; right: 20px; z-index: 60; font-size: 12px; color: #555; }
.tw-ring { position: absolute; inset: 0; }
.tw-card { position: absolute; left: 50%; top: 50%; width: 300px; height: 470px; margin: -235px 0 0 -150px; background: #141414; border: 1px solid #2b2b2b; border-radius: 10px; overflow: hidden; cursor: pointer; transition: transform .55s cubic-bezier(.25,.8,.3,1), filter .55s, border-color .3s; will-change: transform; }
.tw-card.front { cursor: pointer; border-color: #3f3f3f; }
.tw-card.front:hover { border-color: #FFF100; }
.tw-deco { position: absolute; inset: 0; background: linear-gradient(165deg, #202020 0%, #151515 55%, #111 100%); }
.tw-deco::after { content: ""; position: absolute; inset: 0; background: repeating-linear-gradient(-55deg, transparent 0 30px, rgba(255,255,255,.045) 30px 34px); clip-path: polygon(52% 0,100% 0,100% 100%,14% 100%); }
.tw-zz { position: absolute; top: 16px; left: 16px; z-index: 2; font-weight: 900; font-size: 14px; letter-spacing: 1px; color: #999; }
.tw-bignum { position: absolute; right: -8px; bottom: -34px; z-index: 1; font-size: 150px; font-weight: 900; color: rgba(255,255,255,.05); line-height: 1; }
.tw-card h2 { position: absolute; left: 20px; top: 70px; z-index: 2; font-size: 22px; line-height: 1.3; font-weight: 900; letter-spacing: 1px; color: #ccc; padding-right: 18px; }
.tw-cn { position: absolute; left: 20px; top: 168px; z-index: 2; font-size: 13px; color: #888; right: 18px; }
.tw-prog { position: absolute; left: 20px; bottom: 96px; z-index: 2; font-size: 12px; color: #666; }
.tw-bar { position: absolute; left: 20px; bottom: 84px; z-index: 2; width: 150px; height: 3px; background: #2c2c2c; border-radius: 2px; }
.tw-bar i { display: block; height: 3px; background: #FFF100; border-radius: 2px; }
.tw-btn { position: absolute; left: 20px; bottom: 24px; z-index: 2; padding: 10px 26px; font-size: 13px; font-weight: 700; letter-spacing: 2px; border: 0; border-radius: 4px; cursor: pointer; background: #2a2a2a; color: #666; }
.tw-card.front .tw-zz { color: #FFF100; }
.tw-card.front h2 { font-size: 26px; color: #fff; }
.tw-card.front .tw-cn { font-size: 13px; color: #999; top: 196px; }
.tw-card.front .tw-prog { color: #FFF100; font-weight: 700; font-size: 13px; }
.tw-card.front .tw-bar { width: 240px; }
.tw-card.front .tw-deco::after { background: repeating-linear-gradient(-55deg, transparent 0 30px, rgba(255,241,0,.07) 30px 34px); }
.tw-card.front .tw-btn { background: #FFF100; color: #111; }
.tw-card.front .tw-btn:hover { transform: scale(1.04); }
.tw-card.blank { border-style: dashed; border-color: #333; }
.tw-card.blank .tw-btn { cursor: default; }
.tw-foot { position: absolute; bottom: 18px; left: 0; right: 0; text-align: center; font-size: 12px; color: #666; letter-spacing: 4px; z-index: 60; }

/* ---------- 任务进度条 ---------- */
.teach__progress { margin-bottom: 6px; }
.teach__progress-row { display: flex; justify-content: space-between; font-size: 12px; color: var(--t-dim); margin-bottom: 4px; }
.teach__progress-row span:last-child { color: var(--t-acc); font-weight: 700; }
.teach__progress-bar { height: 4px; background: var(--t-bg3); border-radius: 2px; overflow: hidden; }
.teach__progress-bar i { display: block; height: 4px; background: var(--t-acc); border-radius: 2px; transition: width .3s; }
.teach__stagechip { display: none; }

.teach__side {
  width: 320px; min-width: 320px; border-right: 1px solid var(--t-line);
  background: var(--t-bg2); padding: 16px 14px; overflow-y: auto;
  display: flex; flex-direction: column; gap: 14px;
}
.teach__group { display: flex; flex-direction: column; gap: 5px; }
.teach__group label { font-size: 12px; color: var(--t-dim); font-weight: 600; letter-spacing: .03em; }
.teach select, .teach input, .teach textarea {
  background: var(--t-bg3); border: 1px solid var(--t-line); color: var(--t-fg);
  border-radius: 8px; padding: 8px 10px; font-size: 13px; width: 100%;
  outline: none; transition: border-color .15s; font-family: inherit;
}
.teach select:focus, .teach input:focus, .teach textarea:focus { border-color: var(--t-acc); }
.teach textarea { resize: vertical; min-height: 48px; }
.teach__code-area { min-height: 54px; font-family: ui-monospace, Consolas, monospace; font-size: 12px; }
.teach__keyrow { display: flex; gap: 8px; align-items: center; }
.teach__keyrow input { flex: 1; }
.teach__hint { font-size: 11px; color: var(--t-mut); }
.teach__status { font-size: 11px; color: var(--t-mut); }
.teach__stages { display: flex; gap: 4px; margin-bottom: 4px; flex-wrap: wrap; }
.teach__stagechip {
  flex: 1; min-width: 0; text-align: center; font-size: 11px; line-height: 1.3;
  padding: 4px 2px; border-radius: 6px; border: 1px solid var(--t-line);
  background: var(--t-bg3); color: var(--t-mut); pointer-events: none;
}
.teach__stagechip.active { border-color: var(--t-acc); color: var(--t-acc); font-weight: 700; }
.teach[data-theme='ak'] .teach__stagechip.active { background: rgba(192, 57, 43, .08); }
.teach__stagechip.done { border-color: var(--t-green); color: var(--t-green); }
.teach__modes { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.teach__mode {
  background: var(--t-bg3); border: 1px solid var(--t-line); color: var(--t-fg);
  border-radius: 8px; padding: 8px; cursor: pointer; text-align: left; font-size: 12px; transition: .15s;
}
.teach__mode .t { font-weight: 600; font-size: 13px; }
.teach__mode .d { color: var(--t-mut); font-size: 11px; }
.teach__mode.active { border-color: var(--t-acc); box-shadow: 0 0 0 1px var(--t-acc); }
.teach__guide { margin-top: 6px; }
.teach__guide summary { cursor: pointer; font-size: 12px; color: var(--t-dim); }
.teach__guide summary:hover { color: var(--t-fg); }
.teach__guide-body {
  font-size: 12px; color: var(--t-dim); margin-top: 6px; border: 1px solid var(--t-line);
  background: var(--t-bg3); border-radius: 8px; padding: 8px 10px;
  display: flex; flex-direction: column; gap: 8px;
}
.teach__guide-body p { margin: 0; }
.teach__guide-body .tip { color: var(--t-acc); }
.teach__btn {
  background: var(--t-acc); color: #fff; border: 0; border-radius: 8px;
  padding: 8px 14px; font-size: 13px; font-weight: 600; cursor: pointer; transition: .15s;
}
.teach__btn:hover { background: var(--t-acc-dim); }
.teach__btn:disabled { opacity: .5; cursor: not-allowed; }
.teach__ghost {
  background: transparent; border: 1px solid var(--t-line); color: var(--t-dim);
  border-radius: 8px; padding: 7px 10px; font-size: 12px; cursor: pointer; transition: .15s;
}
.teach__ghost:hover { color: var(--t-fg); border-color: var(--t-acc); }
.teach__full { width: 100%; }
.teach__row2 { display: flex; gap: 8px; }
.teach__row2 .teach__ghost { flex: 1; }
.teach__student { display: flex; flex-direction: column; gap: 6px; }
.teach__badge {
  display: flex; align-items: center; gap: 6px; background: var(--t-bg3); border: 1px solid var(--t-line);
  border-radius: 8px; padding: 4px 9px; font-size: 12px; color: var(--t-dim);
}
.teach__stats { font-size: 11px; color: var(--t-dim); display: flex; flex-direction: column; gap: 3px; }
.teach__stats b { color: var(--t-fg); }
.teach__red { color: var(--t-red); }
.teach__yellow { color: var(--t-yellow); }
.teach__dim { color: var(--t-mut); }
.teach__apifoot { margin-top: auto; }

/* 右侧对话区 */
.teach__main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
/* 侧栏收起：对话区占满 */
.teach--noside .teach__side { display: none; }
/* 侧栏开关：实心强调色按钮，醒目 */
.teach__sidetoggle {
  cursor: pointer; border: 1px solid var(--t-acc);
  background: var(--t-acc); color: var(--t-bg);
  font: inherit; font-size: 12px; font-weight: 700; letter-spacing: .02em;
  padding: 3px 14px; border-radius: 999px;
  box-shadow: 0 1px 4px color-mix(in srgb, var(--t-acc) 45%, transparent);
}
.teach__sidetoggle:hover { filter: brightness(1.12); transform: translateY(-1px); }
.teach__sidetoggle:active { transform: translateY(0); }
.teach__chathead {
  padding: 10px 18px; border-bottom: 1px solid var(--t-line); background: var(--t-bg2);
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
}
.teach__chathead .teach__task { margin: 0; font-size: 13px; color: var(--t-fg); }
.teach__chips { display: flex; gap: 8px; }
.teach__metachip {
  font-size: 11px; color: var(--t-dim); background: var(--t-bg3); border: 1px solid var(--t-line);
  border-radius: 20px; padding: 3px 10px; white-space: nowrap;
}
.teach__messages {
  flex: 1; overflow-y: auto; padding: 18px;
  display: flex; flex-direction: column; gap: 14px;
}
.teach__welcome { max-width: 560px; margin: auto auto; text-align: center; color: var(--t-mut); }
.teach__welcome h2 { color: var(--t-dim); font-size: 20px; font-weight: 600; margin-bottom: 10px; line-height: 1.5; }
.teach__welcome p { font-size: 13px; line-height: 1.7; color: var(--t-dim); }
.teach__msg { display: flex; flex-direction: column; }
.teach__msg.user { align-self: flex-end; align-items: flex-end; }
.teach__msg.assistant { align-self: flex-start; align-items: flex-start; max-width: 88%; }
.teach__bubble {
  max-width: 100%; background: var(--t-bg3); border: 1px solid var(--t-line);
  border-radius: 14px; padding: 11px 13px; white-space: pre-wrap; word-break: break-word; color: var(--t-fg);
}
.teach__msg.user .teach__bubble { background: var(--t-acc); border-color: var(--t-acc); color: #fff; }
/* AI 消息 Markdown 正文 */
.teach__bubble.md-body { white-space: normal; }
.md-body > :first-child { margin-top: 0; }
.md-body > :last-child { margin-bottom: 0; }
.md-body p { margin: 6px 0; }
.md-body ul, .md-body ol { margin: 6px 0; padding-left: 20px; }
.md-body li { margin: 3px 0; }
.md-body h1, .md-body h2, .md-body h3, .md-body h4 { margin: 10px 0 6px; font-size: 15px; }
.md-body blockquote { margin: 6px 0; padding: 4px 10px; border-left: 3px solid var(--t-acc-dim); color: var(--t-dim); }
.md-body code:not(.hljs) {
  background: rgba(128, 128, 128, 0.18); border-radius: 4px; padding: 1px 5px;
  font-family: ui-monospace, Consolas, monospace; font-size: 12.5px;
}
.md-body pre {
  background: #14161a; color: #e6e6e6; border-radius: 8px; padding: 10px 12px;
  overflow-x: auto; margin: 8px 0; font-size: 12.5px; line-height: 1.55;
}
.md-body pre code { font-family: ui-monospace, Consolas, monospace; background: none; padding: 0; white-space: pre; }
.md-body table { border-collapse: collapse; margin: 8px 0; font-size: 12.5px; }
.md-body th, .md-body td { border: 1px solid var(--t-line); padding: 4px 8px; text-align: left; }
.md-body th { background: rgba(128, 128, 128, 0.12); }
.md-body a { color: var(--t-acc); }
/* highlight.js 令牌配色（代码块固定深底，两主题通用） */
.md-body .hljs-keyword, .md-body .hljs-built_in { color: #c792ea; }
.md-body .hljs-string, .md-body .hljs-attr { color: #a5e075; }
.md-body .hljs-comment { color: #6a737d; font-style: italic; }
.md-body .hljs-number, .md-body .hljs-literal { color: #f78c6c; }
.md-body .hljs-title, .md-body .hljs-function, .md-body .hljs-name { color: #82aaff; }
.md-body .hljs-type, .md-body .hljs-class { color: #ffcb6b; }
.teach__msg.system { align-self: center; max-width: 92%; }
.teach__sysmsg {
  background: color-mix(in srgb, var(--t-yellow) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--t-yellow) 40%, transparent);
  color: var(--t-yellow); border-radius: 8px; padding: 8px 12px;
  font-size: 12px; text-align: center; white-space: pre-wrap; word-break: break-word;
}
.teach__meta { font-size: 11px; color: var(--t-mut); margin-top: 6px; display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.teach__chip {
  background: color-mix(in srgb, var(--t-acc) 14%, transparent); color: var(--t-acc);
  border: 1px solid color-mix(in srgb, var(--t-acc) 35%, transparent);
  border-radius: 6px; padding: 1px 7px; font-size: 11px;
}
.teach__chip.hint {
  background: color-mix(in srgb, var(--t-yellow) 14%, transparent); color: var(--t-yellow);
  border-color: color-mix(in srgb, var(--t-yellow) 35%, transparent);
}
.teach__chip.behavior {
  background: color-mix(in srgb, var(--t-green) 14%, transparent); color: var(--t-green);
  border-color: color-mix(in srgb, var(--t-green) 35%, transparent);
}
.teach__chip.fail {
  background: color-mix(in srgb, var(--t-red) 14%, transparent); color: var(--t-red);
  border-color: color-mix(in srgb, var(--t-red) 35%, transparent);
}
.teach__fb { display: inline-flex; gap: 4px; margin-left: 4px; align-items: center; }
.teach__fb button {
  background: transparent; border: 1px solid var(--t-line); color: var(--t-dim);
  border-radius: 6px; width: 22px; height: 22px; cursor: pointer; font-size: 12px; line-height: 1;
}
.teach__fb button:hover { border-color: var(--t-acc); color: var(--t-acc); }
.teach__fb button.on { background: color-mix(in srgb, var(--t-acc) 20%, transparent); border-color: var(--t-acc); color: var(--t-fg); }
.teach__kv {
  font-size: 12px; color: var(--t-dim); border-top: 1px dashed var(--t-line);
  margin-top: 8px; padding-top: 6px; display: flex; flex-direction: column; gap: 2px;
}
.teach__kv b { color: var(--t-fg); }
.teach__warn {
  background: color-mix(in srgb, var(--t-red) 9%, transparent);
  border: 1px solid color-mix(in srgb, var(--t-red) 28%, transparent); color: var(--t-red);
  border-radius: 8px; padding: 6px 10px; font-size: 12px; margin-top: 8px; white-space: pre-wrap;
}
.teach__advice {
  margin-top: 10px; border: 1px solid color-mix(in srgb, var(--t-acc) 45%, transparent);
  background: color-mix(in srgb, var(--t-acc) 10%, transparent); border-radius: 10px;
  padding: 9px 12px; display: flex; flex-direction: column; gap: 8px; align-items: flex-start;
}
.teach__advice .a-tag { font-size: 11px; font-weight: 700; color: var(--t-acc); letter-spacing: .04em; }
.teach__advice .a-reason { font-size: 13px; color: var(--t-fg); }
.teach__advice .a-actions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.teach__advice .a-actions .teach__btn { padding: 6px 12px; font-size: 12px; }
.teach__advice .a-next { font-size: 11px; color: var(--t-mut); }

/* 评审卡 */
.teach__reviewcard {
  margin-top: 8px; background: var(--t-bg3); border: 1px solid var(--t-line);
  border-radius: 14px; padding: 12px 14px; min-width: 340px; max-width: 100%;
}
.teach__reviewhead {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;
  font-size: 14px; color: var(--t-fg);
}
.teach__evline { font-size: 11px; color: var(--t-dim); margin: 2px 0 6px; }
.teach__critrow {
  display: flex; gap: 8px; align-items: flex-start; padding: 7px 0;
  border-bottom: 1px solid var(--t-line);
}
.teach__critbody { flex: 1; min-width: 0; }
.teach__crittitle { font-weight: 600; color: var(--t-fg); }
.teach__critev { color: var(--t-dim); font-size: 12px; }
.teach__nextstep { margin-top: 8px; color: var(--t-dim); }
.teach__nextstep b { color: var(--t-fg); }

/* 输入区 */
.teach__composer {
  border-top: 1px solid var(--t-line); padding: 10px 14px; background: var(--t-bg2);
  display: flex; gap: 10px; align-items: flex-end;
}
.teach__composer textarea { flex: 1; min-height: 44px; max-height: 140px; }
.teach__loading { display: inline-flex; gap: 4px; align-items: center; color: var(--t-mut); }
.teach__loading i { width: 6px; height: 6px; border-radius: 50%; background: var(--t-acc); animation: tb 1.1s infinite; }
.teach__loading i:nth-child(2) { animation-delay: .15s; }
.teach__loading i:nth-child(3) { animation-delay: .3s; }
@keyframes tb { 0%, 60%, 100% { opacity: .25; transform: scale(.8); } 30% { opacity: 1; transform: scale(1); } }

.teach__toast {
  position: fixed; top: 70px; left: 50%; transform: translateX(-50%);
  background: #2a2110; border: 1px solid var(--t-yellow); color: #fde68a;
  padding: 9px 16px; border-radius: 9px; font-size: 13px; z-index: 99; max-width: 80%;
}

@media (max-width: 760px) {
  .teach { flex-direction: column; height: auto; min-height: 70vh; }
  .teach__side { width: 100%; min-width: 0; max-height: 46vh; border-right: 0; border-bottom: 1px solid var(--t-line); }
  .teach__messages { min-height: 300px; }
  .teach__reviewcard { min-width: 0; }
}

/* ============================================
   夜间 zzz 主题 — 绝区零风格（克制版）
   深灰底 + 黄色仅用于 active 填充 / 点缀
   无辉光 / 无扫描线 / 小圆角
   放在末尾确保源码顺序优先
   ============================================ */
.teach[data-theme='zzz'] {
  --t-bg: #1A1A1A; --t-bg2: #222222; --t-bg3: #2A2A2A; --t-line: #333333;
  --t-fg: #E8E8E8; --t-dim: #999999; --t-mut: #666666;
  --t-acc: #FFD93D; --t-acc-dim: #C9A800;
  --t-green: #4ECCA3; --t-yellow: #FFD93D; --t-red: #FF5D6C;
  border-radius: 10px; border-color: #333; box-shadow: none; background: var(--t-bg);
}
.teach[data-theme='zzz'] .teach__side { border-right-color: #333; }
.teach[data-theme='zzz'] .teach__chathead { border-bottom-color: #333; }
.teach[data-theme='zzz'] .teach__composer { border-top-color: #333; }
.teach[data-theme='zzz'] .teach__btn {
  background: #333; color: var(--t-fg); border: 1px solid #444; border-radius: 6px; font-weight: 600;
}
.teach[data-theme='zzz'] .teach__btn:hover {
  background: var(--t-acc); color: #0A0A0A; border-color: var(--t-acc); box-shadow: none;
}
.teach[data-theme='zzz'] .teach__ghost {
  background: transparent; color: var(--t-dim); border: 1px solid #444; border-radius: 6px;
}
.teach[data-theme='zzz'] .teach__ghost:hover {
  color: #0A0A0A; border-color: var(--t-acc); background: var(--t-acc); box-shadow: none;
}
.teach[data-theme='zzz'] .teach__mode {
  border-radius: 6px; border: 1px solid #444; background: #2A2A2A;
}
.teach[data-theme='zzz'] .teach__mode.active {
  border-color: var(--t-acc); background: var(--t-acc) !important; color: #0A0A0A !important; box-shadow: none !important;
}
.teach[data-theme='zzz'] .teach__mode.active .t { color: #0A0A0A !important; font-weight: 700; }
.teach[data-theme='zzz'] .teach__mode.active .d { color: rgba(10,10,10,0.6) !important; }
.teach[data-theme='zzz'] .teach__stagechip {
  border-radius: 4px; border: 1px solid #444; background: #2A2A2A;
}
.teach[data-theme='zzz'] .teach__stagechip.active {
  border-color: var(--t-acc); background: var(--t-acc) !important; color: #0A0A0A !important; font-weight: 700;
}
.teach[data-theme='zzz'] .teach__stagechip.done {
  border-color: var(--t-green); background: var(--t-green) !important; color: #0A0A0A !important;
}
.teach[data-theme='zzz'] select:focus,
.teach[data-theme='zzz'] input:focus,
.teach[data-theme='zzz'] textarea:focus {
  border-color: var(--t-acc); box-shadow: none;
}
.teach[data-theme='zzz'] .teach__msg.user .teach__bubble {
  background: #2A2A2A !important; border: 1px solid #444; color: var(--t-fg) !important; border-left: 3px solid var(--t-acc);
}
.teach[data-theme='zzz'] .teach__reviewcard {
  border: 1px solid #444; border-top: 2px solid var(--t-acc); border-radius: 8px; box-shadow: none;
}
.teach[data-theme='zzz'] .teach__advice {
  border: 1px solid #444; border-left: 3px solid var(--t-acc); background: #222; border-radius: 6px;
}
.teach[data-theme='zzz'] .teach__advice .a-tag {
  color: var(--t-acc); text-shadow: none;
}
.teach[data-theme='zzz'] .teach__loading i {
  background: var(--t-acc); box-shadow: none;
}
.teach[data-theme='zzz'] .teach__chip,
.teach[data-theme='zzz'] .teach__metachip,
.teach[data-theme='zzz'] .teach__badge,
.teach[data-theme='zzz'] .teach__bubble,
.teach[data-theme='zzz'] .teach__warn {
  border-radius: 6px; clip-path: none;
}
</style>

