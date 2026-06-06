'use client';

import { useEffect, useMemo, useState, useId, useCallback } from 'react';
import { X, ZoomIn } from 'lucide-react';
import mermaid from 'mermaid';

type MermaidDiagramProps = {
  code: string;
};

let initialized = false;

export default function MermaidDiagram({ code }: MermaidDiagramProps) {
  const [svg, setSvg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [zoomed, setZoomed] = useState(false);

  const baseId = useId().replace(/:/g, '');

  const renderId = useMemo(() => {
    let hash = 0;
    for (let i = 0; i < code.length; i += 1) {
      hash = (hash * 31 + code.charCodeAt(i)) >>> 0;
    }
    return `diagram-${baseId}-${hash.toString(36)}`;
  }, [baseId, code]);

  useEffect(() => {
    if (!initialized) {
      mermaid.initialize({
        startOnLoad: false,
        theme: 'dark',
        securityLevel: 'strict',
        suppressErrorRendering: true,
        flowchart: { htmlLabels: true },
      });
      initialized = true;
    }

    let isMounted = true;
    mermaid
      .render(renderId, code)
      .then(({ svg }) => {
        if (isMounted) {
          setSvg(svg);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err?.message ?? 'Unable to render diagram');
        }
      });

    return () => {
      isMounted = false;
    };
  }, [code, renderId]);

  // Close zoom on Escape
  useEffect(() => {
    if (!zoomed) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setZoomed(false);
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [zoomed]);

  const handleZoom = useCallback(() => setZoomed(true), []);

  if (error) {
    return (
      <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-4">
        <p className="text-xs text-amber-300/70 mb-2">Diagram could not be rendered</p>
        <pre className="rounded-md bg-slate-900/80 p-3 text-xs text-white/70 overflow-x-auto whitespace-pre-wrap font-mono">
          {code}
        </pre>
      </div>
    );
  }

  if (!svg) {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-white/5 bg-white/5 px-3 py-2 text-sm text-white/60">
        Rendering diagram…
      </div>
    );
  }

  return (
    <>
      <div
        className="mermaid-diagram group relative overflow-x-auto rounded-lg border border-white/10 bg-white/5 p-4 cursor-zoom-in hover:border-emerald-500/30 transition-colors"
        onClick={handleZoom}
        title="Click to expand"
      >
        <div dangerouslySetInnerHTML={{ __html: svg }} />
        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity rounded-md bg-slate-800/80 px-2 py-1 flex items-center gap-1 text-[10px] text-white/70 pointer-events-none">
          <ZoomIn size={12} />
          Click to expand
        </div>
      </div>

      {/* Full-screen zoom modal */}
      {zoomed && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
          aria-label="Expanded diagram view"
          onClick={() => setZoomed(false)}
        >
          <button
            onClick={() => setZoomed(false)}
            className="absolute top-4 right-4 rounded-lg bg-slate-800/80 p-2 text-white/80 hover:bg-slate-700 hover:text-white transition z-10"
            aria-label="Close expanded view"
            autoFocus
          >
            <X size={20} />
          </button>
          <div
            className="max-w-[90vw] max-h-[90vh] overflow-auto rounded-xl border border-white/10 bg-slate-900 p-8 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
            dangerouslySetInnerHTML={{ __html: svg }}
          />
        </div>
      )}
    </>
  );
}

