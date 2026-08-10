// Lightweight markdown → HTML renderer for quest content
// Handles: headers, bold, italic, links, images, tables, lists, blockquotes, hr
// Custom: :::callout emoji="X" blocks → game-style player comments

export function renderMarkdown(md: string): string {
  // === STEP 0: Extract callouts (raw HTML, restored at the very end) ===
  const callouts: string[] = [];
  let html = md.replace(/:::callout\s+emoji="([^"]*)"\s*\n([\s\S]*?):::/g,
    (_: string, emoji: string, content: string) => {
      const tag = getCalloutTag(emoji);
      const calloutHtml = `<div class="quest-callout"><span class="quest-callout__avatar">${emoji}</span><div class="quest-callout__body"><span class="quest-callout__tag">${tag}</span><div class="quest-callout__content">${content.trim()}</div></div></div>`;
      callouts.push(calloutHtml);
      return `@@CALLOUT_${callouts.length - 1}@@`;
    });

  // === STEP 1: Escape HTML ===
  html = html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  // === STEP 2: Restore placeholder markers (they contain only ASCII text, safe) ===
  html = html.replace(/@@CALLOUT_(\d+)@@/g, (_, idx) => `@@CALLOUT_${idx}@@`);

  // === STEP 3: Process inline markdown ===
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_, alt, src) => {
    return `<img src="${src}" alt="${alt}" loading="lazy" />`;
  });
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

  // Auto-link bare URLs (not already inside <a> tag)
  html = html.replace(/(?<!href="|">)(https?:\/\/[^\s<>"')]+)/g,
    '<a href="$1" target="_blank" rel="noopener">$1</a>');

  // === STEP 4: Block-level markdown ===
  html = html.replace(/^---+\s*$/gm, '<hr />');
  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

  // Blockquotes (single line)
  html = html.replace(/^>\s*(.+)$/gm, '&gt; $1<br/>');
  html = html.replace(/((?:&gt; .+<br\/>\n?)+)/g, '<blockquote>$1</blockquote>');

  // Lists
  html = html.replace(/^[\-\*]\s+(.+)$/gm, '<li>$1</li>');
  html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>');
  html = html.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');

  // Tables
  html = html.replace(/((?:\s*\|.+\|\n?)+)/g, (match: string) => {
    const lines = match.trim().split('\n').filter(l => l.trim().includes('|'));
    if (lines.length < 2) return match;
    const hasHeader = lines.length > 1 && /^\|?[\s\-:|]+\|?$/.test(lines[1].trim());
    const startIdx = hasHeader ? 2 : 0;
    let table = '<table>';
    if (hasHeader) {
      table += '<thead><tr>';
      lines[0].split('|').filter(c => c.trim()).forEach(c => { table += `<th>${c.trim()}</th>`; });
      table += '</tr></thead>';
    }
    table += '<tbody>';
    for (let i = startIdx; i < lines.length; i++) {
      table += '<tr>';
      lines[i].split('|').filter(c => c.trim()).forEach(c => { table += `<td>${c.trim()}</td>`; });
      table += '</tr>';
    }
    table += '</tbody></table>';
    return table;
  });

  // Line breaks → paragraphs
  html = html.replace(/\n\n/g, '</p><p>');
  html = html.replace(/\n/g, '<br/>');

  // Extract block-level elements that shouldn't be wrapped in <p>
  const blocks: string[] = [];
  html = html.replace(/(<(?:div|h[1-4]|table|ul|blockquote|hr|img|span)[^>]*>[\s\S]*?<\/(?:div|h[1-4]|table|ul|blockquote|span)>|<hr\s*\/?>|<img[^>]*>)/gi, (match) => {
    blocks.push(match);
    return `%%BLOCK_${blocks.length - 1}%%`;
  });

  html = `<p>${html}</p>`;
  blocks.forEach((block, i) => { html = html.replace(`%%BLOCK_${i}%%`, block); });

  // Clean up empty paragraphs
  html = html.replace(/<p>\s*<\/p>/g, '');
  html = html.replace(/<p><br\/><\/p>/g, '');
  html = html.replace(/<p>(\s*<br\/>\s*)+<\/p>/g, '');

  // === STEP 5: Restore callouts (raw HTML, no escaping) ===
  html = html.replace(/@@CALLOUT_(\d+)@@/g, (_, idx) => {
    return callouts[parseInt(idx)] ?? '';
  });

  return html;
}

/** Map emoji to a game-style tag label */
function getCalloutTag(emoji: string): string {
  const map: Record<string, string> = {
    '🌐': '系统提示',
    '⚔️': '老玩家锐评',
    '🤬': '玩家吐槽',
    '🩺': '校园贴士',
    '🤡': '整活预警',
    '🤨': '友情提醒',
    '🐳': '导航',
  };
  return map[emoji] ?? '玩家评论';
}