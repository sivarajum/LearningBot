# Container Registry Roadmap – 4 Weeks (GCR; prefer AR for new builds)

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Configure Docker auth; push/pull test image
- [ ] Day 2: Understand hostnames (gcr.io/us/eu/asia)
- [ ] Day 3: IAM for images; least privilege
- [ ] Day 4: Tagging vs digests; avoid latest
- [ ] Day 5: Cleanup basics: list/delete images
- [ ] Day 6: Mini-project: push app image + pull in GKE/Run
- [ ] Day 7: Review + tighten IAM
- [ ] Day 8: Cost awareness; storage/location
- [ ] Day 9-10: Migration plan outline to Artifact Registry
- [ ] Day 11-14: Refactor manifests to use digests

**Milestone**: Secure push/pull with proper tagging and IAM.

## Weeks 3-4: Intermediate/Advanced (🟡/🔴)
- [ ] Day 15: Image signing (cosign); SBOM (syft)
- [ ] Day 16: Scanning (via AR or external scanner)
- [ ] Day 17: Cleanup scripts for old tags/digests
- [ ] Day 18: WIF for CI; short-lived creds
- [ ] Day 19: Binary Authorization policy (if GKE)
- [ ] Day 20: Dual-publish to AR; cutover plan
- [ ] Day 21-22: Mini-project: signed, scanned image pipeline
- [ ] Day 23-24: Audit logs review; alerts on failed pulls
- [ ] Day 25-28: Capstone: migrate to AR with policy/cleanup

**Milestone**: Signed/scanned images, cleanup in place, AR migration path.

## Resources
- GCR docs: https://cloud.google.com/container-registry/docs
- Prefer AR: https://cloud.google.com/artifact-registry/docs
- Cosign: https://github.com/sigstore/cosign

