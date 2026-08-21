// chatStore：聊天会话状态（多轮最多 6 轮 FR-QA-05、停止生成 FR-QA-07、重新生成 FR-QA-06）
import { defineStore } from 'pinia';
import { askStream, sendFeedback, sha256Short } from '@/api/client';
import { useSettingsStore } from '@/stores/settingsStore';
import { unlockAchievement } from '@/data/achievements';
import type { ChatMessage } from '@/types/nav';

const MAX_HISTORY_ROUNDS = 6;

let msgSeq = 0;
const nextId = () => `m${Date.now()}_${msgSeq++}`;

interface ChatState {
  sessionId: string;
  messages: ChatMessage[];
  sending: boolean;
  abort: AbortController | null;
}

export const useChatStore = defineStore('chat', {
  state: (): ChatState => ({
    sessionId: `s_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`,
    messages: [],
    sending: false,
    abort: null,
  }),
  getters: {
    // 最近 6 轮完整对话（user+assistant 成对），供多轮上下文
    history: (s) => {
      const completed = s.messages.filter((m) => !m.streaming && !m.error && m.content);
      return completed.slice(-MAX_HISTORY_ROUNDS * 2).map((m) => ({ role: m.role, content: m.content }));
    },
  },
  actions: {
    async ask(question: string) {
      const q = question.trim();
      if (!q || this.sending) return;

      // 成就：首次向 AI 提问（消耗 token）
      unlockAchievement('token_enough');

      this.messages.push({ id: nextId(), role: 'user', content: q });
      const assistantMsgId = nextId();
      this.messages.push({
        id: assistantMsgId,
        role: 'assistant',
        content: '',
        streaming: true,
        feedback: null,
      });
      this.sending = true;
      // 通过响应式代理修改（不能直接用 assistantMsg 原始引用，Vue 不感知）
      const getMsg = () => this.messages.find((m) => m.id === assistantMsgId);

      const settings = useSettingsStore();
      const payload = {
        question: q,
        session_id: this.sessionId,
        history: this.history,
        ...(settings.hasKey
          ? {
              api_key: settings.apiKey,
              provider: settings.provider,
              base_url: settings.effectiveBaseUrl || undefined,
              model: settings.effectiveModel || undefined,
            }
          : {}),
      };

      const qHash = await sha256Short(q);

      this.abort = askStream(payload, {
        onToken: (content) => {
          const msg = getMsg();
          if (msg) msg.content += content;
        },
        onCitations: (citations) => {
          const msg = getMsg();
          if (msg) msg.citations = citations;
        },
        onDone: () => {
          const msg = getMsg();
          if (msg) {
            msg.streaming = false;
            msg.qHash = qHash;
          }
          this.sending = false;
          this.abort = null;
        },
        onError: (code, message) => {
          const msg = getMsg();
          if (msg) {
            msg.streaming = false;
            msg.error = `${message}`;
            msg.qHash = qHash;
          }
          this.sending = false;
          this.abort = null;
        },
      });
    },
    stop() {
      // FR-QA-07：中断流式响应
      this.abort?.abort();
      this.abort = null;
      this.sending = false;
      const last = this.messages[this.messages.length - 1];
      if (last?.role === 'assistant') last.streaming = false;
    },
    regenerate() {
      // FR-QA-06：找到最后一条用户提问，删除其后的回答并重新生成
      const lastUserIdx = [...this.messages].map((m) => m.role).lastIndexOf('user');
      if (lastUserIdx < 0 || this.sending) return;
      const question = this.messages[lastUserIdx].content;
      this.messages = this.messages.slice(0, lastUserIdx);
      this.ask(question);
    },
    async feedback(msg: ChatMessage, value: 'up' | 'down', reason?: string) {
      if (!msg.qHash) return false;
      const ok = await sendFeedback({
        q_hash: msg.qHash,
        feedback: value,
        reason,
        session_id: this.sessionId,
      });
      if (ok) msg.feedback = value;
      return ok;
    },
    clear() {
      this.stop();
      this.messages = [];
      this.sessionId = `s_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
    },
  },
});
