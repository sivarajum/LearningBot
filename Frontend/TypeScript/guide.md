# TypeScript Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. Quick Setup
```bash
npm init -y
npm install --save-dev typescript ts-node @types/node
npx tsc --init
```

### 2. Core Types
- Primitives: string, number, boolean, null/undefined
- Arrays/tuples, enums, unions, intersections
- Type aliases vs interfaces; structural typing

### 3. Functions
- Typed params/returns; optional/default; rest params
- Narrowing (typeof, in, instanceof); control flow analysis

## Level 2 – Production Patterns

### Generics & Utility Types
- Generics for reusable components/functions
- Utility types: Partial, Pick, Omit, Record, ReturnType
- Discriminated unions for safe variants

### Modules & Tooling
- Path aliases; tsconfig targets/lib/moduleResolution
- ESLint + Prettier; strict mode on
- Declarations: ambient types, @types packages

### Working with APIs
- Typed fetch wrappers; DTOs; zod/yup runtime validation
- Avoid `any`; use unknown + narrowing

## Level 3 – Architect Playbook

### Large Codebases
- Enforce strictNullChecks, noImplicitAny
- Public API surface via barrels; limit deep imports
- Domain-driven typing; branded types for IDs

### Performance & Build
- IsolatedModules for faster builds; incremental/TSBuildInfo
- Project references for monorepos
- Emit targets (ES2020+), module=ESNext for bundlers

### Safety & DX
- Exhausitve switch on discriminated unions
- Lint rules to ban implicit any/namespace/misused promises
- JSDoc for library exports; d.ts packaging for SDKs

## Ops Cheat Sheet

| Task | Command | Note |
| --- | --- | --- |
| Init | `npx tsc --init` | tsconfig |
| Build | `npx tsc -p tsconfig.json` | emit |
| Check | `npx tsc --noEmit` | typecheck |
| Lint | `npm run lint` | if configured |

## Architecture Patterns

```mermaid
flowchart LR
  Domain[Domain Types] --> Services[Services]
  Services --> API[API Layer]
  API --> UI[UI/Clients]
  Domain --> Validation[Runtime Validation (zod)]
  Services --> Tests[Tests]
```

## Checklist Before Production
- [ ] strict mode on; noImplicitAny/strictNullChecks enabled
- [ ] Lint + format in CI; typecheck with --noEmit
- [ ] DTOs typed; runtime validation at boundaries
- [ ] Barrel exports; avoid deep relative imports
- [ ] Project references for large repos; incremental builds

