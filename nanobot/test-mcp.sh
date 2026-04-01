#!/bin/bash
echo "Starting MCP server..."
export LMS_API_KEY=my-lms-secret-key-123
cd /root/se-toolkit-lab-8/mcp/mcp-lms
exec uv run python -m mcp_lms http://localhost:42002
