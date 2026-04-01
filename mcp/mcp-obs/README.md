# mcp-obs

MCP server for observability tools (VictoriaLogs and VictoriaTraces).

## Tools

- `logs_search` - Search VictoriaLogs by LogsQL query
- `logs_error_count` - Count errors per service over a time window
- `traces_list` - List recent traces for a service
- `traces_get` - Fetch a specific trace by ID

## Usage

```bash
python -m mcp_obs
```

## Configuration

Environment variables:
- `NANOBOT_VICTORIALOGS_URL` - VictoriaLogs URL (default: http://victorialogs:9428)
- `NANOBOT_VICTORIATRACES_URL` - VictoriaTraces URL (default: http://victoriatraces:10428)
