# MANGO Recruiter Scorecard

Review date: 2026-09-06  
Release candidate: pending final CI rerun  
Decision standard: every category must score at least 4/5, total at least 26/30, and no unresolved critical defect.

## Score

| Category | Score | Recruiter judgment | Evidence |
| --- | ---: | --- | --- |
| Correctness and functionality | 4.5/5 | Core retrieval contracts are now consistent; input failures are explicit. | 11 API/vector tests and 5 hosted-search tests pass locally. |
| Architecture and data contracts | 4.5/5 | Clear boundary between deployable showcase, model API, vector index, and monitoring. | Typed FastAPI request models, safe image root, idempotent path index, documented request flow. |
| Code quality and security | 4.5/5 | Small modules, pinned dependencies, no unsafe file traversal, no known dependency advisories. | `npm audit` and `pip-audit` both report zero known vulnerabilities. |
| Testing and reproducibility | 4.0/5 | Strong unit coverage and deterministic test doubles; full CLIP weight smoke test remains manual because it is resource-heavy. | Local backend and frontend suites pass; Docker Compose validation runs in CI. |
| UI, accessibility, and product judgment | 4.5/5 | Distinctive, restrained editorial direction with a clear search-first task flow. | Responsive grid, semantic controls, visible focus, reduced motion, empty states, image dialog, local assets. |
| Documentation and deployment readiness | 4.5/5 | Claims are explicit about hosted concept search versus local CLIP inference. | Live Vercel URL, architecture diagrams, API contract, quick start, limitations, social preview, MIT license. |

**Total: 26.5/30 — MANGO bar met provisionally.**

## Critical-defect gate

- No known critical defects in the implementation.
- Final approval is withheld until the corrected Python 3.11 dependency set passes GitHub Actions.

## Recruiter critique

### What makes this interview-ready

- The repository tells one coherent story from product need to technical design.
- The hosted experience can be understood and used immediately without setup.
- The code avoids claiming that a static Vercel page runs a heavyweight CLIP model.
- Retrieval behavior, validation, indexing, observability, and failure states have direct evidence.

### Honest limitations

- The CLIP weights are not downloaded in CI; an end-to-end model smoke test is a documented manual gate.
- The index is process-local and intentionally unsuitable for multi-instance production serving.
- The hosted collection is intentionally small and should not be presented as a benchmark.

### Next investment if this became a product

Add authenticated object storage, queued GPU-backed ingestion, a persistent pgvector/FAISS index, evaluation datasets, and relevance metrics before calling the system production-scale.

## French design review

- The page gives the primary action visual authority without turning into a marketing splash screen.
- Serif display type, restrained cobalt and chartreuse accents, fine rules, and asymmetrical image rhythm make the product memorable without harming clarity.
- Filters, suggested prompts, result counts, match labels, and the detail view make the search flow self-explanatory.
- Mobile controls remain touch-friendly, the layout reduces cleanly to two columns, and motion respects the user's reduced-motion preference.
