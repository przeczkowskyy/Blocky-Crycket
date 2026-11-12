import { loader } from '@monaco-editor/react';
import * as monaco from 'monaco-editor';
import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker';
import jsonWorker from 'monaco-editor/esm/vs/language/json/json.worker?worker';
import tsWorker from 'monaco-editor/esm/vs/language/typescript/ts.worker?worker';

// Bundle Monaco locally (no CDN) so the studio works offline.
(self as any).MonacoEnvironment = {
  getWorker(_: unknown, label: string) {
    if (label === 'json') return new jsonWorker();
    if (label === 'typescript' || label === 'javascript') return new tsWorker();
    return new editorWorker();
  },
};

monaco.editor.defineTheme('studio-dark', {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'keyword', foreground: 'f5c542' },
    { token: 'string', foreground: '7ee2b8' },
    { token: 'number', foreground: 'a78bfa' },
    { token: 'comment', foreground: '5d6678', fontStyle: 'italic' },
  ],
  colors: {
    'editor.background': '#0c0f15',
    'editor.lineHighlightBackground': '#141922',
    'editorLineNumber.foreground': '#3a4252',
    'editorGutter.background': '#0c0f15',
    'diffEditor.insertedTextBackground': '#34d39922',
    'diffEditor.removedTextBackground': '#f0525222',
  },
});

loader.config({ monaco });

export const MONACO_OPTIONS = {
  fontSize: 13,
  fontFamily: "'Cascadia Code', 'JetBrains Mono', Consolas, monospace",
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
  automaticLayout: true,
  tabSize: 4,
  renderWhitespace: 'selection' as const,
  smoothScrolling: true,
};
