# Docker Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Install Docker, run hello-world
- [ ] Day 2: Images vs containers, common CLI (`ps`, `logs`, `exec`)
- [ ] Day 3: Dockerfile basics (FROM, RUN, COPY, CMD)
- [ ] Day 4: Build/run a simple web app image
- [ ] Day 5: Volumes vs bind mounts; persist data
- [ ] Day 6: Networking (bridge/host), port publishing
- [ ] Day 7: Clean up and review
- [ ] Day 8: .dockerignore and cache basics
- [ ] Day 9: Multi-stage builds intro
- [ ] Day 10: Push/pull to a registry (Docker Hub)
- [ ] Day 11: Environment variables and secrets handling
- [ ] Day 12: Healthchecks and restart policies
- [ ] Day 13: Logging to stdout/stderr; log drivers overview
- [ ] Day 14: Mini-project: containerize a 2-service app

**Milestone**: Comfortable building/running/shipping images; basic hygiene.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Compose v2 basics; define multi-service stack
- [ ] Day 16: Compose env files, profiles, depends_on
- [ ] Day 17: Multi-stage optimization; smaller images
- [ ] Day 18: Caching strategies; deterministic builds
- [ ] Day 19: Debugging containers (exec, nsenter)
- [ ] Day 20: Resource limits (CPU/mem), ulimits
- [ ] Day 21: Docker Buildx and multi-arch builds
- [ ] Day 22: Private registries (ECR/GCR/ACR/GHCR)
- [ ] Day 23: Tagging strategy and immutability
- [ ] Day 24: Intro to security scanning (trivy, docker scan)
- [ ] Day 25: SBOM generation (syft)
- [ ] Day 26: Signing images (cosign) and verification
- [ ] Day 27: Compose for local dev (hot reload + volumes)
- [ ] Day 28: Mini-project: compose stack with db + app + worker

**Milestone**: Production-ready images, compose proficiency, registry usage.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: CI/CD pipeline: build, test, scan, push
- [ ] Day 30: Policy enforcement gates on scan/sign
- [ ] Day 31: Supply chain: provenance + attestations (SLSA basics)
- [ ] Day 32: Runtime security: non-root, seccomp, capabilities
- [ ] Day 33: Performance tuning: layered FS, caching, registry mirrors
- [ ] Day 34: Observability patterns (logs/stdout, metrics sidecars)
- [ ] Day 35: Multi-arch publishing strategy
- [ ] Day 36: Promotion flow: dev → stage → prod via tags/digests
- [ ] Day 37: Disaster recovery: backups of registries, restore drills
- [ ] Day 38: Cost controls: registry retention, cache policies
- [ ] Day 39: Governance checklist; docs and runbooks
- [ ] Day 40-42: Capstone: secure, signed, multi-arch app with CI/CD

**Milestone**: Secure supply chain, automated CI/CD, documented operations.

## Resources
- Official docs: https://docs.docker.com/
- Dockerfile best practices: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- Buildx: https://docs.docker.com/build/buildx/
- Compose: https://docs.docker.com/compose/

