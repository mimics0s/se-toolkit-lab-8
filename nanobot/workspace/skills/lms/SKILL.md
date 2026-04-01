---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

This skill enables the agent to query the LMS backend for labs, items, scores, and other data.

## Available Tools

The LMS MCP server provides these tools:

- `mcp_lms_lms_health` - Check backend health and get item count
- `mcp_lms_lms_labs` - Get all available labs
- `mcp_lms_lms_pass_rates` - Get pass rates for a specific lab
- `mcp_lms_lms_scores` - Get scores for a lab or group
- `mcp_lms_lms_timeline` - Get timeline data for a lab
- `mcp_lms_lms_groups` - Get group information
- `mcp_lms_lms_top_learners` - Get top learners for a lab
- `mcp_lms_lms_completion_rate` - Get completion rate for a lab
- `mcp_lms_lms_learners` - Get learner information
- `mcp_lms_lms_sync_pipeline` - Trigger LMS data sync

## Usage Strategy

### General Rules

- **Always use real tool responses** - never hallucinate data
- **Format numeric results nicely** - show percentages as "85%" not "0.85", include counts
- **Keep responses concise** - summarize data, don't dump raw JSON
- **When the user asks "what can you do?"** - explain your LMS tools and limits clearly

### Handling Lab Parameters

Many tools require a `lab_id` parameter. Follow this strategy:

1. **If the user asks for scores, pass rates, completion, groups, timeline, or top learners WITHOUT naming a lab:**
   - First call `mcp_lms_lms_labs` to get available labs
   - If multiple labs exist, ask the user to choose one
   - Use each lab's `title` field as the user-facing label when presenting choices

2. **If the user provides a lab name or ID:**
   - Use it directly with the appropriate tool
   - If the tool fails, try calling `mcp_lms_labs` to find the correct lab_id

### Tool Selection Guide

| User asks for... | Call this tool first |
|------------------|---------------------|
| "What labs exist?" | `mcp_lms_lms_labs` |
| "Is backend working?" | `mcp_lms_lms_health` |
| "Scores" / "How did students do?" | `mcp_lms_lms_scores` (ask for lab if not provided) |
| "Pass rate" | `mcp_lms_lms_pass_rates` (ask for lab if not provided) |
| "Timeline" / "When is it due?" | `mcp_lms_lms_timeline` (ask for lab if not provided) |
| "Groups" | `mcp_lms_lms_groups` (ask for lab if not provided) |
| "Top students" | `mcp_lms_lms_top_learners` (ask for lab if not provided) |
| "Completion rate" | `mcp_lms_lms_completion_rate` (ask for lab if not provided) |
| "No data" / "Sync data" | `mcp_lms_lms_sync_pipeline` |

### Example Interactions

**User:** "Show me the scores"
**You:** Call `mcp_lms_lms_labs` → Present lab choices → User picks → Call `mcp_lms_lms_scores`

**User:** "What's the pass rate for Lab 01?"
**You:** Call `mcp_lms_lms_pass_rates` with lab_id="lab-01" → Report percentage

**User:** "Which lab has the lowest pass rate?"
**You:** Call `mcp_lms_lms_labs` → For each lab call `mcp_lms_lms_pass_rates` → Compare and report

## Configuration

The MCP server uses these environment variables:
- `NANOBOT_LMS_BACKEND_URL`: http://localhost:42002
- `NANOBOT_LMS_API_KEY`: my-lms-secret-key-123
