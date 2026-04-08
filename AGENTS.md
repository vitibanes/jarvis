# JARVIS Agent Instructions

## Scope
These instructions apply to the entire repository.

## Development Principles
- Keep OpenRouter request count low; avoid unnecessary LLM loops.
- Prefer deterministic tool execution over additional model calls.
- Ensure retries and fallbacks are explicit, logged, and bounded.
- Keep modules small and practical for MVP maintainability.

## Required Checks
- Backend imports should pass with `python -m compileall backend/app`.
- Frontend should build with `npm run build` in `/frontend` when dependencies are installed.

## Pull Requests
- PR title format: `feat(jarvis): <short summary>`.
- Include sections: Overview, Architecture, Validation, Known Limitations.
