// Lightweight markdown → HTML renderer for quest content
// Handles: headers, bold, italic, links, images, tables, lists, blockquotes, hr
// Custom: :::callout emoji="X" blocks → game-style player comments

export function renderMarkdown(md: string): string {
  let html = md;

  // === STEP 0: Parse custom :::callout blocks (before any other processing) ===
  html = html.replace(/:::callout\s+emoji="([^"]*)"\s*\n([\s\S]*?):::/g,
    (_: string, emoji: string, content: string) => {
      // Tag label based on emoji
      const tag = getCalloutTag(emoji);
      return `<div class="quest-callout"><span class="quest-callout__avatar">${emoji}</span><div class="quest-callout__body"><span class="quest-callout__tag">${tag}</span>${content.trim()}</div></div>`;
    });

  // Escape HTML
  html = html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  // Restore our own callout HTML (we placed it before escaping)
  html = html.replace(/&lt;div class=&quot;quest-callout&quot;&gt;/g, '<div class="quest-callout">');
  html = html.replace(/&lt;span class=&quot;quest-callout__avatar&quot;&gt;/g, '<span class="quest-callout__avatar">');
  html = html.replace(/&lt;span class=&quot;quest-callout__tag&quot;&gt;/g, '<span class="quest-callout__tag">');
  html = html.replace(/&lt;\/span&gt;&lt;div class=&quot;quest-callout__body&quot;&gt;/g, '</span><div class="quest-callout__body">');
  html = html.replace(/&lt;\/div&gt;&lt;\/div&gt;/g, '</div></div>');

  // Images: ![alt](path) → <img>  
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_, alt, src) => {
    return `<img src="${src}" alt="${alt}" loading="lazy" />`;
  });

  // Bold
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

  // Italic
  html = html.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

  // Horizontal rules
  html = html.replace(/^---+\s*$/gm, '<hr />');

  // Headers
  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

  // Blockquotes
  html = html.replace(/^>\s*(.+)$/gm, '&gt; $1<br/>');
  html = html.replace(/((?:&gt; .+<br\/>\n?)+)/g, '<blockquote>$1</blockquote>');

  // Unordered lists
  html = html.replace(/^[\-\*]\s+(.+)$/gm, '<li>$1</li>');
  html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>');

  // Ordered lists
  html = html.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');

  // Tables
  html = html.replace(/((?:\s*\|.+\|\n?)+)/g, (match: string) => {
    const lines = match.trim().split('\n').filter(l => l.trim().includes('|'));
    if (lines.length < 2) return match;
    const hasHeader = lines.length > 1 && /^\|[\s\-:|]+\|$/.test(lines[1]);
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

  // Extract blocks that shouldn't be inside <p>
  const blocks: string[] = [];
  const re = /(<(?:div|h[1-4]|table|ul|blockquote|hr|img|span)[^>]*>[\s\S]*?<\/(?:div|h[1-4]|table|ul|blockquote|span)>|<hr\s*\/?>|<img[^>]*>)/gi;
  html = html.replace(re, (match) => {
    blocks.push(match);
    return `%%BLOCK_${blocks.length - 1}%%`;
  });

  html = `<p>${html}</p>`;
  blocks.forEach((block, i) => { html = html.replace(`%%BLOCK_${i}%%`, block); });

  // Cleanup
  html = html.replace(/<p>\s*<\/p>/g, '');
  html = html.replace(/<p><br\/><\/p>/g, '');
  html = html.replace(/<p>(\s*<br\/>\s*)+<\/p>/g, '');

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
