#!/bin/bash
export LMS_API_KEY=my-lms-secret-key-123
export NANOBOT_LMS_API_KEY=my-lms-secret-key-123
cd /root/se-toolkit-lab-8/mcp/mcp-lms
exec uv run python -m mcp_lms http://localhost:42002
