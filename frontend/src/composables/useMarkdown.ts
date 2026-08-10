// Lightweight markdown → HTML renderer for quest content
// Handles: headers, bold, italic, links, images, tables, lists, blockquotes, hr, callouts
// Images use Vite's import.meta.url to resolve @/assets paths at build time

export function renderMarkdown(md: string): string {
  let html = md;

  // Escape HTML first
  html = html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  // Images: ![alt](path) → <img>  
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_, alt, src) => {
    return `<img src="${src}" alt="${alt}" loading="lazy" />`;
  });

  // Bold: **text**
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

  // Italic: *text* (but not **)
  html = html.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');

  // Inline code: `text`
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Links: [text](url)
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

  // Horizontal rules
  html = html.replace(/^---+\s*$/gm, '<hr />');

  // Headers (must come before bold/italic to avoid conflicts)
  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

  // Blockquotes: > text (multi-line support)
  html = html.replace(/^>\s*(.+)$/gm, '&gt; $1<br/>');
  // Wrap consecutive blockquote lines
  html = html.replace(/((?:&gt; .+<br\/>\n?)+)/g, '<blockquote>$1</blockquote>');

  // Unordered lists
  html = html.replace(/^[\-\*]\s+(.+)$/gm, '<li>$1</li>');
  html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>');

  // Ordered lists (simple: 1. 2. 3.)
  html = html.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');

  // Tables: parse | col1 | col2 | pattern
  html = html.replace(/((?:\|.+\|\n?)+)/g, (match: string) => {
    const lines = match.trim().split('\n').filter(l => l.includes('|'));
    if (lines.length < 2) return match;
    
    // Check if header separator row exists
    const hasHeader = lines.length > 1 && /^\|[\s\-:|]+\|$/.test(lines[1]);
    const startIdx = hasHeader ? 2 : 0;
    
    let table = '<table>';
    if (hasHeader) {
      table += '<thead><tr>';
      lines[0].split('|').filter(c => c.trim()).forEach(c => {
        table += `<th>${c.trim()}</th>`;
      });
      table += '</tr></thead>';
    }
    
    table += '<tbody>';
    for (let i = startIdx; i < lines.length; i++) {
      table += '<tr>';
      lines[i].split('|').filter(c => c.trim()).forEach(c => {
        table += `<td>${c.trim()}</td>`;
      });
      table += '</tr>';
    }
    table += '</tbody></table>';
    return table;
  });

  // Line breaks: double newline → paragraph break, single → <br>
  html = html.replace(/\n\n/g, '</p><p>');
  html = html.replace(/\n/g, '<br/>');

  // Wrap in paragraphs (but don't wrap block elements)
  // First, extract blocks that shouldn't be in <p>
  const blocks: string[] = [];
  html = html.replace(/(<(?:h[1-4]|table|ul|blockquote|hr|img)[^>]*>[\s\S]*?<\/(?:h[1-4]|table|ul|blockquote)>|<hr\s*\/?>|<img[^>]*>)/gi, (match) => {
    blocks.push(match);
    return `%%BLOCK_${blocks.length - 1}%%`;
  });

  // Wrap remaining content in <p>
  html = `<p>${html}</p>`;

  // Restore blocks
  blocks.forEach((block, i) => {
    html = html.replace(`%%BLOCK_${i}%%`, block);
  });

  // Clean up empty paragraphs
  html = html.replace(/<p>\s*<\/p>/g, '');
  html = html.replace(/<p><br\/><\/p>/g, '');
  html = html.replace(/<p>(\s*<br\/>\s*)+<\/p>/g, '');

  return html;
}

// Resolve Vite asset paths at build time
// Vite replaces `new URL('@/assets/...', import.meta.url).href` with the hashed path
// For simplicity, we use @/assets/ paths and let Vite handle them at import time
export function resolveAssetPath(assetPath: string): string {
  // At build time, Vite processes these imports
  // We prefix with / to make them absolute from the server root
  if (assetPath.startsWith('@/')) {
    return assetPath.replace('@/', '/src/');
  }
  return assetPath;
}
