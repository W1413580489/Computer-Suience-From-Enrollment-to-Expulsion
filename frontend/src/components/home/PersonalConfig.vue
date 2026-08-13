<template>
  <section class="pc">
    <SectionHeader num="04" title="个人配置" en="PERSONAL CONFIG" />

    <!-- 按钮行 -->
    <div class="pc__row pc__row--btns">
      <button class="pc__btn" @click="goCalendar">校历</button>
      <button class="pc__btn" @click="goProject">项目</button>
      <button class="pc__btn" @click="openDevtools">设置</button>
    </div>

    <!-- 标签行（情绪状态） -->
    <div class="pc__row pc__row--tags">
      <span class="pc__tag">憔悴 <em>EXHAUSTED</em></span>
      <span class="pc__tag">迷茫 <em>LOST</em></span>
      <span class="pc__tag">不想学了 <em>WANT TO QUIT</em></span>
      <span class="pc__tag">求及格 <em>PASS PLEASE</em></span>
    </div>

    <!-- 主面板：左开关 / 中进度条 / 右开关 -->
    <div class="pc__panel">
      <!-- 左开关 3 项 -->
      <div class="pc__col">
        <div class="pc__row-item">
          <span class="pc__label">登录</span>
          <button class="pc__toggle pc__toggle--on pc__toggle--locked" disabled aria-label="登录（始终开启）">
            <span class="pc__toggle-thumb" />
          </button>
        </div>
        <div class="pc__row-item">
          <span class="pc__label">轨道模式</span>
          <button class="pc__toggle" :class="{ 'pc__toggle--on': flags.rail }" @click="goStarRail">
            <span class="pc__toggle-thumb" />
          </button>
        </div>
        <div class="pc__row-item">
          <span class="pc__label">项目仓库</span>
          <button class="pc__toggle" :class="{ 'pc__toggle--on': flags.repo }" @click="goGithub">
            <span class="pc__toggle-thumb" />
          </button>
        </div>
      </div>

      <!-- 中进度条 3 项 -->
      <div class="pc__col pc__col--bars">
        <div class="pc__bar">
          <div class="pc__bar-head">
            <span class="pc__bar-label">Patience</span>
            <span class="pc__bar-val">25%</span>
          </div>
          <div class="pc__bar-track"><div class="pc__bar-fill" style="width: 25%" /></div>
        </div>
        <div class="pc__bar">
          <div class="pc__bar-head">
            <span class="pc__bar-label">Accuracy</span>
            <span class="pc__bar-val">2%</span>
          </div>
          <div class="pc__bar-track"><div class="pc__bar-fill pc__bar-fill--red" style="width: 2%" /></div>
        </div>
        <div class="pc__bar">
          <div class="pc__bar-head">
            <span class="pc__bar-label">Authenticity</span>
            <span class="pc__bar-val">92%</span>
          </div>
          <div class="pc__bar-track"><div class="pc__bar-fill pc__bar-fill--green" style="width: 92%" /></div>
        </div>
      </div>

      <!-- 右开关 4 项 -->
      <div class="pc__col">
        <div class="pc__row-item">
          <span class="pc__label">调制模式</span>
          <button class="pc__toggle" :class="{ 'pc__toggle--on': flags.mod }" @click="toggle('mod')">
            <span class="pc__toggle-thumb" />
          </button>
        </div>
        <div class="pc__row-item">
          <span class="pc__label">知识检索RAG</span>
          <button class="pc__toggle" :class="{ 'pc__toggle--on': flags.rag }" @click="toggle('rag')">
            <span class="pc__toggle-thumb" />
          </button>
        </div>
        <div class="pc__row-item">
          <span class="pc__label">网站设置</span>
          <button class="pc__toggle" :class="{ 'pc__toggle--on': flags.settings }" @click="toggle('settings')">
            <span class="pc__toggle-thumb" />
          </button>
        </div>
        <div class="pc__row-item">
          <span class="pc__label">区域探索</span>
          <button class="pc__toggle pc__toggle--locked-off" disabled aria-label="区域探索（始终关闭）">
            <span class="pc__toggle-thumb" />
          </button>
        </div>
      </div>
    </div>

    <!-- 网站设置弹窗 -->
    <div v-if="showSettingsAlert" class="pc__alert-mask" @click.self="closeAlert">
      <div class="pc__alert">
        <button class="pc__alert-close" aria-label="关闭" @click="closeAlert">×</button>
        <p>你想设置什么？</p>
        <p>你想设置什么！</p>
        <p>想要就找我发源代码</p>
      </div>
    </div>

    <!-- 打开 F12 提示弹窗（设置按钮） -->
    <div v-if="showDevtools" class="pc__alert-mask" @click.self="showDevtools = false">
      <div class="pc__alert pc__alert--code">
        <button class="pc__alert-close" aria-label="关闭" @click="showDevtools = false">×</button>
        <p class="pc__alert-title">// DEVTOOLS</p>
        <p>按 <kbd>F12</kbd> 或 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>I</kbd> 打开浏览器开发者工具</p>
        <p class="pc__alert-sub">本站点无法通过 JS 直接唤起 DevTools（浏览器安全策略）</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import SectionHeader from './SectionHeader.vue';

const router = useRouter();

const flags = reactive({
  rail: false,
  repo: false,
  mod: false,
  rag: false,
  settings: false,
});

const showSettingsAlert = ref(false);
const showDevtools = ref(false);

function goCalendar() {
  router.push('/calendar');
}

