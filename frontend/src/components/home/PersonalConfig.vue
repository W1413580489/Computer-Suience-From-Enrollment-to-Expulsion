<template>
  <section class="pc">
    <SectionHeader num="04" title="个人配置" en="PERSONAL CONFIG" />

    <!-- 按钮行 -->
    <div class="pc__row">
      <div class="pc__row-head">
        <span class="pc__row-title">// BUTTONS / 按钮系统</span>
        <span class="pc__row-line" />
      </div>
      <div class="pc__btns">
        <!-- 夜间 zzz：zenless-ui 按钮 -->
        <template v-if="theme.isZzz">
          <z-button type="primary" size="large" class="pc__zbtn" @click="goCalendar">校历</z-button>
          <z-button size="large" class="pc__zbtn" @click="goProject">项目</z-button>
          <z-button type="fire" size="large" class="pc__zbtn" @click="emit('onOpenApi')">设置</z-button>
          <z-button v-if="userStore.isLoggedIn" size="large" class="pc__zbtn" @click="switchIdentity">切换身份</z-button>
        </template>
        <!-- 日间 ak：原版按钮 -->
        <template v-else>
          <button class="pc__btn pc__btn--primary" @click="goCalendar">校历 <em>CALENDAR</em></button>
          <button class="pc__btn pc__btn--secondary" @click="goProject">项目 <em>PROJECT</em></button>
          <button class="pc__btn pc__btn--neon" @click="emit('onOpenApi')">设置 <em>SETTINGS</em></button>
          <button v-if="userStore.isLoggedIn" class="pc__btn pc__btn--secondary" @click="switchIdentity">切换身份 <em>SWITCH</em></button>
        </template>
      </div>
    </div>

    <!-- 标签行 -->
    <div class="pc__row">
      <div class="pc__row-head">
        <span class="pc__row-title">// BADGES / 情绪标签</span>
        <span class="pc__row-line" />
      </div>
      <div class="pc__badges">
        <!-- 夜间 zzz：zenless-ui 标签 -->
        <template v-if="theme.isZzz">
          <z-tag v-for="(b, i) in activeBadges" :key="i" :type="badgeType(i)">{{ b.text }}</z-tag>
        </template>
        <!-- 日间 ak：原版标签 -->
        <template v-else>
          <span
            v-for="(b, i) in activeBadges"
            :key="i"
            class="pc__badge"
            :class="badgeClass(i)"
          >{{ b.text }} <em>{{ b.en }}</em></span>
        </template>
      </div>
    </div>

    <!-- 主面板：左开关 / 中进度条 / 右开关 -->
    <div class="pc__panel">
      <div class="pc__panel-head">
        <span class="pc__row-title">// TOGGLE &amp; PROGRESS / 开关与进度条</span>
        <span class="pc__row-line" />
      </div>
      <div class="pc__grid">
        <!-- 左开关 3 项 -->
        <div class="pc__col">
          <div class="pc__switch">
            <span class="pc__switch-label">登录</span>
            <!-- 夜间 zzz：zenless-ui 开关（锁定开启） -->
            <z-switch v-if="theme.isZzz" :model-value="true" disabled />
            <!-- 日间 ak：原版开关 -->
            <button v-else class="pc__toggle pc__toggle--on pc__toggle--locked" disabled aria-label="登录（始终开启）">
              <span class="pc__toggle-thumb" />
              <span class="pc__toggle-text">ON</span>
            </button>
          </div>
          <div class="pc__switch">
            <span class="pc__switch-label">轨道模式</span>
            <z-switch
              v-if="theme.isZzz"
              v-model="flags.rail"
              @change="onLaunch('rail', 'https://sr.mihoyo.com/')"
            />
            <button
              v-else
              class="pc__toggle"
              :class="{ 'pc__toggle--on': flags.rail }"
              @click="onLaunch('rail', 'https://sr.mihoyo.com/')"
            >
              <span class="pc__toggle-thumb" />
              <span class="pc__toggle-text">{{ flags.rail ? 'ON' : 'OFF' }}</span>
            </button>
          </div>
          <div class="pc__switch">
            <span class="pc__switch-label">项目仓库</span>
            <z-switch
              v-if="theme.isZzz"
              v-model="flags.repo"
              @change="onLaunch('repo', 'https://github.com/')"
            />
            <button
              v-else
              class="pc__toggle"
              :class="{ 'pc__toggle--on': flags.repo }"
              @click="onLaunch('repo', 'https://github.com/')"
            >
              <span class="pc__toggle-thumb" />
              <span class="pc__toggle-text">{{ flags.repo ? 'ON' : 'OFF' }}</span>
            </button>
          </div>
        </div>

        <!-- 中进度条 3 项 -->
        <div class="pc__col pc__col--bars">
          <div v-for="(bar, i) in activeBars" :key="i" class="pc__bar">
            <div class="pc__bar-head">
              <span class="pc__bar-label">{{ bar.label }}</span>
              <span class="pc__bar-val" :class="barToneClass(bar.tone)">{{ bar.value }}%</span>
            </div>
            <!-- 夜间 zzz：zenless-ui 进度条 / 日间 ak：原版 -->
            <z-progress
              v-if="theme.isZzz"
              :percent="bar.value"
              :color="bar.tone === 'red' ? 'danger' : bar.tone === 'green' ? 'success' : undefined"
            />
            <div v-else class="pc__bar-track">
              <div
                class="pc__bar-fill"
                :class="{ 'pc__bar-fill--red': bar.tone === 'red', 'pc__bar-fill--green': bar.tone === 'green' }"
                :style="{ '--w': bar.value + '%' }"
              />
            </div>
          </div>
        </div>

        <!-- 右开关 4 项 -->
        <div class="pc__col">
          <div class="pc__switch">
            <span class="pc__switch-label">调制模式</span>
            <z-switch v-if="theme.isZzz" v-model="flags.mod" @change="onModToggle" />
            <button
              v-else
              class="pc__toggle"
              :class="{ 'pc__toggle--on': flags.mod }"
              @click="onModToggle"
            >
              <span class="pc__toggle-thumb" />
              <span class="pc__toggle-text">{{ flags.mod ? 'ON' : 'OFF' }}</span>
            </button>
          </div>
          <div class="pc__switch">
            <span class="pc__switch-label">知识检索RAG</span>
            <z-switch v-if="theme.isZzz" v-model="flags.rag" />
            <button
              v-else
              class="pc__toggle"
              :class="{ 'pc__toggle--on': flags.rag }"
              @click="toggle('rag')"
            >
              <span class="pc__toggle-thumb" />
              <span class="pc__toggle-text">{{ flags.rag ? 'ON' : 'OFF' }}</span>
            </button>
          </div>
          <div class="pc__switch">
            <span class="pc__switch-label">网站设置</span>
            <z-switch v-if="theme.isZzz" v-model="flags.settings" @click="onSettingsClick" />
            <button
              v-else
              ref="settingsBtn"
              class="pc__toggle"
              :class="{ 'pc__toggle--on': flags.settings }"
              @click="toggle('settings')"
            >
              <span class="pc__toggle-thumb" />
              <span class="pc__toggle-text">{{ flags.settings ? 'ON' : 'OFF' }}</span>
            </button>
          </div>
          <div class="pc__switch">
            <span class="pc__switch-label">区域探索</span>
            <z-switch
              v-if="theme.isZzz"
              v-model="flags.area"
              @change="onLaunch('area', 'https://ys.mihoyo.com/')"
            />
            <button
              v-else
              class="pc__toggle pc__toggle--locked"
              :class="{ 'pc__toggle--on': flags.area }"
              @click="onLaunch('area', 'https://ys.mihoyo.com/')"
            >
              <span class="pc__toggle-thumb" />
              <span class="pc__toggle-text">{{ flags.area ? 'ON' : 'OFF' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 网站设置弹窗：Teleport 到 body，避免父级 .hud-fade-in 的 transform 破坏 z-modal 的 position:fixed 上下文 -->
    <Teleport v-if="theme.isZzz && showSettingsAlert" to="body">
      <z-modal
        v-model="showSettingsAlert"
        title="网站设置 · SETTINGS"
        :show-footer="false"
        @close="closeAlert"
      >
        <p class="pc__alert-line">你想设置什么？</p>
        <p class="pc__alert-line">你想设置什么！</p>
        <p class="pc__alert-line pc__alert-line--dim">想要就找我发源代码</p>
      </z-modal>
    </Teleport>
    <Teleport v-else to="body">
      <div v-if="showSettingsAlert" class="pc__alert-mask" @click.self="closeAlert">
        <div class="pc__alert" role="dialog" aria-modal="true">
          <button class="pc__alert-close" aria-label="关闭" @click="closeAlert">×</button>
          <p>你想设置什么？</p>
          <p>你想设置什么！</p>
          <p>想要就找我发源代码</p>
        </div>
      </div>
    </Teleport>

    <!-- 日间 ak：自定义 message 浮层 -->
    <Teleport v-if="!theme.isZzz" to="body">
      <Transition name="pc-msg">
        <div v-if="akMsg.visible" class="pc__msg" :class="`pc__msg--${akMsg.type}`">
          <span class="pc__msg-icon">{{ akMsg.type === 'error' ? '✕' : akMsg.type === 'warning' ? '!' : '✓' }}</span>
          <span class="pc__msg-text">{{ akMsg.text }}</span>
        </div>
      </Transition>
    </Teleport>

    <!-- 全屏 Modal：第三次打开调制模式后显示 -->
    <!-- 夜间 zzz：zenless-ui 居中弹窗 -->
    <Teleport v-if="theme.isZzz" to="body">
      <z-modal
        v-model="showModModal"
        title="闲得慌 · BORED"
        :show-footer="false"
        @close="showModModal = false"
      >
        <p class="pc__modal-text">你真是一个闲的慌的人。。。。</p>
      </z-modal>
    </Teleport>
    <!-- 日间 ak：自定义全屏模态 -->
    <Teleport v-else to="body">
      <Transition name="pc-modal">
        <div v-if="showModModal" class="pc__fullscreen" @click="showModModal = false">
          <div class="pc__fullscreen-inner" @click.stop>
            <button class="pc__fullscreen-close" aria-label="关闭" @click="showModModal = false">×</button>
            <p class="pc__fullscreen-text">你真是一个闲的慌的人。。。。</p>
          </div>
        </div>
      </Transition>
    </Teleport>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage } from 'zenless-ui';
import SectionHeader from './SectionHeader.vue';
import { useThemeStore } from '@/stores/themeStore';
import { useUserStore } from '@/stores/userStore';
import { gradeBadges, gradeBars, type GradeBar } from '@/data/gradeContent';
import { useAchievementStore } from '@/stores/achievementStore';

const router = useRouter();
const theme = useThemeStore();
const userStore = useUserStore();
const message = useMessage();

const emit = defineEmits<{ onOpenApi: [] }>();

// ---- 年级驱动的情绪标签 / 进度条 ----
const DEFAULT_GRADE = 1; // 游客默认展示大一文案

const activeGrade = computed(() => userStore.user?.grade ?? DEFAULT_GRADE);

const activeBadges = computed(() => gradeBadges[activeGrade.value] ?? gradeBadges[DEFAULT_GRADE]);

const activeBars = computed<GradeBar[]>(() => gradeBars[activeGrade.value] ?? gradeBars[DEFAULT_GRADE]);

// zzz 主题标签色循环
function badgeType(i: number): string | undefined {
  return ['fire', 'ice', 'ether', undefined][i % 4];
}

// ak 主题标签 class 循环
function badgeClass(i: number): string {
  return ['pc__badge--fire', 'pc__badge--ice', 'pc__badge--ether', 'pc__badge--normal'][i % 4];
}

function barToneClass(tone?: string): string {
  if (tone === 'red') return 'pc__bar-val--red';
  if (tone === 'green') return 'pc__bar-val--green';
  return '';
}

const flags = reactive({
  rail: false,
  repo: false,
  mod: false,
  rag: false,
  settings: false,
  area: false,
});

const showSettingsAlert = ref(false);

// ---- 调制模式彩蛋 ----
const modToggleCount = ref(0);
const showModModal = ref(false);
const akMsg = ref<{ visible: boolean; type: 'error' | 'warning' | 'success'; text: string }>({
  visible: false,
  type: 'success',
  text: '',
});
let akMsgTimer: ReturnType<typeof setTimeout> | null = null;

/** 日间 ak 自定义 message 浮层（3 秒后自动隐藏） */
function showAkMsg(type: 'error' | 'warning' | 'success', text: string) {
  if (akMsgTimer) clearTimeout(akMsgTimer);
  akMsg.value = { visible: true, type, text };
  akMsgTimer = setTimeout(() => {
    akMsg.value.visible = false;
  }, 3000);
}

/** 调制模式开关联动：三次打开分别触发 error → warning → success + 全屏 Modal */
function onModToggle() {
  // ZZZ 模式：v-model 已更新，如果 flags.mod 为 false 说明是关闭操作，跳过
  // AK 模式：手动设为 true 模拟打开
  if (theme.isZzz) {
    if (!flags.mod) return;
  } else {
    flags.mod = true;
  }

  modToggleCount.value++;
  const count = modToggleCount.value;

  if (count === 1) {
    // 第一次：error「请勿再次打开！」
    if (theme.isZzz) message.error('请勿再次打开！');
    else showAkMsg('error', '请勿再次打开！');
  } else if (count === 2) {
    // 第二次：warning「建议停止打开」
    if (theme.isZzz) message.warning('建议停止打开');
    else showAkMsg('warning', '建议停止打开');
  } else {
    // 第三次：success「允许开放调制模式」→ message 结束后全屏 Modal
    if (theme.isZzz) message.success('允许开放调制模式');
    else showAkMsg('success', '允许开放调制模式');
    // 成就：第三次打开调制模式（闲得慌彩蛋）
    useAchievementStore().unlock('control_you');
    setTimeout(() => {
      showModModal.value = true;
    }, 1500);
  }

  // 开关自动关闭
  setTimeout(() => {
    flags.mod = false;
  }, 200);
}

function goCalendar() {
  router.push('/calendar');
}

function goProject() {
  window.open('https://tralis2671.feishu.cn/wiki/FCATwwKbziiC7zkAL64cl3EXnCf', '_blank', 'noopener');
}

function switchIdentity() {
  userStore.logout();
  router.push('/login');
}

// 跳转类开关：跳完后 ~600ms 自动回弹关闭
function onLaunch(key: 'rail' | 'repo' | 'area', url: string) {
  flags[key] = true;
  window.open(url, '_blank', 'noopener');
  // 成就：轨道模式 / 区域探索
  if (key === 'rail') useAchievementStore().unlock('rail_mode');
  else if (key === 'area') useAchievementStore().unlock('area_explore');
  setTimeout(() => {
    flags[key] = false;
  }, 800);
}

function toggle(key: 'mod' | 'rag' | 'settings') {
  flags[key] = !flags[key];
}

// z-switch 点击直接弹窗（click 在 checkbox toggle 之前触发，flags.settings 还是旧值）
function onSettingsClick() {
  if (!flags.settings) {
    showSettingsAlert.value = true;
  }
}

function closeAlert() {
  showSettingsAlert.value = false;
  flags.settings = false;
}
</script>

<style scoped>
.pc {
  padding: 80px 32px 96px;
  max-width: 1120px;
  margin: 0 auto;
  width: 100%;
}

/* ---- 共用小标题头（// 标题 + 横线）---- */
.pc__row-head,
.pc__panel-head {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 14px;
}

.pc__row-title {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--amber);
  text-transform: uppercase;
  white-space: nowrap;
}

