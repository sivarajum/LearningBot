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

type MarkdownRendererProps = {
  content: string;
};

type CodeProps = ComponentPropsWithoutRef<'code'> & {
  inline?: boolean;
  node?: unknown;
};

type HeadingProps = ComponentPropsWithoutRef<'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'> & {
  level?: number;
};

const prismStyle = vscDarkPlus as { [key: string]: CSSProperties };

export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
  // Create a fresh slugger per render to avoid shared state issues
  // across concurrent renders or StrictMode double-renders
  const slugger = useMemo(() => new GithubSlugger(), [content]);

  return (
    <div className="markdown-content">
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
        h4: ({ children, ...props }: HeadingProps) => {
          const id = slugger.slug(String(children));
          return <h4 id={id} className="scroll-mt-16" {...props}>{children}</h4>;
        },
        h5: ({ children, ...props }: HeadingProps) => {
          const id = slugger.slug(String(children));
          return <h5 id={id} className="scroll-mt-16" {...props}>{children}</h5>;
        },
        h6: ({ children, ...props }: HeadingProps) => {
          const id = slugger.slug(String(children));
          return <h6 id={id} className="scroll-mt-16" {...props}>{children}</h6>;
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
              <div className="my-6 rounded-lg overflow-hidden border border-white/10 shadow-lg">
                <div className="flex items-center justify-between bg-slate-800/50 px-4 py-2 border-b border-white/10">
                  <span className="text-xs font-mono text-white/70 uppercase tracking-wide">{language}</span>
                </div>
                <SyntaxHighlighter
                  PreTag="div"
                  language={language}
                  style={prismStyle}
                  customStyle={{
                    margin: 0,
                    padding: '1.5rem',
                    backgroundColor: '#1e1e1e',
                    fontSize: '14px',
                    lineHeight: '1.6',
                    fontFamily: '"Monaco", "Menlo", "Ubuntu Mono", "Consolas", "source-code-pro", monospace',
                  }}
                  showLineNumbers={code.split('\n').length > 10}
                  lineNumberStyle={{
                    minWidth: '3em',
                    paddingRight: '1em',
                    color: '#858585',
                    userSelect: 'none',
                  }}
                  {...rest}
                >
                  {code}
                </SyntaxHighlighter>
              </div>
            );
          }
          
          // Code block without language specified
          if (!inline && !language) {
            return (
              <div className="my-6 rounded-lg overflow-hidden border border-white/10 shadow-lg bg-slate-900/50">
                <pre className="p-4 overflow-x-auto">
                  <code className="text-sm font-mono text-slate-200 whitespace-pre">
                    {code}
                  </code>
                </pre>
              </div>
            );
          }

          return (
            <code 
              className={clsx("px-1.5 py-0.5 rounded bg-slate-800/50 text-cyan-300 text-sm font-mono border border-slate-700/50", className)} 
              {...props}
            >
              {children}
            </code>
          );
        },
      }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

