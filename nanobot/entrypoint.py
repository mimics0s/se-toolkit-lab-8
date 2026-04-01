#!/usr/bin/env python3
"""
Entrypoint for nanobot Docker container.

Resolves environment variables into config.json at runtime, then launches nanobot gateway.
"""

import json
import os
import sys
from pathlib import Path


def main():
    # Paths
    app_dir = Path("/app/nanobot")
    config_path = app_dir / "config.json"
    resolved_path = Path("/tmp/config.resolved.json")  # Write to /tmp to avoid permission issues
    workspace_dir = app_dir / "workspace"

    # Read base config
    with open(config_path) as f:
        config = json.load(f)

    # Override from environment variables
    # LLM provider settings
    if api_key := os.environ.get("LLM_API_KEY"):
        config["providers"]["custom"]["apiKey"] = api_key
    if api_base := os.environ.get("LLM_API_BASE_URL"):
        config["providers"]["custom"]["apiBase"] = api_base
    if api_model := os.environ.get("LLM_API_MODEL"):
        config["agents"]["defaults"]["model"] = api_model

    # Gateway settings
    if gateway_host := os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS"):
        config["gateway"]["host"] = gateway_host
    if gateway_port := os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT"):
        config["gateway"]["port"] = int(gateway_port)

    # Webchat channel settings
    if webchat_host := os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS"):
        if "webchat" not in config["channels"]:
            config["channels"]["webchat"] = {}
        config["channels"]["webchat"]["host"] = webchat_host
    if webchat_port := os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT"):
        if "webchat" not in config["channels"]:
            config["channels"]["webchat"] = {}
        config["channels"]["webchat"]["port"] = int(webchat_port)
    if webchat_enabled := os.environ.get("NANOBOT_WEBSOCKET_ENABLED"):
        if "webchat" not in config["channels"]:
            config["channels"]["webchat"] = {}
        config["channels"]["webchat"]["enabled"] = webchat_enabled.lower() == "true"
    if access_key := os.environ.get("NANOBOT_ACCESS_KEY"):
        if "webchat" not in config["channels"]:
            config["channels"]["webchat"] = {}
        config["channels"]["webchat"]["accessKey"] = access_key

    # MCP LMS server settings
    if lms_backend_url := os.environ.get("NANOBOT_LMS_BACKEND_URL"):
        config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_BACKEND_URL"] = lms_backend_url
    if lms_api_key := os.environ.get("NANOBOT_LMS_API_KEY"):
        config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_API_KEY"] = lms_api_key

    # MCP webchat server settings
    if webchat_relay_url := os.environ.get("NANOBOT_WEBSOCKET_RELAY_URL"):
        config["tools"]["mcpServers"]["webchat"]["env"]["NANOBOT_WEBSOCKET_RELAY_URL"] = webchat_relay_url
    if webchat_token := os.environ.get("NANOBOT_WEBSOCKET_TOKEN"):
        config["tools"]["mcpServers"]["webchat"]["env"]["NANOBOT_WEBSOCKET_TOKEN"] = webchat_token

    # MCP obs server settings
    if obs_logs_url := os.environ.get("NANOBOT_VICTORIALOGS_URL"):
        config["tools"]["mcpServers"]["obs"]["env"]["NANOBOT_VICTORIALOGS_URL"] = obs_logs_url
    if obs_traces_url := os.environ.get("NANOBOT_VICTORIATRACES_URL"):
        config["tools"]["mcpServers"]["obs"]["env"]["NANOBOT_VICTORIATRACES_URL"] = obs_traces_url

    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Using config: {resolved_path}", file=sys.stderr)

    # Launch nanobot gateway
    os.execvp("nanobot", ["nanobot", "gateway", "--config", str(resolved_path), "--workspace", str(workspace_dir)])


if __name__ == "__main__":
    main()
