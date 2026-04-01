#!/bin/bash
cd /root/se-toolkit-lab-8/mcp/mcp-lms
exec uv run python -c "
import asyncio
from mcp_lms.server import main
asyncio.run(main('http://localhost:42002'))
"
