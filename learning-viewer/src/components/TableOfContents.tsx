'use client';

import { useEffect, useMemo, useState } from 'react';
import type { RefObject } from 'react';
import { ChevronRight } from 'lucide-react';
import clsx from 'clsx';
import GithubSlugger from 'github-slugger';

type Heading = {
  id: string;
  text: string;
  level: number;
};

type TableOfContentsProps = {
  content: string;
  className?: string;
  /** Optional ref to the scroll container holding the headings.
   *  When provided, IntersectionObserver uses it as `root` for accurate tracking. */
  scrollContainerRef?: RefObject<HTMLElement | null>;
};

export default function TableOfContents({ content, className, scrollContainerRef }: TableOfContentsProps) {
  const headings = useMemo(() => {
    // Extract headings from markdown content
    const headingRegex = /^(#{1,6})\s+(.+)$/gm;
    const matches: Heading[] = [];
    let match;
    const slugger = new GithubSlugger();

    while ((match = headingRegex.exec(content)) !== null) {
      const level = match[1].length;
      const text = match[2].trim();
      // Generate ID using github-slugger (same as MarkdownRenderer)
      const id = slugger.slug(text);

      matches.push({ id, text, level });
    }

    return matches;
  }, [content]);

  const [activeId, setActiveId] = useState<string>('');

  // Update active heading based on scroll position
  useEffect(() => {
    if (headings.length === 0) return;

    const observerOptions: IntersectionObserverInit = {
      root: scrollContainerRef?.current ?? null,
      rootMargin: '-100px 0px -66%',
      threshold: 0,
    };

    const observerCallback = (entries: IntersectionObserverEntry[]) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setActiveId(entry.target.id);
        }
      });
    };

    const observer = new IntersectionObserver(observerCallback, observerOptions);

    // Observe all headings
    headings.forEach((heading) => {
      const element = document.getElementById(heading.id);
      if (element) {
        observer.observe(element);
      }
    });

    return () => {
      observer.disconnect();
    };
  }, [headings, scrollContainerRef]);

  // Scroll to heading when clicked — manually calculates offset within
  // the scroll container so it works reliably in nested scroll layouts.
  const handleHeadingClick = (id: string) => {
    const element = document.getElementById(id);
    const container = scrollContainerRef?.current;
    if (element && container) {
      const containerRect = container.getBoundingClientRect();
      const elementRect = element.getBoundingClientRect();
      const scrollOffset = elementRect.top - containerRect.top + container.scrollTop;
      const headerHeight = 80; // sticky header
      container.scrollTo({
        top: scrollOffset - headerHeight,
        behavior: 'smooth',
      });
      setActiveId(id);
    } else if (element) {
      // Fallback if no scroll container ref
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setActiveId(id);
    }
  };

  if (headings.length === 0) {
    return (
      <aside className={clsx('p-4', className)}>
        <h3 className="text-xs uppercase tracking-[0.3em] text-white/50 mb-4">Table of Contents</h3>
        <p className="text-xs text-white/40">No headings found</p>
      </aside>
    );
  }

  return (
    <aside className={clsx('flex flex-col p-4 overflow-hidden', className)}>
      <h3 className="text-xs uppercase tracking-[0.3em] text-white/50 mb-4 sticky top-0 bg-slate-900/30 pb-2">
        Table of Contents
      </h3>
      <nav className="flex-1 overflow-y-auto pr-2 space-y-0.5">
        {headings.map((heading, index) => {
          const paddingLeft = `${(heading.level - 1) * 12 + 8}px`;
          const isActive = activeId === heading.id;

          return (
            <button
              key={`${heading.id}-${index}`}
              onClick={() => handleHeadingClick(heading.id)}
              className={clsx(
                'w-full text-left text-xs py-1.5 px-2 rounded transition-all flex items-start gap-1.5',
                isActive
                  ? 'bg-emerald-500/20 text-emerald-200 font-medium'
                  : 'text-white/60 hover:bg-white/10 hover:text-white/80',
              )}
              style={{ paddingLeft }}
              title={heading.text}
            >
              <ChevronRight
                size={10}
                className={clsx(
                  'transition-transform flex-shrink-0 mt-0.5',
                  isActive ? 'rotate-90 text-emerald-300 opacity-100' : 'opacity-30',
                  heading.level > 1 && 'opacity-20',
                )}
              />
              <span className="truncate leading-relaxed">{heading.text}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
