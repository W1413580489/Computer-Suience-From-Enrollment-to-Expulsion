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
        <button class="pc__btn pc__btn--primary" @click="goCalendar">校历 <em>CALENDAR</em></button>
        <button class="pc__btn pc__btn--secondary" @click="goProject">项目 <em>PROJECT</em></button>
        <button class="pc__btn pc__btn--neon" @click="emit('onOpenApi')">设置 <em>SETTINGS</em></button>
      </div>
    </div>

    <!-- 标签行 -->
    <div class="pc__row">
      <div class="pc__row-head">
        <span class="pc__row-title">// BADGES / 情绪标签</span>
        <span class="pc__row-line" />
      </div>
      <div class="pc__badges">
        <span class="pc__badge pc__badge--fire">憔悴 <em>EXHAUSTED</em></span>
        <span class="pc__badge pc__badge--ice">迷茫 <em>LOST</em></span>
        <span class="pc__badge pc__badge--ether">不想学了 <em>WANT TO QUIT</em></span>
        <span class="pc__badge pc__badge--normal">求及格 <em>PASS PLEASE</em></span>
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
            <button class="pc__toggle pc__toggle--on pc__toggle--locked" disabled aria-label="登录（始终开启）">
              <span class="pc__toggle-thumb" />
              <span class="pc__toggle-text">ON</span>
            </button>
          </div>
          <div class="pc__switch">
            <span class="pc__switch-label">轨道模式</span>
            <button
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
            <button
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
          <div class="pc__bar">
            <div class="pc__bar-head">
              <span class="pc__bar-label">Patience</span>
              <span class="pc__bar-val">25%</span>
            </div>
            <div class="pc__bar-track">
              <div class="pc__bar-fill" :style="{ '--w': '25%' }" />
            </div>
          </div>
          <div class="pc__bar">
            <div class="pc__bar-head">
              <span class="pc__bar-label">Accuracy</span>
              <span class="pc__bar-val pc__bar-val--red">2%</span>
            </div>
            <div class="pc__bar-track">
              <div class="pc__bar-fill pc__bar-fill--red" :style="{ '--w': '2%' }" />
            </div>
          </div>
          <div class="pc__bar">
            <div class="pc__bar-head">
              <span class="pc__bar-label">Authenticity</span>
              <span class="pc__bar-val pc__bar-val--green">92%</span>
            </div>
            <div class="pc__bar-track">
              <div class="pc__bar-fill pc__bar-fill--green" :style="{ '--w': '92%' }" />
            </div>
          </div>
        </div>

        <!-- 右开关 4 项 -->
        <div class="pc__col">
          <div class="pc__switch">
            <span class="pc__switch-label">调制模式</span>
            <button
              class="pc__toggle"
              :class="{ 'pc__toggle--on': flags.mod }"
              @click="toggle('mod')"
            >
              <span class="pc__toggle-thumb" />
              <span class="pc__toggle-text">{{ flags.mod ? 'ON' : 'OFF' }}</span>
            </button>
          </div>
          <div class="pc__switch">
            <span class="pc__switch-label">知识检索RAG</span>
            <button
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
            <button
              ref="settingsBtn"
              class="pc__toggle"
              :class="{ 'pc__toggle--on': flags.settings }"
              @click="toggle('settings')"
            >
              <span class="pc__toggle-thumb" />
              <span class="pc__toggle-text">{{ flags.settings ? 'ON' : 'OFF' }}</span>
            </button>
            <Teleport to="body">
              <div v-if="showSettingsAlert" class="pc__alert-mask" @click.self="closeAlert">
                <div class="pc__alert" role="dialog" aria-modal="true">
                  <button class="pc__alert-close" aria-label="关闭" @click="closeAlert">×</button>
                  <p>你想设置什么？</p>
                  <p>你想设置什么！</p>
                  <p>想要就找我发源代码</p>
                </div>
              </div>
            </Teleport>
          </div>
          <div class="pc__switch">
            <span class="pc__switch-label">区域探索</span>
            <button
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
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import SectionHeader from './SectionHeader.vue';

const router = useRouter();

const emit = defineEmits<{ onOpenApi: [] }>();

const flags = reactive({
  rail: false,
  repo: false,
  mod: false,
  rag: false,
  settings: false,
  area: false,
});

const showSettingsAlert = ref(false);

function goCalendar() {
  router.push('/calendar');
}

function goProject() {
  window.open('https://tralis2671.feishu.cn/wiki/FCATwwKbziiC7zkAL64cl3EXnCf', '_blank', 'noopener');
}

// 跳转类开关：跳完后 ~600ms 自动回弹关闭
function onLaunch(key: 'rail' | 'repo' | 'area', url: string) {
  flags[key] = true;
  window.open(url, '_blank', 'noopener');
  setTimeout(() => {
    flags[key] = false;
  }, 800);
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