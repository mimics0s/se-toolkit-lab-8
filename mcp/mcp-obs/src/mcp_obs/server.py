"""MCP server for observability tools (VictoriaLogs and VictoriaTraces)."""

import asyncio
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


def create_server() -> Server:
    """Create the MCP observability server."""
    server = Server("mcp-obs")

    # Get configuration from environment
    victorialogs_url = os.environ.get("NANOBOT_VICTORIALOGS_URL", "http://victorialogs:9428")
    victoriatraces_url = os.environ.get("NANOBOT_VICTORIATRACES_URL", "http://victoriatraces:10428")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available observability tools."""
        return [
            Tool(
                name="logs_search",
                description="Search VictoriaLogs by LogsQL query. Returns matching log entries.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "LogsQL query (e.g., '_time:10m service.name:\"Learning Management Service\" severity:ERROR')"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 20
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="logs_error_count",
                description="Count errors per service over a time window. Returns error counts grouped by service.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "minutes": {
                            "type": "integer",
                            "description": "Time window in minutes",
                            "default": 60
                        },
                        "service": {
                            "type": "string",
                            "description": "Filter by service name (optional)"
                        }
                    }
                }
            ),
            Tool(
                name="traces_list",
                description="List recent traces for a service from VictoriaTraces.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service": {
                            "type": "string",
                            "description": "Service name to filter traces"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of traces to return",
                            "default": 10
                        }
                    },
                    "required": ["service"]
                }
            ),
            Tool(
                name="traces_get",
                description="Fetch a specific trace by ID from VictoriaTraces. Returns full trace with all spans.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "trace_id": {
                            "type": "string",
                            "description": "Trace ID (hex string, e.g., 'c470c599021b884282d9598eba80d262')"
                        }
                    },
                    "required": ["trace_id"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute an observability tool."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            if name == "logs_search":
                query = arguments.get("query", "")
                limit = arguments.get("limit", 20)
                
                # VictoriaLogs LogsQL query API
                url = f"{victorialogs_url}/select/logsql/query"
                params = {"query": query, "limit": limit}
                
                response = await client.post(url, params=params)
                response.raise_for_status()
                
                # VictoriaLogs returns JSONL or JSON depending on request
                try:
                    result = response.json()
                except:
                    result = response.text
                
                return [TextContent(type="text", text=f"Logs search results:\n{result}")]

            elif name == "logs_error_count":
                minutes = arguments.get("minutes", 60)
                service = arguments.get("service")
                
                # Build LogsQL query for error count
                time_filter = f"_time:{minutes}m"
                severity_filter = "severity:ERROR"
                service_filter = f'service.name:"{service}"' if service else ""
                query = f"{time_filter} {severity_filter} {service_filter}".strip()
                
                url = f"{victorialogs_url}/select/logsql/query"
                params = {"query": query, "limit": 1000}
                
                response = await client.post(url, params=params)
                response.raise_for_status()
                
                try:
                    logs = response.json()
                    # Count errors
                    if isinstance(logs, list):
                        error_count = len(logs)
                    else:
                        error_count = 0
                except:
                    error_count = 0
                
                return [TextContent(type="text", text=f"Found {error_count} error(s) in the last {minutes} minutes")]

            elif name == "traces_list":
                service = arguments.get("service", "")
                limit = arguments.get("limit", 10)
                
                # VictoriaTraces Jaeger-compatible API
                url = f"{victoriatraces_url}/select/jaeger/api/traces"
                params = {"service": service, "limit": limit}
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                result = response.json()
                
                # Extract summary info
                traces_summary = []
                if isinstance(result, dict) and "data" in result:
                    for trace in result["data"][:limit]:
                        trace_id = trace.get("traceID", "unknown")
                        spans = trace.get("spans", [])
                        span_count = len(spans)
                        # Get trace start time
                        start_time = spans[0].get("startTime", 0) if spans else 0
                        traces_summary.append({
                            "trace_id": trace_id,
                            "span_count": span_count,
                            "start_time": start_time
                        })
                
                return [TextContent(type="text", text=f"Recent traces for '{service}':\n{traces_summary}")]

            elif name == "traces_get":
                trace_id = arguments.get("trace_id", "")
                
                # VictoriaTraces Jaeger-compatible API for single trace
                url = f"{victoriatraces_url}/select/jaeger/api/traces/{trace_id}"
                
                response = await client.get(url)
                response.raise_for_status()
                
                result = response.json()
                
                # Extract trace summary
                if isinstance(result, dict) and "data" in result:
                    trace_data = result["data"]
                    if isinstance(trace_data, list) and len(trace_data) > 0:
                        trace = trace_data[0]
                        spans = trace.get("spans", [])
                        span_summary = []
                        for span in spans:
                            span_summary.append({
                                "span_id": span.get("spanID"),
                                "operation_name": span.get("operationName"),
                                "service_name": span.get("process", {}).get("serviceName"),
                                "duration": span.get("duration"),
                                "tags": span.get("tags", [])
                            })
                        return [TextContent(type="text", text=f"Trace {trace_id}:\n{span_summary}")]
                
                return [TextContent(type="text", text=f"Trace {trace_id} not found or empty")]

            else:
                raise ValueError(f"Unknown tool: {name}")

    return server


def main():
    """Run the MCP observability server."""
    server = create_server()
    
    async def run_server():
        async with stdio_server() as (read_stream, write_stream):
            init_options = server.create_initialization_options()
            await server.run(read_stream, write_stream, init_options)
    
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
