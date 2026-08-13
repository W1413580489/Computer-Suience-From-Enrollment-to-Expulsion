<template>
  <section class="ai-invite">
    <div class="ai-invite__inner">
      <!-- 状态标识 -->
      <div class="ai-invite__status">
        <span class="ai-invite__dot" />
        <span class="ai-invite__label">AI ASSISTANT</span>
      </div>

      <!-- 对话气泡邀请 -->
      <div class="ai-invite__bubble">
        <p class="ai-invite__greet">今天想了解什么？</p>
        <p class="ai-invite__options">
          <span>选课？</span>
          <span>保研？</span>
          <span>还是校园生活？</span>
        </p>
      </div>

      <!-- 启动按钮 -->
      <button class="ai-invite__cta" @click="startChat">
        <span>START CHAT</span>
        <span class="ai-invite__arrow">→</span>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useNavStore } from '@/stores/navStore';

const router = useRouter();
const nav = useNavStore();

function startChat() {
  router.push(nav.chatRoute || '/chat');
}
</script>

<style scoped>
.ai-invite {
  padding: 24px 24px 32px;
  max-width: 720px;
  margin: 0 auto;
  width: 100%;
}

.ai-invite__inner {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 18px;
  padding: 28px 32px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-left: 3px solid var(--neon-cyan);
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%);
}

/* ---- 状态标识 ---- */
.ai-invite__status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-invite__dot {
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

.ai-invite__label {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 3px;
  color: var(--neon-cyan);
  text-transform: uppercase;
}

/* ---- 对话气泡 ---- */
.ai-invite__bubble {
  position: relative;
  padding: 14px 18px;
  background: var(--bg-panel-2);
  clip-path: polygon(0 0, 100% 0, 100% 100%, 14px 100%, 0 calc(100% - 14px));
}

.ai-invite__greet {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.ai-invite__options {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 13px;
  color: var(--text-secondary);
}

.ai-invite__options span:nth-child(1) { color: var(--amber); }
.ai-invite__options span:nth-child(2) { color: var(--neon-magenta); }
.ai-invite__options span:nth-child(3) { color: var(--neon-cyan); }

/* ---- 启动按钮 ---- */
.ai-invite__cta {
  align-self: flex-end;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 28px;
  background: var(--amber);
  color: var(--on-amber);
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 2px;
  clip-path: polygon(var(--cut-sm) 0, 100% 0, 100% calc(100% - var(--cut-sm)), calc(100% - var(--cut-sm)) 100%, 0 100%, 0 var(--cut-sm));
  transition: transform 150ms, box-shadow 150ms;
}

.ai-invite__cta:hover {
  transform: translate(2px, -2px);
  box-shadow: -4px 4px 0 var(--neon-cyan);
}

.ai-invite__cta:active {
  transform: translate(0, 0);
  box-shadow: none;
}

.ai-invite__arrow {
  transition: transform 150ms;
}

.ai-invite__cta:hover .ai-invite__arrow {
  transform: translateX(3px);
}

/* ---- 响应式 ---- */
@media (max-width: 767px) {
  .ai-invite {
    padding: 16px 16px 24px;
  }

  .ai-invite__inner {
    padding: 20px 22px;
    gap: 14px;
  }

  .ai-invite__bubble {
    padding: 12px 14px;
  }

  .ai-invite__greet {
    font-size: 16px;
  }

  .ai-invite__options {
    font-size: 12px;
    gap: 10px;
  }

  .ai-invite__cta {
    align-self: stretch;
    justify-content: center;
    padding: 11px 22px;
  }
}
</style>
