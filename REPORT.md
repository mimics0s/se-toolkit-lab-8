# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

**Q: "What is the agentic loop?"**

The agentic loop refers to a fundamental concept in artificial intelligence and robotics where an agent continuously perceives its environment, makes decisions based on those perceptions, takes actions, and observes the outcomes of those actions. This cycle repeats, allowing the agent to learn and adapt over time.

In essence, the agentic loop involves four main components:

1. **Perception**: The agent senses its environment through sensors or data inputs.
2. **Decision Making**: Based on the perceived information, the agent evaluates options and decides what action to take.
3. **Action**: The agent executes the chosen action in the environment.
4. **Observation**: The agent observes the results of its action and updates its understanding of the environment.

This iterative process enables agents to interact with their surroundings intelligently, learning from experience and improving their performance over time.

**Q: "What labs are available in our LMS?" (before MCP configured)**

Based on what I can observe in the system, I can see there's at least one lab directory (lab-1) in the wiki, but I don't have direct access to the LMS API or tools to query the available labs.

Since I cannot directly access the LMS backend to retrieve the list of available labs, and the LMS tools aren't properly exposed in this environment, I'll need to work with what I can see in the filesystem.

From my exploration, I can see:

1. There's a lab-1 directory in the wiki
2. There's an LMS MCP implementation in /root/se-toolkit-lab-8/mcp/mcp-lms/
3. There's an .env.docker.secret file with LMS API key configuration
4. The system appears to be set up for LMS integration

However, without being able to directly query the LMS API or access the proper MCP tools, I cannot provide you with the exact list of available labs from the LMS system.

## Task 1B — Agent with LMS tools

**Q: "What labs are available?"**

Here are the available labs:

1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. lab-08

**Q: "Is the LMS backend healthy?"**

"Yes, the LMS backend is healthy. It reports a total of 56 items in the system."

## Task 1C — Skill prompt

**Q: "Show me the scores" (without specifying a lab)**

I'll get the scores for you. Since there are multiple labs, could you please specify which lab's scores you'd like to see? Here are the available labs:

1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. lab-08

Please let me know which one you're interested in.

## Task 2A — Deployed agent

Nanobot gateway startup log excerpt:

```
🐈 Starting nanobot gateway version 0.1.4.post5 on port 18790...
✓ Channels enabled: webchat
✓ Heartbeat: every 1800s
2026-04-01 17:06:27.456 | INFO | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'lms': connected, 9 tools registered
2026-04-01 17:06:29.507 | INFO | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'webchat': connected, 1 tools registered
2026-04-01 17:06:29.507 | INFO | nanobot.agent.loop:run:280 - Agent loop started
```

Services running:
- `nanobot` - Up (gateway mode)
- `client-web-flutter` - Built and volume mounted
- `caddy` - Proxying `/ws/chat` and `/flutter`

## Task 2B — Web client

WebSocket endpoint test (via Python):

```
$ echo '{"content":"What labs are available?"}' | websocat "ws://localhost:42002/ws/chat?access_key=my-nanobot-password-456"

{"type":"text","content":"Here are the available labs:

1. **Lab 01** – Products, Architecture & Roles
2. **Lab 02** — Run, Fix, and Deploy a Backend Service
3. **Lab 03** — Backend API: Explore, Debug, Implement, Deploy
4. **Lab 04** — Testing, Front-end, and AI Agents
5. **Lab 05** — Data Pipeline and Analytics Dashboard
6. **Lab 06** — Build Your Own Agent
7. **Lab 07** — Build a Client with an AI Coding Agent
8. **Lab 08** — lab-08

Is there a specific lab you'd like to explore?...","format":"markdown"}
```

Flutter client:
- Accessible at `http://localhost:42002/flutter`
- Login protected by `NANOBOT_ACCESS_KEY=my-nanobot-password-456`
- WebSocket route `/ws/chat` proxied through Caddy

## Task 3A — Structured logging

**Structured logs from VictoriaLogs (JSON format)**

**Happy-path log entry** (trace_id: `ead0f10049eaa9b8bf453168824e5d90`):

```json
{
  "_msg": "request_started",
  "_time": "2026-04-01T18:40:53.499018752Z",
  "event": "request_started",
  "method": "GET",
  "path": "/items/",
  "service.name": "Learning Management Service",
  "severity": "INFO",
  "trace_id": "ead0f10049eaa9b8bf453168824e5d90",
  "span_id": "80b3067d8a7cb4f3",
  "otelTraceID": "ead0f10049eaa9b8bf453168824e5d90",
  "otelSpanID": "80b3067d8a7cb4f3"
}
```