function goProject() {
  // 「邪修学习指南」飞书篇章占位 URL：先打开知识库首页
  window.open('https://tralis2671.feishu.cn/wiki/VvKVwsHo2iIIC4ko0PmcKs4lnKd', '_blank', 'noopener');
}

function goStarRail() {
  flags.rail = !flags.rail;
  window.open('https://sr.mihoyo.com/', '_blank', 'noopener');
}

function goGithub() {
  flags.repo = !flags.repo;
  window.open('https://github.com/', '_blank', 'noopener');
}

function openDevtools() {
  showDevtools.value = true;
}

function toggle(key: 'mod' | 'rag' | 'settings') {
  flags[key] = !flags[key];
  if (key === 'settings' && flags.settings) {
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
  padding: 0 32px 96px;
  max-width: 1120px;
  margin: 0 auto;
  width: 100%;
}

/* ---- 按钮行 ---- */
.pc__row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.pc__btn {
  flex: 1;
  min-width: 120px;
  padding: 14px 24px;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
  background: transparent;
  color: var(--text-primary);
  border: 2px solid var(--border-subtle);
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
  cursor: pointer;
  transition: border-color 160ms, color 160ms, background 160ms;
}

.pc__btn:hover {
  border-color: var(--amber);
  color: var(--amber);
  background: var(--amber-soft);
}

/* ---- 标签行（情绪） ---- */
.pc__row--tags {
  margin-bottom: 22px;
}

.pc__tag {
  display: inline-flex;
  align-items: baseline;
  gap: 8px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  background: var(--bg-panel-2);
  border: 1px solid var(--border-subtle);
  clip-path: polygon(var(--cut-sm) 0, 100% 0, 100% calc(100% - var(--cut-sm)), calc(100% - var(--cut-sm)) 100%, 0 100%, 0 var(--cut-sm));
}

.pc__tag em {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--amber);
  font-style: normal;
}

/* ---- 主面板 ---- */
.pc__panel {
  display: grid;
  grid-template-columns: 1fr 1.2fr 1fr;
  gap: 18px;
  background: var(--bg-panel-2);
  border: 1px solid var(--border-subtle);
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
  padding: 24px;
}

.pc__col {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.pc__row-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed var(--border-subtle);
}

.pc__col > .pc__row-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.pc__label {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 600;
}

/* ---- 开关（参考 zzz-toggle） ---- */
.pc__toggle {
  position: relative;
  width: 52px;
  height: 26px;
  flex-shrink: 0;
  background: var(--bg-panel-3);
  border: 2px solid var(--ink);
  cursor: pointer;
  padding: 0;
  clip-path: polygon(var(--cut-sm) 0, 100% 0, 100% calc(100% - var(--cut-sm)), calc(100% - var(--cut-sm)) 100%, 0 100%, 0 var(--cut-sm));
  transition: background 180ms;
}

.pc__toggle-thumb {
  position: absolute;
  top: 50%;
  left: 3px;
  width: 16px;
  height: 16px;
  transform: translateY(-50%);
  background: var(--text-secondary);
  transition: left 180ms, background 180ms;
}

.pc__toggle--on {
  background: var(--amber);
}

.pc__toggle--on .pc__toggle-thumb {
  left: calc(100% - 19px);
  background: var(--ink);
}

.pc__toggle--locked,
.pc__toggle--locked-off {
  cursor: not-allowed;
  opacity: 0.75;
}

.pc__toggle--locked-off .pc__toggle-thumb {
  left: 3px;
}

/* ---- 进度条（中列） ---- */
.pc__col--bars {
  background: var(--bg-panel);
  padding: 20px;
  border: 1px solid var(--border-subtle);
  clip-path: polygon(var(--cut-sm) 0, 100% 0, 100% calc(100% - var(--cut-sm)), calc(100% - var(--cut-sm)) 100%, 0 100%, 0 var(--cut-sm));
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

.pc__bar-track {
  height: 8px;
  background: var(--bg-panel-3);
  clip-path: polygon(var(--cut-sm) 0, 100% 0, 100% calc(100% - var(--cut-sm)), calc(100% - var(--cut-sm)) 100%, 0 100%, 0 var(--cut-sm));
  overflow: hidden;
}

.pc__bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--amber), var(--neon-cyan));
}

.pc__bar-fill--red {
  background: var(--neon-magenta);
}

.pc__bar-fill--green {
  background: var(--success, #4ECCA3);
}

/* ---- 弹窗（遮罩 + 内容） ---- */
.pc__alert-mask {
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

.pc__alert {
  position: relative;
  max-width: 420px;
  padding: 32px 36px;
  background: var(--bg-panel-2);
  border: 2px solid var(--amber);
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
  font-size: 15px;
  color: var(--text-primary);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pc__alert p {
  letter-spacing: 1px;
}

.pc__alert-close {
  position: absolute;
  top: 10px;
  right: 14px;
  font-size: 22px;
  line-height: 1;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px 8px;
  transition: color 160ms;
}

.pc__alert-close:hover {
  color: var(--amber);
}

.pc__alert-title {
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 700;
  color: var(--amber);
  letter-spacing: 2px;
}

.pc__alert-sub {
  font-size: 12px;
  color: var(--text-muted);
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

/* ---- 响应式 ---- */
@media (max-width: 900px) {
  .pc__panel {
    grid-template-columns: 1fr;
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
    padding: 12px 18px;
  }

  .pc__tag {
    font-size: 12px;
    padding: 6px 12px;
  }

  .pc__tag em {
    font-size: 9px;
  }
}
</style>