<template>
  <section class="ai-invite">
    <!-- ===== 票据式 AI 邀请（整张票据可点击） ===== -->
    <button class="ticket" @click="startChat" aria-label="进入智能助手">
      <!-- 主体 -->
      <div class="ticket__main">
        <div class="ticket__status">
          <span class="ticket__dot" />
          <span class="ticket__label">AI ASSISTANT</span>
        </div>
        <div class="ticket__bubble">
          <p class="ticket__greet">今天想了解什么？</p>
          <p class="ticket__options">
            <span>选课？</span>
            <span>保研？</span>
            <span>还是校园生活？</span>
          </p>
        </div>
        <span class="ticket__cta">START CHAT →</span>
      </div>
      <!-- 票根 -->
      <div class="ticket__stub">
        <span class="ticket__stub-label">ADMIT ONE · 智能助手</span>
      </div>
    </button>

    <!-- ===== 数据面板 ===== -->
    <div class="stats">
      <!-- 左：网站完成度 -->
      <div class="stat">
        <div class="stat__value">87%</div>
        <div class="stat__label">SITE COMPLETION</div>
        <div class="stat__bar"><div class="stat__fill" /></div>
      </div>

      <!-- 中：最新更新时间 -->
      <div class="stat stat--center">
        <div class="stat__value stat__value--date">{{ updatedAt }}</div>
        <div class="stat__label">LAST UPDATE</div>
        <div class="stat__sub">网站最新更新时间</div>
      </div>

      <!-- 右：致谢名单（逐个放映） -->
      <div class="stat stat--credits">
        <div class="stat__label stat__label--credits">CREDITS · 致谢名单</div>
        <div class="credits">
          <ul class="credits__list">
            <li v-for="(name, i) in credits" :key="i">{{ name }}</li>
            <li v-for="(name, i) in credits" :key="'dup-' + i" aria-hidden="true">{{ name }}</li>
          </ul>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useNavStore } from '@/stores/navStore';

const router = useRouter();
const nav = useNavStore();

function startChat() {
  router.push(nav.chatRoute || '/chat');
}

// 最新更新时间：取自 changelog 最新版本日期，无则回退
const updatedAt = computed(() => nav.changelog[0]?.date ?? '2026-08-13');

// 致谢名单
const credits = [
  '王叔',
  '高书记',
  '林家络',
  '大暨王朝1566',
  '鸟破苍穹',
  'Ssr老板',
  '研究生牢唐',
  '小孩',
  '扩列与点赞之神',
  '不知名的好心人',
  '深圳科创学院',
  'QQ',
  '少女暴君',
  '沪上哈基',
  '谢总',
  '乔伊皇',
  '木宁习习',
  '北极熊女王',
  '小企鹅',
  '锦瑟无端五十弦',
  '社恐哥',
  '米居',
  '网安梵某学长',
];
</script>

