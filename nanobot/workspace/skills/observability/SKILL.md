---
name: observability
description: Use VictoriaLogs and VictoriaTraces MCP tools for system observability
always: true
---

# Observability Skill

This skill enables the agent to investigate system failures using VictoriaLogs and VictoriaTraces.

## Available Tools

The MCP observability server provides these tools:

- `mcp_obs_logs_search` - Search logs by LogsQL query
- `mcp_obs_logs_error_count` - Count errors per service over a time window
- `mcp_obs_traces_list` - List recent traces for a service
- `mcp_obs_traces_get` - Fetch a specific trace by ID

## Usage Strategy

### When the user asks "What went wrong?" or "Check system health"

Follow this investigation flow:

1. **Start with error count** - Call `mcp_obs_logs_error_count` with `minutes=10` to see if there are recent errors
2. **Search for specific errors** - If errors exist, call `mcp_obs_logs_search` with a query like:
   - `_time:10m service.name:"Learning Management Service" severity:ERROR`
3. **Extract trace ID** - From the log results, look for `trace_id` field
4. **Fetch the trace** - Call `mcp_obs_traces_get` with the trace_id to see the full request flow
5. **Summarize findings** - Provide a concise explanation mentioning:
   - What service failed
   - What operation was attempted
   - What error occurred (from logs)
   - Where in the request flow it failed (from traces)

### Example Investigation Flow

**User:** "What went wrong?"

**You:**
1. Call `mcp_obs_logs_error_count({"minutes": 10})` → "Found 5 error(s)"
2. Call `mcp_obs_logs_search({"query": "_time:10m service.name:\"Learning Management Service\" severity:ERROR", "limit": 5})`
3. From logs, extract `trace_id=c470c599021b884282d9598eba80d262`
4. Call `mcp_obs_traces_get({"trace_id": "c470c599021b884282d9598eba80d262"})`
5. Summarize: "The LMS backend failed when querying the database. The db_query operation encountered a connection error to PostgreSQL. The trace shows the request started at auth_success but failed at db_query with 'connection refused'."

### LogsQL Query Tips

Common useful queries:

- Last 10 minutes of errors: `_time:10m severity:ERROR`
- LMS backend errors: `_time:10m service.name:"Learning Management Service" severity:ERROR`
- Specific trace: `trace_id:c470c599021b884282d9598eba80d262`
- All db_query events: `_time:10m event:db_query`

### Response Guidelines

- **Be concise** - Summarize, don't dump raw JSON
- **Mention both logs and traces** - Show you checked both
- **Name the failing service** - e.g., "LMS backend", "PostgreSQL"
- **Name the failing operation** - e.g., "db_query", "auth_check"
- **Include error details** - e.g., "connection refused", "timeout"

## Configuration

The MCP server uses these environment variables:
- `NANOBOT_VICTORIALOGS_URL`: http://victorialogs:9428
- `NANOBOT_VICTORIATRACES_URL`: http://victoriatraces:10428