The happy-path request shows the complete flow with `severity: INFO` and `status: 200`:
- `request_started` → `auth_success` → `db_query` → `request_completed`

**Error-path log entry** (trace_id: `c470c599021b884282d9598eba80d262`):

```json
{
  "_msg": "db_query",
  "_time": "2026-04-01T18:08:40.178516992Z",
  "error": "(sqlalchemy.dialects.postgresql.asyncpg.InterfaceError) <class 'asyncpg.exceptions._base.InterfaceError'>: connection is closed",
  "event": "db_query",
  "operation": "select",
  "service.name": "Learning Management Service",
  "severity": "ERROR",
  "trace_id": "c470c599021b884282d9598eba80d262",
  "span_id": "19875ef92b6c39af",
  "table": "item"
}
```

The error-path shows `severity: ERROR` with the `error` field containing the database connection failure.

**Key structured log fields:**
- `service.name`: "Learning Management Service"
- `severity`: "INFO" or "ERROR"
- `event`: request_started, auth_success, db_query, request_completed
- `trace_id`: links to distributed traces (e.g., `ead0f10049eaa9b8bf453168824e5d90`)
- `span_id`: individual span within a trace
- `error`: contains the actual error message (only on ERROR severity)
- `otelTraceID` / `otelSpanID`: OpenTelemetry trace/span identifiers

**VictoriaLogs query:**

Query used: `_time:1h service.name:"Learning Management Service" severity:ERROR`

Raw logs saved to:
- `lab/screenshots/task-3a-logs-raw.json` (healthy requests)
- `lab/screenshots/task-3a-errors-raw.json` (error requests)

---

## Task 3B — Traces

**Healthy trace** (trace_id: `ead0f10049eaa9b8bf453168824e5d90`):

Span hierarchy:
```
GET /items/ (404ms, status 200)
├── connect (298ms) - PostgreSQL connection
├── SELECT db-lab-8 (48ms) - Database query
└── GET /items/ http send (67μs + 42μs + 30μs) - Response sending
```

**Error trace** (trace_id: `91bf443ad7ffad65c08a717526d2ad29`):

Span hierarchy showing failure:
```
GET /items/ (699ms, status 404)
├── connect (689ms) - FAILED with error
│   └── Exception: socket.gaierror: [Errno -2] Name or service not known
└── GET /items/ http send (83μs + 41μs + 59μs) - Error response
```

Raw traces saved to: `lab/screenshots/task-3b-traces-raw.json`

The error trace shows the `connect` span failed with a DNS resolution error when PostgreSQL was stopped, causing the entire request to fail with a 404 status.

---

## Task 3C — Observability MCP tools

**MCP tools registered:**
- `mcp_obs_logs_search` — search logs by LogsQL query
- `mcp_obs_logs_error_count` — count errors per service over a time window
- `mcp_obs_traces_list` — list recent traces for a service
- `mcp_obs_traces_get` — fetch a specific trace by ID

**Agent response under normal conditions:**

Q: "Any LMS backend errors in the last 10 minutes?"

> "Good news! **No LMS backend errors** in the last 10 minutes. The Learning Management Service has been running cleanly."

**Agent response under failure conditions (PostgreSQL stopped):**

Q: "Any LMS backend errors in the last 10 minutes?"

> "Yes, there are **3 errors** in the LMS backend in the last 10 minutes. All are database connectivity issues..."

The agent correctly:
1. Called `mcp_obs_logs_error_count` to check for recent errors
2. Called `mcp_obs_logs_search` to retrieve error details
3. Summarized findings concisely without dumping raw JSON

## Task 4A — Multi-step investigation

**Agent investigation flow when asked "The LMS backend is failing. What went wrong?"**

The agent chained multiple observability tools:

1. `mcp_lms_lms_health()` - Checked backend health status
2. `mcp_obs_logs_search()` - Searched error logs for LMS backend
3. `mcp_obs_traces_list()` - Listed recent traces for the service
4. `mcp_obs_traces_get()` - Fetched specific trace to analyze failure

**Agent's response:**

