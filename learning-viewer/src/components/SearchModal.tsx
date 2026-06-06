'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Search, FileText, Heading, AlignLeft, X, Command } from 'lucide-react';
import clsx from 'clsx';

import type { SearchMatch } from '@/app/api/search/route';

type SearchModalProps = {
  open: boolean;
  onClose: () => void;
  onSelect: (path: string) => void;
};

const MATCH_ICONS = {
  filename: FileText,
  heading: Heading,
  content: AlignLeft,
} as const;

const MATCH_LABELS = {
  filename: 'File',
  heading: 'Heading',
  content: 'Content',
} as const;

function SearchModalInner({ onClose, onSelect }: Omit<SearchModalProps, 'open'>) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchMatch[]>([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Focus input on mount
  useEffect(() => {
    const t = setTimeout(() => inputRef.current?.focus(), 50);
    return () => clearTimeout(t);
  }, []);

  // Clean up debounce timer on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  // Debounced search
  const doSearch = useCallback((q: string) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (!q.trim()) {
      setResults([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    debounceRef.current = setTimeout(async () => {
      try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(q)}&limit=15`);
        if (res.ok) {
          const data = await res.json();
          setResults(data.results ?? []);
        }
      } catch { /* ignore */ }
      setLoading(false);
    }, 200);
  }, []);

  const handleInputChange = (value: string) => {
    setQuery(value);
    setActiveIndex(0);
    doSearch(value);
  };

  const handleSelect = (path: string) => {
    onSelect(path);
    onClose();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((i) => Math.min(i + 1, results.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((i) => Math.max(i - 1, 0));
    } else if (e.key === 'Enter' && results[activeIndex]) {
      e.preventDefault();
      handleSelect(results[activeIndex].path);
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] bg-black/60 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label="Search files"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="w-full max-w-xl rounded-xl border border-white/10 bg-slate-950 shadow-2xl overflow-hidden">
        {/* Search input */}
        <div className="flex items-center gap-3 border-b border-white/10 px-4 py-3">
          <Search size={18} className="text-emerald-400 flex-shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => handleInputChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search files, headings, content..."
            className="flex-1 bg-transparent text-sm text-white placeholder:text-white/40 focus:outline-none"
          />
          {loading && (
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-emerald-400 border-t-transparent flex-shrink-0" />
          )}
          <button
            onClick={onClose}
            className="rounded p-1 text-white/40 hover:text-white/80 hover:bg-white/10 transition"
          >
            <X size={16} />
          </button>
        </div>

        {/* Results */}
        <div className="max-h-[50vh] overflow-y-auto">
          {query && !loading && results.length === 0 && (
            <div className="px-4 py-8 text-center text-sm text-white/40">
              No results for &ldquo;{query}&rdquo;
            </div>
          )}

          {results.map((result, idx) => {
            const Icon = MATCH_ICONS[result.matchType];
            return (
              <button
                key={`${result.path}-${result.matchType}-${idx}`}
                className={clsx(
                  'flex w-full items-start gap-3 px-4 py-3 text-left transition',
                  idx === activeIndex
                    ? 'bg-emerald-500/15 text-emerald-200'
                    : 'text-white/80 hover:bg-white/5',
                )}
                onClick={() => handleSelect(result.path)}
                onMouseEnter={() => setActiveIndex(idx)}
              >
                <Icon size={16} className="mt-0.5 flex-shrink-0 text-emerald-400/70" />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium truncate">{result.name}</span>
                    <span className="rounded bg-white/10 px-1.5 py-0.5 text-[10px] uppercase tracking-wider text-white/50">
                      {MATCH_LABELS[result.matchType]}
                    </span>
                  </div>
                  <p className="mt-0.5 text-xs text-white/40 truncate">
                    {result.matchType === 'filename'
                      ? result.breadcrumbs
                      : result.matchText}
                  </p>
                </div>
              </button>
            );
          })}
        </div>

        {/* Footer hint */}
        <div className="flex items-center gap-4 border-t border-white/10 px-4 py-2 text-[11px] text-white/30">
          <span className="flex items-center gap-1">
            <kbd className="rounded border border-white/20 px-1 py-0.5 font-mono text-[10px]">&#8593;&#8595;</kbd>
            navigate
          </span>
          <span className="flex items-center gap-1">
            <kbd className="rounded border border-white/20 px-1 py-0.5 font-mono text-[10px]">Enter</kbd>
            select
          </span>
          <span className="flex items-center gap-1">
            <kbd className="rounded border border-white/20 px-1 py-0.5 font-mono text-[10px]">Esc</kbd>
            close
          </span>
          <span className="ml-auto flex items-center gap-1">
            <Command size={10} />K to toggle
          </span>
        </div>
      </div>
    </div>
  );
}

/** Wrapper that unmounts inner component when closed, ensuring fresh state on re-open. */
export default function SearchModal({ open, onClose, onSelect }: SearchModalProps) {
  if (!open) return null;
  return <SearchModalInner onClose={onClose} onSelect={onSelect} />;
}
