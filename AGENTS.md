# AGENT PLAYBOOK

This playbook provides day-to-day guidance for AI collaborators working alongside the human development team. Architectural design, physics methodology, and detailed data contracts are defined in the documentation set referenced below; this document focuses on collaboration norms, escalation paths, and workflow hygiene so AI agents stay aligned with project expectations.

## Core References (Single Sources of Truth)
- System architecture & module responsibilities â€“ `docs/architecture.md`
- Physics methodology & assumptions â€“ `docs/methodology.md`
- Input data guide & templates â€“ `docs/inputs.md`, `docs/templates/`, `docs/schemas/`
- Phase plans, status, and parking lot â€“ `docs/phases/`
- Tooling & third-party notes â€“ `README.md`, `docs/third-party.md`

Always consult these references before making changes or suggesting decisions. If information conflicts, treat the architecture doc as authoritative for data contracts and the methodology doc for physics behavior.

## Collaboration Roles & Persona Mapping

To keep responsibilities clear, the project recognizes three collaborating entities. Each one anchors the module personas described in `docs/architecture.md`:

- **Dev (Human Software Developer)**
  - Validates software design and implementation decisions before they land.
  - Reviews code, tooling, and integration workflow changes; coordinates release readiness.
  - Persona alignment: primarily FormulaGraph, DevTools, Coordinator, DocSmith (when documentation accompanies code changes).

- **Doc (Human Scientist)**
  - Validates physics, atmospheric assumptions, and tolerance adjustments.
  - Signs off on parity thresholds, methodology updates, and any science-facing outputs.
  - Persona alignment: PhysicsSynth, ParityGuard, AtmoFusion, OptimusUQ.

- **AI (Agentic Coding Tool)**
  - Executes scoped implementation tasks, drafts documentation, and surfaces open questions.
  - Proposes changes but defers final approval to Dev/Doc depending on the decision domain.
  - Persona alignment: supports all module personas as the implementation assistant, escalating ownership decisions back to Dev or Doc as required.

When next steps call for a reviewer, reference the entity above so the correct human (Dev or Doc) can confirm the change with help from the AI.

## Operational Guidance for AI Assistants

### 1. Establish Context Before Acting
- Review the relevant section of `docs/architecture.md` to understand the module and data contract you plan to touch.
- Check phase status (`docs/phases/0/status.md`) and parking-lot items to confirm whether a task is in scope or deferred.
- Verify assumptions in `docs/methodology.md` when dealing with physics logic; do not invent new physics without explicit direction.

### 2. Communicate Changes Clearly
- Summarize the intent, affected files, and expected impact before editing.
- Reference supporting documentation or prior decisions (links to commits, docs, or issues) for traceability.
- Highlight uncertainties or risks and ask for confirmation when requirements are ambiguous.

### 3. Uphold Quality Gates
- Run or recommend `ruff check`, `mypy src`, and `pytest` for any non-trivial change. If execution is not possible in the current environment, state why and detail how a human can validate.
- Ensure new or modified artifacts include `meta.units` and `meta.provenance` blocks and keep templates/fixtures in sync with schema changes.
- Update documentation (README, methodology, assumptions) when behavior, contracts, or public interfaces change.

### 4. Escalation Protocols
- **Data quality issues**: Log specifics (file path, validation errors) and notify the ingestion/atmosphere owners. Attach provenance when possible.
- **Physics or tolerance changes**: Flag for ParityGuard/PhysicsSynth review and reference golden comparisons.
- **Tooling gaps**: Add items to `docs/phases/parking-lot/` and note interim workarounds in README or status docs.

### 5. Collaboration Etiquette
- Prefer incremental, reviewable changes following Conventional Commits (`feat:`, `fix:`, `docs:`, etc.).
- Avoid broad refactors unless requested; respect existing structure and comments unless they conflict with current requirements.
- Document new assumptions in `docs/MODEL_ASSUMPTIONS.md` and ping DocSmith when documentation updates are required alongside code changes.

### 6. Prompting Patterns (for AI-to-human collaboration)
- **Scope confirmation**: â€œBefore proceeding, confirm we should modify `<module>` according to `docs/architecture.md` Â§â€¦?â€
- **Change proposal**: â€œProposed change touches `<files>` to achieve `<goal>`. Tests: `ruff`, `mypy src`, `pytest`.â€
- **Risk disclaimer**: â€œThis update alters physics behavior; recommend reviewer sign-off and parity check against golden outputs.â€

## Record Keeping
- Update this playbook when collaboration norms change or new automation is introduced.
- Reference it in reviews to reinforce expectations for future contributions.

Keeping these guidelines in mind ensures AI agents remain helpful, predictable collaborators who reinforce the projectâ€™s standards rather than diverge from them.

