import { Fragment, type ReactNode } from 'react';

/** Small, dependency-free Markdown renderer (headings, lists, code, quotes, tables, bold/italic/code spans). */
export function Markdown({ text, className }: { text: string; className?: string }) {
  return <div className={`md ${className ?? ''}`}>{renderBlocks(text ?? '')}</div>;
}

function inline(s: string, key = 0): ReactNode[] {
  const out: ReactNode[] = [];
  const re = /(`[^`]+`)|(\*\*[^*]+\*\*)|(\*[^*\s][^*]*\*)|(\[[^\]]+\]\([^)]+\))/g;
  let last = 0; let m: RegExpExecArray | null; let i = 0;
  while ((m = re.exec(s))) {
    if (m.index > last) out.push(s.slice(last, m.index));
    const t = m[0];
    if (t.startsWith('`')) out.push(<code key={`${key}-${i++}`}>{t.slice(1, -1)}</code>);
    else if (t.startsWith('**')) out.push(<strong key={`${key}-${i++}`}>{t.slice(2, -2)}</strong>);
    else if (t.startsWith('[')) { const mm = t.match(/\[([^\]]+)\]\(([^)]+)\)/)!; out.push(<a key={`${key}-${i++}`} href={mm[2]} target="_blank" rel="noreferrer" className="text-cyan underline">{mm[1]}</a>); }
    else out.push(<em key={`${key}-${i++}`}>{t.slice(1, -1)}</em>);
    last = m.index + t.length;
  }
  if (last < s.length) out.push(s.slice(last));
  return out;
}

function renderBlocks(text: string): ReactNode[] {
  const lines = text.replace(/\r\n/g, '\n').split('\n');
  const out: ReactNode[] = [];
  let i = 0; let k = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (line.startsWith('```')) {
      const buf: string[] = []; i++;
      while (i < lines.length && !lines[i].startsWith('```')) buf.push(lines[i++]);
      i++;
      out.push(<pre key={k++}><code>{buf.join('\n')}</code></pre>);
      continue;
    }
    const h = line.match(/^(#{1,4})\s+(.*)$/);
    if (h) { const L = Math.min(h[1].length, 3); const C = (`h${L}`) as 'h1'; out.push(<C key={k++}>{inline(h[2])}</C>); i++; continue; }
    if (line.startsWith('>')) {
      const buf: string[] = [];
      while (i < lines.length && lines[i].startsWith('>')) buf.push(lines[i++].replace(/^>\s?/, ''));
      out.push(<blockquote key={k++}>{inline(buf.join(' '))}</blockquote>);
      continue;
    }
    if (/^\s*\|/.test(line) && i + 1 < lines.length && /^\s*\|?\s*:?-{2,}/.test(lines[i + 1])) {
      const row = (l: string) => l.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
      const head = row(line); i += 2;
      const rows: string[][] = [];
      while (i < lines.length && /^\s*\|/.test(lines[i])) rows.push(row(lines[i++]));
      out.push(<table key={k++}><thead><tr>{head.map((c, j) => <th key={j}>{inline(c)}</th>)}</tr></thead><tbody>{rows.map((r, ri) => <tr key={ri}>{r.map((c, j) => <td key={j}>{inline(c)}</td>)}</tr>)}</tbody></table>);
      continue;
    }
    if (/^\s*([*-]|\d+\.)\s+/.test(line)) {
      const ordered = /^\s*\d+\./.test(line);
      const items: string[] = [];
      while (i < lines.length && /^\s*([*-]|\d+\.)\s+/.test(lines[i])) items.push(lines[i++].replace(/^\s*([*-]|\d+\.)\s+/, ''));
      const L = ordered ? 'ol' : 'ul';
      out.push(<L key={k++}>{items.map((it, j) => <li key={j}>{inline(it, j)}</li>)}</L>);
      continue;
    }
    if (!line.trim()) { i++; continue; }
    const buf: string[] = [];
    while (i < lines.length && lines[i].trim() && !/^(#{1,4}\s|```|>|\s*([*-]|\d+\.)\s|\s*\|)/.test(lines[i])) buf.push(lines[i++]);
    if (!buf.length) { buf.push(lines[i++]); }
    out.push(<p key={k++}>{buf.map((b, j) => <Fragment key={j}>{j > 0 && ' '}{inline(b, j)}</Fragment>)}</p>);
  }
  return out;
}