<style scoped>
.ai-invite {
  padding: 8px 32px 40px;
  max-width: 1120px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

/* ===== 票据 ===== */
.ticket {
  position: relative;
  display: flex;
  width: 100%;
  background: var(--bg-panel-2);
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
  overflow: hidden;
  cursor: pointer;
  text-align: left;
  border: 1px solid rgba(255, 217, 61, 0.16);
  transition: transform 180ms, border-color 180ms, box-shadow 180ms;
}

.ticket:hover {
  transform: translateY(-3px);
  border-color: var(--amber);
  box-shadow: 0 8px 32px rgba(255, 217, 61, 0.14);
}

.ticket:active {
  transform: translateY(0);
}

/* 主体 */
.ticket__main {
  flex: 1;
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-width: 0;
}

.ticket__status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ticket__dot {
  width: 8px;
  height: 8px;
  background: var(--neon-cyan);
  border-radius: 50%;
  animation: ai-blink 2s infinite;
}

@keyframes ai-blink {
  0%, 100% { opacity: 1; box-shadow: 0 0 6px var(--neon-cyan); }
  50% { opacity: 0.4; box-shadow: 0 0 3px var(--neon-cyan); }
}

.ticket__label {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 3px;
  color: var(--neon-cyan);
  text-transform: uppercase;
}

.ticket__bubble {
  padding: 14px 18px;
  background: var(--bg-panel-3);
  clip-path: polygon(0 0, 100% 0, 100% 100%, 14px 100%, 0 calc(100% - 14px));
}

.ticket__greet {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.ticket__options {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 13px;
  color: var(--text-secondary);
}

.ticket__options span:nth-child(1) { color: var(--amber); }
.ticket__options span:nth-child(2) { color: var(--neon-magenta); }
.ticket__options span:nth-child(3) { color: var(--neon-cyan); }

.ticket__cta {
  align-self: flex-end;
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 2px;
  color: var(--amber);
}

.ticket:hover .ticket__cta {
  transform: translateX(3px);
}

/* 票根（虚线分隔 + 竖排文字） */
.ticket__stub {
  width: 88px;
  flex-shrink: 0;
  padding: 24px 12px;
  background: var(--bg-panel);
  border-left: 2px dashed var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: center;
}

.ticket__stub-label {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 3px;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  white-space: nowrap;
}

/* ===== 数据面板 ===== */
.stats {
  display: grid;
  grid-template-columns: 1fr 1fr 1.4fr;
  gap: 14px;
}

.stat {
  position: relative;
  background: var(--bg-panel-2);
  padding: 18px 20px;
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
  border-bottom: 2px solid var(--amber);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat--center {
  align-items: center;
  justify-content: center;
  text-align: center;
}

.stat__value {
  font-family: var(--font-display);
  font-size: 34px;
  font-weight: 900;
  line-height: 1;
  color: var(--amber);
}

.stat__value--date {
  font-family: var(--font-mono);
  font-size: 20px;
  letter-spacing: 1px;
}

.stat__label {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.stat__sub {
  font-size: 11px;
  color: var(--text-muted);
}

.stat__bar {
  margin-top: 8px;
  width: 100%;
  height: 8px;
  background: var(--bg-panel-3);
  clip-path: polygon(var(--cut-sm) 0, 100% 0, 100% calc(100% - var(--cut-sm)), calc(100% - var(--cut-sm)) 100%, 0 100%, 0 var(--cut-sm));
  overflow: hidden;
}

.stat__fill {
  width: 87%;
  height: 100%;
  background: linear-gradient(90deg, var(--amber), var(--neon-cyan));
}

/* 致谢名单滚动 */
.stat--credits {
  border-bottom-color: var(--neon-cyan);
}

.stat__label--credits {
  color: var(--neon-cyan);
}

.credits {
  margin-top: 4px;
  height: 56px;
  overflow: hidden;
  position: relative;
  -webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 16%, black 84%, transparent 100%);
  mask-image: linear-gradient(to bottom, transparent 0%, black 16%, black 84%, transparent 100%);
}

.credits__list {
  list-style: none;
  margin: 0;
  padding: 0;
  animation: credits-scroll 30s linear infinite;
}

.credits__list li {
  font-size: 12px;
  line-height: 28px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@keyframes credits-scroll {
  0% { transform: translateY(0); }
  100% { transform: translateY(-50%); }
}

.credits:hover .credits__list {
  animation-play-state: paused;
}

/* ---- 响应式 ---- */
@media (max-width: 767px) {
  .ai-invite {
    padding: 8px 16px 28px;
    gap: 12px;
  }

  .ticket__main {
    padding: 18px 18px;
    gap: 12px;
  }

  .ticket__bubble {
    padding: 12px 14px;
  }

  .ticket__greet {
    font-size: 16px;
  }

  .ticket__stub {
    width: 56px;
    padding: 18px 8px;
  }

  .ticket__cta {
    align-self: stretch;
    text-align: center;
  }

  .stats {
    grid-template-columns: 1fr;
  }
}
</style>
