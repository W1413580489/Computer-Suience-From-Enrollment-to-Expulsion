// AI 消息渲染管道（唯一入口）：Markdown → HTML → DOMPurify 消毒 → 代码高亮
//
// 安全契约：
//   - AI 输出是"运行时不可信内容"，必须先 marked 生成 HTML、再 DOMPurify 消毒，
//     顺序不可颠倒（先消毒会被 marked 还原出危险标签）
//   - DOMPurify 默认剥除 <script>/事件属性/javascript: 协议，无需额外配置
//   - 代码高亮对"已转义的代码文本"执行，输出天然安全
//   - 学生消息不走本函数，永远保持纯文本插值
//
// 与 useMarkdown.ts（任务攻略页）的关系：那条管道处理打包期可信内容
// （:::callout 自定义语法），本管道处理运行时不可信内容——两个信任域，
// 不合并。
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import hljs from 'highlight.js/lib/common';

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// 代码块渲染：有语言标注则高亮，否则纯转义（自动探测噪音大，不做）
marked.use({
  gfm: true,
  breaks: true, // 聊天场景单换行转 <br>
  renderer: {
    code(...args: unknown[]) {
      // 兼容 marked 新旧签名：新版传 token 对象，旧版传 (code, lang)
      const t = args[0] as { text?: string; lang?: string } | string;
      const lang = args[1] as string | undefined;
      const text = typeof t === 'string' ? t : (t.text ?? '');
      const rawLang = (typeof t === 'object' && t !== null ? t.lang : lang) || '';
      const language = rawLang && hljs.getLanguage(rawLang) ? rawLang : '';
      const body = language ? hljs.highlight(text, { language }).value : escapeHtml(text);
      const cls = language ? ` class="hljs language-${language}"` : ' class="hljs"';
      return `<pre><code${cls}>${body}</code></pre>`;
    },
  },
});

export function renderAiMarkdown(md: string): string {
  if (!md) return '';
  const html = marked.parse(md, { async: false }) as string;
  return DOMPurify.sanitize(html);
}
