// API 客户端：SSE 流式提问、Key 验证、反馈、高频问题
import type { Citation } from '@/types/nav';

export interface AskPayload {
  question: string;
  session_id?: string;
  history?: { role: string; content: string }[];
  api_key?: string;
  provider?: string;
  base_url?: string;
  model?: string;
}

export interface AskCallbacks {
  onStart?: () => void;
  onToken?: (content: string) => void;
  onCitations?: (citations: Citation[]) => void;
  onDone?: (usage: { tokens_in: number; tokens_out: number }) => void;
  onError?: (code: string, message: string) => void;
}

async function sha256Short(text: string): Promise<string> {
  const normalized = text.trim().toLowerCase();
  // 非安全上下文（http://IP:port）下 crypto.subtle 不可用，降级为 FNV-1a 哈希
  try {
    if (crypto?.subtle) {
      const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(normalized));
      return Array.from(new Uint8Array(buf))
        .map((b) => b.toString(16).padStart(2, '0'))
        .join('')
        .slice(0, 16);
    }
  } catch {
    /* 降级走 FNV-1a */
  }
  // FNV-1a 32-bit，均匀且快速，足以作为会话内反馈标识
  let h = 0x811c9dc5;
  for (let i = 0; i < normalized.length; i++) {
    h ^= normalized.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return (h >>> 0).toString(16).padStart(8, '0');
}

export { sha256Short };

/**
 * POST /api/ask —— SSE 流式（FR-QA-01）。
 * 返回 AbortController 以支持「停止生成」（FR-QA-07）。
 */
export function askStream(payload: AskPayload, cb: AskCallbacks): AbortController {
  const controller = new AbortController();

  (async () => {
    let resp: Response;
    try {
      resp = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });
    } catch (e) {
      if ((e as Error).name !== 'AbortError') {
        cb.onError?.('NETWORK', '网络连接失败，请检查网络后重试');
      }
      return;
    }

    // HTTP 级错误（限流 / 平台未配置 Key / 参数错误）
    if (!resp.ok || !resp.body) {
      try {
        const data = await resp.json();
        cb.onError?.(data?.error?.code ?? `HTTP_${resp.status}`, data?.error?.message ?? `请求失败（HTTP ${resp.status}）`);
      } catch {
        cb.onError?.(`HTTP_${resp.status}`, `请求失败（HTTP ${resp.status}）`);
      }
      return;
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        buffer = events.pop() ?? '';
        for (const evt of events) {
          const line = evt.split('\n').find((l) => l.startsWith('data:'));
          if (!line) continue;
          let data: Record<string, unknown>;
          try {
            data = JSON.parse(line.slice(5).trim());
          } catch {
            continue;
          }
          switch (data.type) {
            case 'start':
              cb.onStart?.();
              break;
            case 'token':
              cb.onToken?.(String(data.content ?? ''));
              break;
            case 'citations':
              cb.onCitations?.((data.citations as Citation[]) ?? []);
              break;
            case 'done':
              cb.onDone?.((data.usage as { tokens_in: number; tokens_out: number }) ?? { tokens_in: 0, tokens_out: 0 });
              break;
            case 'error':
              cb.onError?.(String(data.code ?? 'UNKNOWN'), String(data.message ?? '未知错误'));
              break;
          }
        }
      }
    } catch (e) {
      if ((e as Error).name !== 'AbortError') {
        cb.onError?.('STREAM_BROKEN', '连接中断，回答可能不完整');
      }
    }
  })();

  return controller;
}

export async function verifyKey(payload: {
  api_key: string;
  provider: string;
  base_url?: string;
  model?: string;
}): Promise<{ valid: boolean; message: string }> {
  try {
    const resp = await fetch('/api/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!data.ok) return { valid: false, message: data?.error?.message ?? '验证失败' };
    return data.data.valid
      ? { valid: true, message: `连接成功（${data.data.model || '模型可用'}）` }
      : { valid: false, message: data.data.message ?? 'Key 无效' };
  } catch {
    return { valid: false, message: '网络连接失败，无法验证' };
  }
}

export async function sendFeedback(payload: {
  q_hash: string;
  feedback: 'up' | 'down';
  reason?: string;
  session_id?: string;
}): Promise<boolean> {
  try {
    const resp = await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return resp.ok;
  } catch {
    return false;
  }
}

export async function fetchHotQuestions(): Promise<{ q: string; label: string }[]> {
  try {
    const resp = await fetch('/api/hot_questions');
    const data = await resp.json();
    return data.ok ? data.data : [];
  } catch {
    return [];
  }
}

export async function fetchHealth(): Promise<{ status: string; chunks: number; platform_key_configured: boolean } | null> {
  try {
    const resp = await fetch('/api/health');
    const data = await resp.json();
    return data.ok ? data.data : null;
  } catch {
    return null;
  }
}