```
## Root Cause: Database Connection Failure

The LMS backend is failing due to a **DNS resolution error** when trying to connect to the PostgreSQL database.

**Error:** `socket.gaierror: [Errno -2] Name or service not known`

**What's happening:**
1. ✅ The backend successfully fetches items from the external API
2. ❌ It then fails when trying to connect to the PostgreSQL database

**Database connection attempt:**
- Host: `postgres`
- Port: `5432`
- Database: `db-lab-8`
- User: `postgres`

### Likely Causes

1. **PostgreSQL container is not running**
2. **Network isolation** - The LMS backend container cannot reach the `postgres` hostname
3. **Service name mismatch** - The actual database service might have a different hostname

### Recommended Actions

1. **Check if PostgreSQL is running:**
   ```bash
   docker ps | grep postgres
   ```

2. **Verify Docker network connectivity**

3. **Check the DATABASE_URL environment variable**

4. **Restart the database service** if it's stopped
```

The agent successfully:
- Identified the failing service (LMS backend)
- Named the root cause (DNS resolution failure to PostgreSQL)
- Cited evidence from both logs and traces
- Provided actionable remediation steps

---

## Task 4B — Proactive health check

**Cron job created:**

```
Job ID: 7dce20af
Schedule: Every 2 minutes
Task: Health check - Check for LMS/backend errors in the last 2 minutes using mcp_obs_logs_error_count.
      If errors found, inspect recent traces with mcp_obs_traces_get and post a short summary.
```

**Agent confirmed the job:**

```
You have **1 scheduled job**:

| Job ID | Description | Schedule | Next Run |
|--------|-------------|----------|----------|
| 7dce20af | Health check: Check for LMS/ba | Every 2 minutes | 2026-04-01 19:03:43 UTC |
```

**Proactive health report (while PostgreSQL was stopped):**

```
**🏥 Health Check Report** ✅

The system looks healthy. No errors were found in the last 2 minutes across all services...
```

Note: The health check reported "healthy" because the database failure occurred more than 2 minutes before the cron run. The check correctly looks for *new* errors in the rolling window.

**Nanobot logs showing cron execution:**

```
2026-04-01 19:03:43.610 | INFO | nanobot.cron.service:_execute_job:268 - Cron: executing job 'Health check: Check for LMS/ba' (7dce20af)
2026-04-01 19:03:47.573 | INFO | nanobot.agent.loop:_prepare_tools:253 - Tool call: mcp_obs_logs_error_count({"minutes": 2, "service": "Learning Management Service"})
2026-04-01 19:03:53.574 | INFO | nanobot.agent.loop:_process_message:479 - Response to webchat:user: **Health Check Report** ✅
```

---

## Task 4C — Bug fix and recovery

### 1. Root Cause Identified

**Planted bug location:** `backend/src/lms_backend/routers/items.py`

**The bug:** The `get_items` endpoint caught all exceptions and raised a misleading `404 "Items not found"` instead of properly reporting database failures:

```python
# BEFORE (buggy code)
@router.get("/", response_model=list[ItemRecord])
async def get_items(session: AsyncSession = Depends(get_session)):
    """Get all items."""
    try:
        return await read_items(session)
    except Exception as exc:
        logger.warning(
            "items_list_failed_as_not_found",
            extra={"event": "items_list_failed_as_not_found"},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Items not found",
        ) from exc  # ← Misleading 404 for database failures
```

### 2. Fix Applied

Changed the error handler to:
- Log at ERROR level (not WARNING)
- Return HTTP 500 (not 404) for database failures
- Include the actual error message in the response

```python
# AFTER (fixed code)
@router.get("/", response_model=list[ItemRecord])
async def get_items(session: AsyncSession = Depends(get_session)):
    """Get all items."""
    try:
        return await read_items(session)
    except Exception as exc:
        logger.error(
            "items_list_failed",
            extra={"event": "items_list_failed", "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(exc)}",
        ) from exc  # ← Proper 500 with actual error
```

### 3. Post-fix Failure Check

After redeploying, triggered the failure again (PostgreSQL stopped):

**Agent response:**

```
The LMS backend is currently experiencing issues. All endpoints are returning HTTP 500 Internal Server Error...

## Root Cause: Database Connection Failure

The LMS backend is failing due to a **DNS resolution error** when trying to connect to the PostgreSQL database.

**Error:** `socket.gaierror: [Errno -2] Name or service not known`
```

The agent now correctly reports:
- HTTP 500 status (not misleading 404)
- The actual database connection error
- Proper root cause analysis

### 4. Healthy Follow-up

After restarting PostgreSQL, verified recovery:

**Agent response to "Is the LMS backend healthy now?":**

```
Yes, the LMS backend is healthy! ✅

- **Status**: Healthy
- **Item count**: 56 items
- **Errors**: None

Everything is running smoothly.
```
