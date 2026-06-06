'use client';

import { useMemo, useState, useRef, useEffect, useCallback, Component } from 'react';
import type { ReactNode, ErrorInfo } from 'react';
import useSWR from 'swr';
import clsx from 'clsx';
import {
  ArrowLeft,
  Folder,
  FolderOpen,
  Loader2,
  Search,
  FileText,
  Star,
  StarOff,
  Zap,
  PanelRightClose,
  PanelRightOpen,
  Eye,
  EyeOff,
  Command,
} from 'lucide-react';

import type { MarkdownPayload, TreeNode } from '@/lib/types';
import MarkdownRenderer from './MarkdownRenderer';
import TableOfContents from './TableOfContents';
import SearchModal from './SearchModal';
import VisualModeRenderer from './VisualModeRenderer';

type ExplorerProps = {
  initialTree: TreeNode[];
};

const fetcher = (url: string) =>
  fetch(url).then((res) => {
    if (!res.ok) {
      throw new Error('Unable to load data');
    }
    return res.json();
  });

const FAVORITES_KEY = 'learningbot-favorites';
const MAX_FAVORITES = 20;

function loadFavorites(): string[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(FAVORITES_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveFavorites(favs: string[]) {
  try {
    localStorage.setItem(FAVORITES_KEY, JSON.stringify(favs));
  } catch {
    // localStorage unavailable (private browsing, full storage)
  }
}

/** Sort children so cheatsheet.md appears first in each folder */
function sortWithCheatsheetFirst(children: TreeNode[]): TreeNode[] {
  return [...children].sort((a, b) => {
    const aIsCheatsheet = a.type === 'file' && a.name.toLowerCase() === 'cheatsheet.md';
    const bIsCheatsheet = b.type === 'file' && b.name.toLowerCase() === 'cheatsheet.md';
    if (aIsCheatsheet && !bIsCheatsheet) return -1;
    if (!aIsCheatsheet && bIsCheatsheet) return 1;
    return 0;
  });
}

/** Find cheatsheet.md path in a folder's direct children */
function findCheatsheet(node: TreeNode): string | null {
  if (node.type !== 'folder' || !node.children) return null;
  const cs = node.children.find(
    (c) => c.type === 'file' && c.name.toLowerCase() === 'cheatsheet.md'
  );
  return cs ? cs.path : null;
}

/** Count headings in markdown content */
function countHeadings(content: string): number {
  const headingRegex = /^#{1,6}\s+.+$/gm;
  const matches = content.match(headingRegex);
  return matches ? matches.length : 0;
}

export default function Explorer({ initialTree }: ExplorerProps) {
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [navigationHistory, setNavigationHistory] = useState<string[]>([]);
  const [sidebarFilter, setSidebarFilter] = useState('');
  const treeData = initialTree;
  const [manuallyExpanded, setManuallyExpanded] = useState<Set<string>>(new Set());
  const [sidebarWidth, setSidebarWidth] = useState(300);
  const [isResizing, setIsResizing] = useState(false);
  const resizeRef = useRef<HTMLDivElement>(null);
  const contentScrollRef = useRef<HTMLDivElement>(null);

  // Feature: Cmd+K Search Modal
  const [searchOpen, setSearchOpen] = useState(false);

  // Feature: Visual Mode Toggle
  const [visualMode, setVisualMode] = useState(() => {
    if (typeof window === 'undefined') return false;
    try { return localStorage.getItem('learningbot-visual-mode') === 'true'; } catch { return false; }
  });

  // Refs to read current state without nesting setState calls
  const selectedPathRef = useRef<string | null>(null);
  const historyRef = useRef<string[]>([]);
  useEffect(() => { selectedPathRef.current = selectedPath; }, [selectedPath]);
  useEffect(() => { historyRef.current = navigationHistory; }, [navigationHistory]);

  const toggleVisualMode = useCallback(() => {
    setVisualMode((prev) => {
      const next = !prev;
      try { localStorage.setItem('learningbot-visual-mode', String(next)); } catch { /* ignored */ }
      return next;
    });
    // Scroll content to top when toggling to avoid disorientation
    contentScrollRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  /** Navigate to a file, pushing current path onto history stack */
  const navigateTo = useCallback((path: string) => {
    const prev = selectedPathRef.current;
    if (prev) setNavigationHistory((h) => [...h, prev]);
    setSelectedPath(path);
  }, []);

  /** Go back to the previous file in history, or clear selection */
  const navigateBack = useCallback(() => {
    const h = historyRef.current;
    const prev = h[h.length - 1] ?? null;
    setSelectedPath(prev);
    setNavigationHistory(h.slice(0, -1));
  }, []);

  // Cmd+K / Ctrl+K keyboard shortcut
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen((prev) => !prev);
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, []);

  // Feature 3: Favorites (load from localStorage via initializer to avoid effect-setState)
  const [favorites, setFavorites] = useState<string[]>(loadFavorites);

  // Favorites cap warning toast
  const [favCapWarning, setFavCapWarning] = useState(false);
  const warningTimerRef = useRef<ReturnType<typeof setTimeout>>(undefined);
  useEffect(() => () => clearTimeout(warningTimerRef.current), []);

  const toggleFavorite = useCallback((path: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setFavorites((prev) => {
      let next: string[];
      if (prev.includes(path)) {
        next = prev.filter((p) => p !== path);
      } else {
        if (prev.length >= MAX_FAVORITES) {
          clearTimeout(warningTimerRef.current);
          setFavCapWarning(true);
          warningTimerRef.current = setTimeout(() => setFavCapWarning(false), 3000);
          return prev;
        }
        next = [...prev, path];
      }
      saveFavorites(next);
      return next;
    });
  }, []);

  // Feature 4: TOC panel toggle
  const [tocOpen, setTocOpen] = useState(true);

  // Auto-expand parent folders when a file is selected (computed, not state)
  const expanded = useMemo(() => {
    const result = new Set(manuallyExpanded);

    if (selectedPath) {
      const pathParts = selectedPath.split('/').filter(Boolean);
      // Build all parent folder paths
      for (let i = 1; i < pathParts.length; i++) {
        result.add(pathParts.slice(0, i).join('/'));
      }
    }

    return result;
  }, [selectedPath, manuallyExpanded]);

  const { data, isLoading, error } = useSWR<MarkdownPayload>(
    selectedPath ? `/api/content?path=${encodeURIComponent(selectedPath)}` : null,
    fetcher,
    { revalidateOnFocus: false },
  );

  const contentText = data?.content ?? '';
  const headingCount = useMemo(() => {
    if (!contentText) return 0;
    return countHeadings(contentText);
  }, [contentText]);
  const showToc = !!selectedPath && !!data && headingCount >= 3;

  const filteredTree = useMemo(() => {
    if (!sidebarFilter.trim()) return treeData;

    const query = sidebarFilter.toLowerCase();
    const filterNode = (node: TreeNode): TreeNode | null => {
      if (node.type === 'file') {
        return node.name.toLowerCase().includes(query) ? node : null;
      }

      const children =
        node.children
          ?.map(filterNode)
          .filter((child): child is TreeNode => Boolean(child)) ?? [];

      if (children.length > 0 || node.name.toLowerCase().includes(query)) {
        return { ...node, children };
      }

      return null;
    };

    return treeData
      .map(filterNode)
      .filter((node): node is TreeNode => Boolean(node));
  }, [sidebarFilter, treeData]);

  const stats = useMemo(() => summarizeTree(treeData), [treeData]);

  const handleFolderToggle = useCallback((path: string) => {
    setManuallyExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  }, []);

  /** When a folder NAME is clicked, expand it AND auto-select cheatsheet.md if present */
  const handleFolderClick = useCallback((node: TreeNode) => {
    // Always toggle expansion
    handleFolderToggle(node.path);
    // Auto-select cheatsheet.md if it exists in this folder
    const csPath = findCheatsheet(node);
    if (csPath) {
      navigateTo(csPath);
    }
  }, [handleFolderToggle, navigateTo]);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
  }, []);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      
      const newWidth = e.clientX;
      // Min width: 200px, Max width: 600px
      if (newWidth >= 200 && newWidth <= 600) {
        setSidebarWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing]);

  return (
    <div className="flex min-h-screen bg-slate-950/95 text-white relative">
      <aside 
        className="flex flex-col flex-shrink-0 border-r border-white/10 bg-slate-900/80 p-4 shadow-2xl h-screen overflow-hidden transition-[width] duration-0"
        style={{ width: `${sidebarWidth}px` }}
      >
        <header className="mb-4 pb-4 border-b border-white/10">
          <h1 className="text-lg font-semibold text-white mb-1">
            LearningBot Explorer
          </h1>
          <p className="text-xs text-white/50">
            Browse your learning content
          </p>
        </header>

        <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm mb-2">
          <Search size={14} className="text-emerald-300/80 flex-shrink-0" />
          <input
            value={sidebarFilter}
            onChange={(event) => setSidebarFilter(event.target.value)}
            placeholder="Search topics..."
            className="flex-1 bg-transparent text-xs text-white placeholder:text-white/40 focus:outline-none"
          />
        </div>
        <button
          onClick={() => setSearchOpen(true)}
          className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white/50 hover:bg-white/10 hover:text-white/70 transition mb-3 w-full"
        >
          <Search size={12} />
          <span className="flex-1 text-left">Deep search...</span>
          <kbd className="flex items-center gap-0.5 rounded border border-white/20 px-1 py-0.5 text-[10px] font-mono">
            <Command size={10} />K
          </kbd>
        </button>

        {/* Favorites Section */}
        {favorites.length > 0 && (
          <div className="mb-3 pb-3 border-b border-white/10">
            <h3 className="text-[10px] uppercase tracking-[0.3em] text-amber-300/70 mb-2 px-1 flex items-center gap-1.5">
              <Star size={10} className="fill-amber-300/70" />
              Favorites
            </h3>
            <div className="space-y-0.5">
              {favorites.map((fav) => {
                const parts = fav.split('/').filter(Boolean);
                const label =
                  parts.length >= 2
                    ? `${parts[parts.length - 2]} / ${parts[parts.length - 1]}`
                    : parts[parts.length - 1] ?? fav;
                return (
                  <div
                    key={fav}
                    className={clsx(
                      'flex w-full items-center gap-2 rounded-lg px-2 py-1 text-left text-xs transition',
                      selectedPath === fav
                        ? 'bg-amber-500/20 text-amber-200'
                        : 'text-white/70 hover:bg-white/10',
                    )}
                  >
                    <button
                      onClick={() => navigateTo(fav)}
                      className="flex items-center gap-2 flex-1 min-w-0"
                    >
                      <Star size={12} className="fill-amber-400 text-amber-400 flex-shrink-0" />
                      <span className="truncate">{label}</span>
                    </button>
                    <button
                      onClick={(e) => toggleFavorite(fav, e)}
                      className="text-white/30 hover:text-red-400 flex-shrink-0"
                      title="Remove from favorites"
                    >
                      <StarOff size={12} />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <nav className="flex-1 overflow-y-auto pr-2 text-sm">
          {filteredTree.length === 0 ? (
            <p className="text-center text-xs text-white/50">
              No matches for {'\u201C'}{sidebarFilter}{'\u201D'}
            </p>
          ) : (
            filteredTree.map((node) => (
              <TreeNodeItem
                key={node.path || node.name}
                node={node}
                depth={0}
                expanded={expanded}
                onFolderClick={handleFolderClick}
                selectedPath={selectedPath}
                onSelectFile={navigateTo}
                favorites={favorites}
                onToggleFavorite={toggleFavorite}
              />
            ))
          )}
        </nav>
      </aside>

      {/* Resize Handle */}
      <div
        ref={resizeRef}
        onMouseDown={handleMouseDown}
        className={clsx(
          'w-1 hover:w-1.5 bg-slate-700/30 hover:bg-emerald-500/60 cursor-col-resize flex-shrink-0 transition-all relative z-10 group',
          isResizing && 'bg-emerald-500/80 w-1.5'
        )}
      >
        <div className="absolute inset-y-0 -left-2 -right-2 cursor-col-resize" />
      </div>

      <section className="flex flex-col flex-1 bg-slate-950/60 relative h-screen overflow-hidden">
        <div className="flex items-center justify-between border-b border-white/5 px-6 py-4 backdrop-blur bg-slate-900/40 sticky top-0 z-10">
          <div>
            <h2 className="text-lg font-semibold text-white">
              {data?.name ?? 'Select a topic to view content'}
            </h2>
            {selectedPath && data && (
              <div className="flex items-center gap-1 text-xs text-white/50 mt-1 flex-wrap">
                {data.breadcrumbs.map((b, i) => {
                  const isLast = i === data.breadcrumbs.length - 1;
                  return (
                    <span key={b.path} className="flex items-center gap-1">
                      {i > 0 && <span className="text-white/30">/</span>}
                      {isLast ? (
                        <span className="text-white/60">{b.label}</span>
                      ) : (
                        <button
                          onClick={() => {
                            setManuallyExpanded((prev) => {
                              const next = new Set(prev);
                              next.add(b.path);
                              return next;
                            });
                          }}
                          className="hover:text-emerald-300 hover:underline transition cursor-pointer"
                        >
                          {b.label}
                        </button>
                      )}
                    </span>
                  );
                })}
              </div>
            )}
          </div>
          <div className="flex items-center gap-2">
            {/* TOC toggle button */}
            {showToc && (
              <button
                onClick={() => setTocOpen((prev) => !prev)}
                className="inline-flex items-center gap-1.5 rounded-lg border border-white/20 px-3 py-1.5 text-xs text-white/80 transition hover:bg-white/10"
                title={tocOpen ? 'Hide table of contents' : 'Show table of contents'}
              >
                {tocOpen ? <PanelRightClose size={14} /> : <PanelRightOpen size={14} />}
                TOC
              </button>
            )}
            {selectedPath && data && (
              <button
                onClick={toggleVisualMode}
                className={clsx(
                  'inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs transition',
                  visualMode
                    ? 'border-emerald-500/40 bg-emerald-500/15 text-emerald-300'
                    : 'border-white/20 text-white/60 hover:bg-white/10 hover:text-white/80',
                )}
                title={visualMode ? 'Show full document' : 'Show only diagrams & tables'}
              >
                {visualMode ? <EyeOff size={14} /> : <Eye size={14} />}
                {visualMode ? 'Full Document' : 'Diagrams & Tables'}
              </button>
            )}
            {selectedPath && (
              <button
                onClick={navigateBack}
                className={clsx(
                  'inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs transition',
                  navigationHistory.length > 0
                    ? 'border-white/20 text-white/80 hover:bg-white/10'
                    : 'border-white/10 text-white/40 hover:bg-white/5',
                )}
                title={navigationHistory.length > 0 ? 'Go to previous file' : 'Go to home screen'}
              >
                <ArrowLeft size={14} />
                {navigationHistory.length > 0 ? 'Back' : 'Home'}
              </button>
            )}
          </div>
        </div>

        <div ref={contentScrollRef} className="flex-1 overflow-y-auto">
          {!selectedPath && (
            <div className="px-6 py-8">
              <HeroEmptyState folderCount={stats.folders} fileCount={stats.files} />
            </div>
          )}

          {selectedPath && (
            <div className="px-6 py-8">
              {isLoading && (
                <div className="flex items-center gap-2 text-sm text-white/70">
                  <Loader2 size={16} className="animate-spin" />
                  Loading content…
                </div>
              )}

              {error && (
                <p className="text-sm text-red-300">
                  Unable to load this file. Please try again.
                </p>
              )}

              {data && (
                <ContentErrorBoundary key={selectedPath}>
                  <article className="prose prose-invert max-w-4xl mx-auto px-8 py-10">
                    {visualMode ? (
                      <VisualModeRenderer content={data.content} />
                    ) : (
                      <MarkdownRenderer content={data.content} />
                    )}
                  </article>
                </ContentErrorBoundary>
              )}
            </div>
          )}
        </div>
      </section>

      {/* Feature 4: Table of Contents Panel */}
      {showToc && tocOpen && (
        <aside className="flex-shrink-0 w-[200px] border-l border-white/10 bg-slate-900/50 h-screen overflow-y-auto">
          <TableOfContents content={data.content} scrollContainerRef={contentScrollRef} />
        </aside>
      )}

      <SearchModal
        open={searchOpen}
        onClose={() => setSearchOpen(false)}
        onSelect={navigateTo}
      />

      {/* Favorites cap warning toast */}
      {favCapWarning && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 rounded-lg bg-amber-600/90 px-4 py-2 text-sm text-white shadow-lg backdrop-blur animate-in fade-in slide-in-from-bottom-4">
          Favorites limit reached ({MAX_FAVORITES} max). Remove one to add more.
        </div>
      )}
    </div>
  );
}

type TreeNodeItemProps = {
  node: TreeNode;
  depth: number;
  expanded: Set<string>;
  selectedPath: string | null;
  onFolderClick: (node: TreeNode) => void;
  onSelectFile: (path: string) => void;
  favorites: string[];
  onToggleFavorite: (path: string, e: React.MouseEvent) => void;
};

function TreeNodeItem({
  node,
  depth,
  expanded,
  selectedPath,
  onFolderClick,
  onSelectFile,
  favorites,
  onToggleFavorite,
}: TreeNodeItemProps) {
  const isFolder = node.type === 'folder';
  const isExpanded = expanded.has(node.path);
  const isSelected = selectedPath === node.path;
  const isCheatsheet = !isFolder && node.name.toLowerCase() === 'cheatsheet.md';
  const isFavorited = !isFolder && favorites.includes(node.path);

  // Sort children with cheatsheet first
  const sortedChildren = useMemo(() => {
    if (!isFolder || !node.children) return [];
    return sortWithCheatsheetFirst(node.children);
  }, [isFolder, node.children]);

  return (
    <div>
      <div
        className={clsx(
          'flex w-full items-center gap-1.5 rounded-lg px-2 py-1 text-left text-sm transition group',
          isSelected ? 'bg-emerald-500/20 text-emerald-200' : 'text-white/80 hover:bg-white/10',
        )}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
      >
        <button
          className="flex items-center gap-2 flex-1 min-w-0"
          onClick={() => {
            if (isFolder) {
              onFolderClick(node);
            } else {
              onSelectFile(node.path);
            }
          }}
        >
          {isFolder ? (
            isExpanded ? <FolderOpen size={16} className="flex-shrink-0" /> : <Folder size={16} className="flex-shrink-0" />
          ) : isCheatsheet ? (
            <Zap size={16} className="text-yellow-400 flex-shrink-0" />
          ) : (
            <FileText size={16} className="flex-shrink-0" />
          )}
          <span className="truncate">{node.name}</span>
        </button>

        {/* Star icon for files */}
        {!isFolder && (
          <button
            onClick={(e) => onToggleFavorite(node.path, e)}
            className={clsx(
              'flex-shrink-0 transition',
              isFavorited
                ? 'text-amber-400'
                : 'text-white/0 group-hover:text-white/30 hover:!text-amber-400',
            )}
            title={isFavorited ? 'Remove from favorites' : 'Add to favorites'}
          >
            <Star size={14} className={clsx(isFavorited && 'fill-amber-400')} />
          </button>
        )}
      </div>

      {isFolder && isExpanded && sortedChildren.length > 0 && (
        <div className="space-y-1">
          {sortedChildren.map((child) => (
            <TreeNodeItem
              key={child.path}
              node={child}
              depth={depth + 1}
              expanded={expanded}
              selectedPath={selectedPath}
              onFolderClick={onFolderClick}
              onSelectFile={onSelectFile}
              favorites={favorites}
              onToggleFavorite={onToggleFavorite}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function HeroEmptyState({ folderCount, fileCount }: { folderCount: number; fileCount: number }) {
  return (
    <div className="mx-auto max-w-xl rounded-3xl border border-white/10 bg-white/5 p-10 text-center shadow-[0_40px_120px_rgba(6,182,212,0.2)]">
      <p className="text-xs uppercase tracking-[0.4em] text-emerald-200/70">
        Start Exploring
      </p>
      <h3 className="mt-2 text-3xl font-semibold text-white">
        Pick any markdown doc to open it here
      </h3>
      <p className="mt-4 text-sm text-white/70">
        {folderCount} folders & {fileCount} markdown files indexed automatically from your{' '}
        LearningBot workspace. Select a file on the left to see its content rendered with Mermaid,
        code highlighting, and beautiful typography.
      </p>
    </div>
  );
}

class ContentErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean }> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError(): { hasError: boolean } {
    return { hasError: true };
  }
  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Content render error:', error, info);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-8 text-center">
          <p className="text-sm text-red-300">Failed to render this content. Try selecting a different file.</p>
        </div>
      );
    }
    return this.props.children;
  }
}

function summarizeTree(nodes: TreeNode[]) {
  let folders = 0;
  let files = 0;

  const traverse = (items: TreeNode[]) => {
    for (const item of items) {
      if (item.type === 'folder') {
        folders += 1;
        if (item.children) {
          traverse(item.children);
        }
      } else {
        files += 1;
      }
    }
  };

  traverse(nodes);

  return { folders, files };
}

