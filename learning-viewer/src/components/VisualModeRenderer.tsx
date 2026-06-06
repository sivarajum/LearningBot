'use client';

import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import type { ComponentPropsWithoutRef, CSSProperties } from 'react';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/cjs/styles/prism';
import GithubSlugger from 'github-slugger';
import clsx from 'clsx';

import MermaidDiagram from './MermaidDiagram';

type VisualModeRendererProps = {
  content: string;
};

type CodeProps = ComponentPropsWithoutRef<'code'> & {
  inline?: boolean;
  node?: unknown;
};

type HeadingProps = ComponentPropsWithoutRef<'h1'> & { level?: number };

const VISUAL_KEYWORDS = [
  'cheatsheet',
  'cheat sheet',
  '5 things',
  'interview killer',
  'when to use',
];

/** Split markdown into sections by headings, extract only visual-worthy ones. */
function extractVisualSections(raw: string): string {
  const lines = raw.split('\n');
  const sections: { heading: string; lines: string[] }[] = [];
  let current: { heading: string; lines: string[] } = { heading: '', lines: [] };

  for (const line of lines) {
    if (/^#{1,3}\s/.test(line)) {
      if (current.heading || current.lines.length > 0) {
        sections.push(current);
      }
      current = { heading: line, lines: [] };
    } else {
      current.lines.push(line);
    }
  }
  if (current.heading || current.lines.length > 0) {
    sections.push(current);
  }

  const kept: string[] = [];

  for (const section of sections) {
    const body = section.lines.join('\n');
    const hasMermaid = /```mermaid/i.test(body);
    const hasTable = /\|.+\|/.test(body) && /\|[-:]+\|/.test(body);
    const headingLower = section.heading.toLowerCase();
    const hasKeyword = VISUAL_KEYWORDS.some((kw) => headingLower.includes(kw));

    if (hasMermaid || hasTable || hasKeyword) {
      if (section.heading) kept.push(section.heading);
      kept.push(body);
      kept.push(''); // spacing
    }
  }

  return kept.join('\n').trim();
}

const prismStyle = vscDarkPlus as { [key: string]: CSSProperties };

export default function VisualModeRenderer({ content }: VisualModeRendererProps) {
  const visual = useMemo(() => extractVisualSections(content), [content]);
  const slugger = useMemo(() => new GithubSlugger(), [content]);

  if (!visual) {
    return (
      <div className="rounded-xl border border-white/10 bg-white/5 p-8 text-center text-sm text-white/50">
        No diagrams, tables, or key sections found in this document.
      </div>
    );
  }

  return (
    <div className="markdown-content space-y-6">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw]}
        skipHtml={false}
        components={{
          h1: ({ children, ...props }: HeadingProps) => {
            const id = slugger.slug(String(children));
            return <h1 id={id} className="scroll-mt-20" {...props}>{children}</h1>;
          },
          h2: ({ children, ...props }: HeadingProps) => {
            const id = slugger.slug(String(children));
            return <h2 id={id} className="scroll-mt-20" {...props}>{children}</h2>;
          },
          h3: ({ children, ...props }: HeadingProps) => {
            const id = slugger.slug(String(children));
            return <h3 id={id} className="scroll-mt-20" {...props}>{children}</h3>;
          },
          code({ inline, className, children, ...props }: CodeProps) {
            const match = /language-(\w+)/.exec(className || '');
            const language = match?.[1];
            const code = String(children).replace(/\n$/, '');

            if (language === 'mermaid') {
              return <MermaidDiagram key={code} code={code} />;
            }

            if (!inline && language) {
              // eslint-disable-next-line @typescript-eslint/no-unused-vars
              const { style: _style, ...rest } = props;
              return (
                <div className="my-4 rounded-lg overflow-hidden border border-white/10 shadow-lg">
                  <div className="flex items-center bg-slate-800/50 px-4 py-2 border-b border-white/10">
                    <span className="text-xs font-mono text-white/70 uppercase tracking-wide">{language}</span>
                  </div>
                  <SyntaxHighlighter
                    PreTag="div"
                    language={language}
                    style={prismStyle}
                    customStyle={{
                      margin: 0, padding: '1rem',
                      backgroundColor: '#1e1e1e', fontSize: '13px',
                    }}
                    {...rest}
                  >
                    {code}
                  </SyntaxHighlighter>
                </div>
              );
            }

            return (
              <code
                className={clsx(
                  'px-1.5 py-0.5 rounded bg-slate-800/50 text-cyan-300 text-sm font-mono border border-slate-700/50',
                  className,
                )}
                {...props}
              >
                {children}
              </code>
            );
          },
        }}
      >
        {visual}
      </ReactMarkdown>
    </div>
  );
}