.pc__row-line {
  flex: 1;
  height: 1px;
  background: var(--amber);
  opacity: 0.7;
}

.pc__row {
  margin-bottom: 28px;
}

/* ---- 按钮 ---- */
.pc__btns {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

/* zenless-ui 按钮在按钮行内平铺 */
.pc__zbtn {
  flex: 1;
  min-width: 160px;
}

/* zenless-ui 进度条与原版轨道等高 */
.pc__col--bars :deep(.z-progress__track) {
  height: 10px;
}

.pc__btn {
  flex: 1;
  min-width: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 20px;
  font-size: 16px;
  font-weight: 800;
  letter-spacing: 1px;
  cursor: pointer;
  transition: transform 160ms, box-shadow 160ms;
  background: transparent;
  color: var(--text-primary);
}

.pc__btn em {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  font-style: normal;
  opacity: 0.85;
}

/* 主按钮：黄底黑字，斜切左下角 */
.pc__btn--primary {
  background: var(--amber);
  color: var(--ink);
  clip-path: polygon(0 0, 100% 0, 100% 0, 100% 100%, 18px 100%, 0 calc(100% - 18px));
}

.pc__btn--primary em { color: var(--ink); }

.pc__btn--primary:hover {
  transform: translate(-2px, -2px);
  box-shadow: 4px 4px 0 var(--neon-cyan);
}

/* 次按钮：黑底白字，灰色描边 */
.pc__btn--secondary {
  background: var(--bg-panel);
  color: var(--text-primary);
  border: 2px solid var(--border-subtle);
  clip-path: polygon(0 0, 100% 0, 100% 0, 100% 100%, 18px 100%, 0 calc(100% - 18px));
}

.pc__btn--secondary:hover {
  border-color: var(--amber);
  color: var(--amber);
}

/* 霓虹按钮：黑底青色描边 */
.pc__btn--neon {
  background: var(--bg-panel);
  color: var(--neon-cyan);
  border: 2px solid var(--neon-cyan);
  clip-path: polygon(0 0, 100% 0, 100% 0, 100% 100%, 18px 100%, 0 calc(100% - 18px));
}

.pc__btn--neon em { color: var(--neon-cyan); }

.pc__btn--neon:hover {
  background: var(--neon-cyan);
  color: var(--ink);
  box-shadow: 0 0 18px var(--neon-cyan-glow);
}

.pc__btn--neon:hover em { color: var(--ink); }

/* ---- 标签（badge，斜切角）---- */
.pc__badges {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.pc__badge {
  display: inline-flex;
  align-items: baseline;
  gap: 8px;
  padding: 7px 14px;
  font-size: 14px;
  font-weight: 700;
  clip-path: polygon(0 0, 100% 0, 100% 0, 100% 100%, 12px 100%, 0 calc(100% - 12px));
  color: var(--ink);
}

.pc__badge em {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  font-style: normal;
}

.pc__badge--fire { background: var(--amber); }
.pc__badge--ice { background: var(--neon-cyan); }
.pc__badge--ether { background: var(--neon-magenta); color: var(--text-primary); }
.pc__badge--ether em { color: var(--text-primary); }
.pc__badge--normal { background: var(--bg-panel-3); color: var(--text-secondary); }
.pc__badge--normal em { color: var(--text-muted); }

/* ---- 面板 ---- */
.pc__panel {
  background: var(--bg-panel-2);
  border: 1px solid var(--border-subtle);
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
  padding: 24px;
}

.pc__panel-head {
  margin-bottom: 22px;
}

.pc__grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr 1fr;
  gap: 18px;
}

/* ---- 开关（电池感斜切角）---- */
.pc__col {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pc__switch {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  clip-path: polygon(0 0, 100% 0, 100% 0, 100% 100%, 12px 100%, 0 calc(100% - 12px));
}

.pc__switch-label {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 600;
}

.pc__toggle {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 64px;
  height: 28px;
  padding: 0 6px;
  background: var(--bg-panel-3);
  border: 2px solid var(--amber);
  cursor: pointer;
  flex-shrink: 0;
  clip-path: polygon(0 0, 100% 0, 100% 0, 100% 100%, 10px 100%, 0 calc(100% - 10px));
  transition: background 200ms;
}

.pc__toggle-thumb {
  position: absolute;
  top: 50%;
  left: 4px;
  width: 16px;
  height: 16px;
  background: var(--amber);
  transform: translateY(-50%);
  transition: left 220ms, background 220ms;
  clip-path: polygon(0 0, 100% 0, 100% 0, 100% 100%, 4px 100%, 0 calc(100% - 4px));
}

.pc__toggle-text {
  position: relative;
  z-index: 1;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--text-muted);
  margin-left: auto;
}

.pc__toggle--on {
  background: var(--amber);
}

.pc__toggle--on .pc__toggle-thumb {
  left: calc(100% - 20px);
  background: var(--ink);
}

.pc__toggle--on .pc__toggle-text {
  color: var(--ink);
  margin-left: 0;
  margin-right: auto;
}

.pc__toggle--locked {
  cursor: not-allowed;
  opacity: 0.9;
}

/* ---- 进度条（中列）---- */
.pc__col--bars {
  background: var(--bg-panel);
  padding: 20px;
  border: 1px solid var(--border-subtle);
  clip-path: polygon(var(--cut-sm) 0, 100% 0, 100% calc(100% - var(--cut-sm)), calc(100% - var(--cut-sm)) 100%, 0 100%, 0 var(--cut-sm));
  gap: 18px;
  justify-content: center;
}

.pc__bar {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pc__bar-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.pc__bar-label {
  font-family: var(--font-mono);
  font-size: 13px;
  letter-spacing: 1px;
  color: var(--text-secondary);
}

.pc__bar-val {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 900;
  color: var(--amber);
}

.pc__bar-val--red { color: var(--neon-magenta); }
.pc__bar-val--green { color: var(--success); }

.pc__bar-track {
  height: 10px;
  background: var(--bg-panel-3);
  clip-path: polygon(var(--cut-sm) 0, 100% 0, 100% calc(100% - var(--cut-sm)), calc(100% - var(--cut-sm)) 100%, 0 100%, 0 var(--cut-sm));
  position: relative;
  overflow: hidden;
}

.pc__bar-fill {
  width: var(--w, 0%);
  height: 100%;
  background: linear-gradient(90deg, var(--amber), var(--neon-cyan));
  transition: width 300ms;
}

.pc__bar-fill--red {
  background: linear-gradient(90deg, var(--neon-cyan), var(--neon-magenta));
}

.pc__bar-fill--green {
  background: linear-gradient(90deg, var(--amber), var(--success));
}

/* ---- 弹窗 ---- */
/* z-modal 内容排版 */
.pc__alert-line {
  margin: 0;
  font-size: 14px;
  color: var(--text-primary);
  text-align: center;
  letter-spacing: 0.5px;
}
.pc__alert-line--dim {
  font-size: 12px;
  color: var(--text-muted);
}

.pc__alert-mask {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.pc__alert {
  position: relative;
  width: 320px;
  padding: 28px 32px;
  background: var(--bg-panel-2);
  border: 2px solid var(--amber);
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
  font-size: 15px;
  color: var(--text-primary);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.pc__alert p {
  letter-spacing: 0.5px;
}

.pc__alert-close {
  position: absolute;
  top: 8px;
  right: 12px;
  font-size: 22px;
  line-height: 1;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px 8px;
  background: transparent;
  transition: color 160ms;
}

.pc__alert-close:hover {
  color: var(--amber);
}

.pc__alert-title {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  color: var(--amber);
  letter-spacing: 2px;
}

.pc__alert-sub {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 6px;
}

.pc__alert kbd {
  display: inline-block;
  padding: 2px 8px;
  background: var(--bg-panel-3);
  border: 1px solid var(--border-subtle);
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--amber);
  margin: 0 2px;
}

.pc__modal-mask {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.pc__modal {
  position: relative;
  width: 360px;
  padding: 32px 36px;
  background: var(--bg-panel-2);
  border: 2px solid var(--amber);
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
  font-size: 14px;
  color: var(--text-primary);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* ---- 响应式 ---- */
@media (max-width: 900px) {
  .pc__grid {
    grid-template-columns: 1fr;
  }
}

/* ============================================
   放大 Message（ZZZ + AK 双端）
   ============================================ */
/* 夜间 zzz：全局放大 z-message */
:deep(.z-message) {
  font-size: 18px !important;
  padding: 16px 32px !important;
  min-width: 280px;
  text-align: center;
  font-weight: 700;
}

/* ============================================
   z-modal 内文字排版
   ============================================ */
.pc__modal-text {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  text-align: center;
  letter-spacing: 1px;
  padding: 16px 0;
}

/* ============================================
   日间 ak 自定义 message 浮层
   ============================================ */
.pc__msg {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10001;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 32px;
  background: var(--bg-panel-2);
  border: 2px solid var(--amber);
  clip-path: polygon(var(--cut-sm) 0, 100% 0, 100% calc(100% - var(--cut-sm)), calc(100% - var(--cut-sm)) 100%, 0 100%, 0 var(--cut-sm));
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  min-width: 280px;
  justify-content: center;
}

.pc__msg-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  font-family: var(--font-mono);
  font-size: 18px;
  font-weight: 900;
  clip-path: var(--clip-sm);
  flex-shrink: 0;
}

.pc__msg-text {
  letter-spacing: 0.5px;
}

.pc__msg--error {
  border-color: var(--neon-magenta);
  color: var(--neon-magenta);
}
.pc__msg--error .pc__msg-icon {
  background: var(--neon-magenta);
  color: var(--text-primary);
}

.pc__msg--warning {
  border-color: var(--warning);
  color: var(--warning);
}
.pc__msg--warning .pc__msg-icon {
  background: var(--warning);
  color: var(--ink);
}

.pc__msg--success {
  border-color: var(--success);
  color: var(--success);
}
.pc__msg--success .pc__msg-icon {
  background: var(--success);
  color: var(--ink);
}

/* message 进入/离开动画 */
.pc-msg-enter-active,
.pc-msg-leave-active {
  transition: opacity 300ms, transform 300ms;
}
.pc-msg-enter-from,
.pc-msg-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-12px);
}

/* ============================================
   全屏 Modal（调制模式第三次触发）
   ============================================ */
.pc__fullscreen {
  position: fixed;
  inset: 0;
  z-index: 10002;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.88);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.pc__fullscreen-inner {
  position: relative;
  padding: 80px 60px;
  text-align: center;
}

.pc__fullscreen-text {
  margin: 0;
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 700;
  letter-spacing: 3px;
  color: var(--amber);
  text-shadow: 0 0 30px var(--amber-glow);
}

.pc__fullscreen-close {
  position: absolute;
  top: -40px;
  right: -20px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  line-height: 1;
  color: var(--text-muted);
  background: transparent;
  cursor: pointer;
  transition: color 200ms;
}

.pc__fullscreen-close:hover {
  color: var(--amber);
}

/* 全屏 Modal 动画 */
.pc-modal-enter-active,
.pc-modal-leave-active {
  transition: opacity 400ms;
}
.pc-modal-enter-active .pc__fullscreen-inner,
.pc-modal-leave-active .pc__fullscreen-inner {
  transition: transform 400ms cubic-bezier(0.34, 1.56, 0.64, 1), opacity 400ms;
}
.pc-modal-enter-from,
.pc-modal-leave-to {
  opacity: 0;
}
.pc-modal-enter-from .pc__fullscreen-inner,
.pc-modal-leave-to .pc__fullscreen-inner {
  transform: scale(0.8);
  opacity: 0;
}

@media (max-width: 767px) {
  .pc__fullscreen-text {
    font-size: 24px;
    letter-spacing: 1px;
  }
  .pc__fullscreen-inner {
    padding: 60px 24px;
  }
}

@media (max-width: 767px) {
  .pc {
    padding: 0 16px 64px;
  }

  .pc__panel {
    padding: 18px;
  }

  .pc__btn {
    min-width: 0;
    font-size: 14px;
    padding: 12px 14px;
  }

  .pc__badge {
    font-size: 12px;
    padding: 6px 10px;
  }

  .pc__badge em {
    font-size: 9px;
  }
}
</style>