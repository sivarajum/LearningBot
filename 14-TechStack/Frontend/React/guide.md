# React Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. Quick Setup
```bash
npx create-react-app demo --template typescript
cd demo && npm start
```

### 2. Core Concepts
- Components (function), JSX, props, state
- Hooks: useState, useEffect, useMemo, useCallback
- Rendering: reconciliation, keys, conditional rendering

### 3. First Component
```tsx
function Counter() {
  const [count, setCount] = useState(0);
  return (
    <button onClick={() => setCount(c => c + 1)}>
      Count: {count}
    </button>
  );
}
```

## Level 2 – Production Patterns

### State & Data
- Lift state thoughtfully; context for cross-cutting state
- Server data: SWR/React Query; caching, mutations, retries
- Forms: react-hook-form or Formik; validation with Zod/Yup

### Routing & Code Split
- React Router with data APIs or Next.js app router
- Dynamic import with Suspense; route-level split

### Styling & Theming
- CSS-in-JS (emotion/styled-components) or CSS modules
- Design systems; consistent spacing/typography

## Level 3 – Architect Playbook

### Performance
- Memoize hot paths; avoid prop-drilling with context selectors
- Virtualize large lists (react-window)
- Defer non-critical work (useTransition/useDeferredValue)

### Reliability & Observability
- Error boundaries; Suspense fallbacks
- Logging/metrics: wrap fetch; capture errors; web vitals

### Architecture
- Feature-driven folder structure; co-locate tests/stories
- Env management; build-time vs runtime config

## Ops Cheat Sheet

| Task | Command | Note |
| --- | --- | --- |
| Dev server | `npm start` | local dev |
| Build | `npm run build` | prod bundle |
| Lint | `npm run lint` | quality |
| Test | `npm test -- --watch=false` | CI |

## Architecture Patterns

```mermaid
flowchart LR
  UI[UI Components] --> State[State/Cache (React Query)]
  UI --> Router[Router]
  Router --> Pages[Pages/Layouts]
  State --> API[API Client/Fetch Wrapper]
  API --> Backend[Backend Services]
  UI --> Design[Design System]
```

## Checklist Before Production
- [ ] Lint/format/tests enforced in CI
- [ ] Error boundaries + Suspense fallbacks
- [ ] Data fetching with caching/retries; loading states
- [ ] Code splitting on routes/heavy components
- [ ] Env config handled safely; no secrets in bundle
- [ ] Web vitals monitoring; logging for errors

