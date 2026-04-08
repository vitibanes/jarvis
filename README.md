# JARVIS (OpenRouter-First MVP)

JARVIS is a practical autonomous assistant with controlled planning, persistent memory, tool execution, and observability.
It is intentionally optimized for OpenRouter request efficiency and production-minded reliability.

## 1) Concise implementation plan (execution order)
1. Define modular architecture and folder layout.
2. Implement backend foundation (FastAPI + DB + config).
3. Implement OpenRouter provider abstraction with retries/fallback.
4. Add request tracking, budgeting, and limits.
5. Add layered memory (conversation, summary, factual/task/tool).
6. Add tool registry and guarded tool execution.
7. Add API routes and status/log endpoints.
8. Add dark, minimal frontend console.
9. Add docs, env sample, deployment guidance.

## 2) Architecture
Core flow:
1. Receive user goal.
2. Classify request type (`direct`, `memory`, `tool`, `multi_step`).
3. Skip heavy planning for simple tasks.
4. Retrieve relevant memory only.
5. Execute tool-first when applicable.
6. Call OpenRouter once when possible.
7. Apply retry/fallback policy on provider errors.
8. Persist task, logs, memory, usage records.
9. Return final response and status metadata.

### Components
- **Planner**: lightweight classification and concise steps.
- **Executor**: deterministic tool mapping/execution.
- **Memory manager**: store/retrieve memory and rolling summary.
- **Tool registry**: validated tool calls and structured outputs.
- **OpenRouter client**: normalized errors, retries, fallback across model tiers.
- **Rate limit manager**: minute/day hard controls.
- **Usage tracker**: persistent request counters + usage history.
- **Summarization/caching layer**: rolling summary + memory relevance retrieval.

## 3) Folder structure
```text
/backend
  /app
    /api
    /core
    /agents
    /memory
    /tools
    /providers
    /models
    /services
    /storage
    /utils
    main.py
/frontend
/docs
```

## 4) OpenRouter optimization strategy
- One-call-first behavior per task.
- Deterministic tool-first handling for file/http/command operations.
- Retry only on retryable failures (408/429/502/503).
- Immediate stop on 401/402 (credential/credit issues).
- Model fallback on 404 or exhausted retry path.
- Persistent per-minute and per-day counters.
- Rolling summary to avoid repeatedly sending long histories.

## 5) Request budgeting
Configured through `.env`:
- `MAX_REQUESTS_PER_MINUTE`
- `MAX_REQUESTS_PER_DAY`
- `MAX_RETRIES`
- `MAX_STEPS_PER_TASK`
- `REQUEST_TIMEOUT_SECONDS`

Behavior:
- Task blocked before provider call if hard limit is reached.
- Retries use exponential backoff + jitter.
- Fallback model chain is bounded (primary -> secondary -> tertiary).

## 6) Fallback strategy
Task types map to model tiers:
- `cheap_fast`
- `balanced`
- `reasoning`
- `emergency_free`

Tier model lists are defined by config in code and example YAML in `docs/model_policy.sample.yaml`.

## 7) Memory design
Implemented layers:
1. conversational memory
2. rolling summary memory
3. factual memory (via typed entries)
4. task memory
5. tool result memory

MVP uses lightweight deterministic embeddings for local relevance search and keeps storage SQLite-compatible for easy PostgreSQL migration later.

## 8) Running locally
### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open: `http://localhost:3000`

## 9) Deployment
- Backend: Railway / Render / VPS using `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Frontend: Vercel with `NEXT_PUBLIC_API_BASE` pointing to backend `/api` URL.

## 10) Change models
Update `.env`:
- `PRIMARY_MODEL`
- `SECONDARY_MODEL`
- `TERTIARY_MODEL`

Restart backend.

## 11) Add tools
1. Implement callable in `backend/app/tools/default_tools.py`.
2. Register in `AgentService` tool registry.
3. Ensure structured output and timeout/validation rules.

## 12) Debug failures
- Check `GET /api/status` for usage and provider status.
- Check `GET /api/logs` for step-level events.
- Check `UsageRecord` table for model and error code history.
- Common OpenRouter outcomes:
  - `401`: invalid API key/config.
  - `402`: insufficient credits.
  - `404`: model missing/unavailable -> fallback.
  - `408/429/502/503`: retry/backoff path.

## 13) Simplifications in this MVP
- Lightweight local embedding substitute instead of full FAISS stack to keep setup low-cost and simple.
- Rule-based planner/executor routing to minimize request volume.
- Single backend worker assumptions; for scale use PostgreSQL + Redis locks and distributed counters.
