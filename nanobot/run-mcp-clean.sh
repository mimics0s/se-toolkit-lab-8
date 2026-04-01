#!/bin/bash
cd /root/se-toolkit-lab-8/mcp/mcp-lms
export LMS_API_KEY=my-lms-secret-key-123
exec uv run python -m mcp_lms http://localhost:42002
