<template>
  <section class="ai-section">
    <SectionHeader num="02" title="智能助手" en="AI ASSISTANT" />

    <!-- 票据式 AI 邀请（整张票据可点击） -->
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
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useNavStore } from '@/stores/navStore';
import SectionHeader from './SectionHeader.vue';

const router = useRouter();
const nav = useNavStore();

function startChat() {
  router.push(nav.chatRoute || '/chat');
}
</script>

<style scoped>
.ai-section {
  padding: 80px 32px;
  max-width: 1120px;
  margin: 0 auto;
  width: 100%;
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
  font-size: 12px;
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
  font-size: 21px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.ticket__options {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 14.5px;
  color: var(--text-secondary);
}

.ticket__options span:nth-child(1) { color: var(--amber); }
.ticket__options span:nth-child(2) { color: var(--neon-magenta); }
.ticket__options span:nth-child(3) { color: var(--neon-cyan); }

.ticket__cta {
  align-self: flex-end;
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 900;
  letter-spacing: 2px;
  color: var(--amber);
}

.ticket:hover .ticket__cta {
  transform: translateX(3px);
}

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
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 3px;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  white-space: nowrap;
}

/* ---- 响应式 ---- */
@media (max-width: 767px) {
  .ai-section {
    padding: 48px 16px;
  }

  .ticket__main {
    padding: 18px 18px;
    gap: 12px;
  }

  .ticket__bubble {
    padding: 12px 14px;
  }

  .ticket__greet {
    font-size: 17px;
  }

  .ticket__stub {
    width: 56px;
    padding: 18px 8px;
  }

  .ticket__cta {
    align-self: stretch;
    text-align: center;
  }
}
</style>
