#!/usr/bin/env python3
"""Production-ready MCP server for changedetection.io API."""

import os
import sys
from typing import Any, Optional
import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.stdio import stdio_server
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Changedetection.io API configuration
BASE_URL = os.getenv("CHANGEDETECTION_URL", "http://localhost:5000")
API_KEY = os.getenv("CHANGEDETECTION_API_KEY", "")

if not API_KEY:
    logger.warning("CHANGEDETECTION_API_KEY not set. Some operations may fail.")

# Initialize MCP server
app = Server("changedetection-mcp-server")


class ChangeDetectionClient:
    """Client for interacting with changedetection.io API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"x-api-key": api_key} if api_key else {}

    async def _request(
        self, method: str, endpoint: str, data: Optional[dict] = None
    ) -> Any:
        """Make HTTP request to changedetection.io API."""
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            try:
                if method == "GET":
                    response = await client.get(url, headers=self.headers, timeout=30.0)
                elif method == "POST":
                    response = await client.post(
                        url, headers=self.headers, json=data, timeout=30.0
                    )
                elif method == "DELETE":
                    response = await client.delete(url, headers=self.headers, timeout=30.0)
                elif method == "PUT":
                    response = await client.put(
                        url, headers=self.headers, json=data, timeout=30.0
                    )
                else:
                    raise ValueError(f"Unsupported method: {method}")

                response.raise_for_status()
                return response.json() if response.text else {}
            except httpx.HTTPError as e:
                logger.error(f"HTTP error occurred: {e}")
                raise
            except Exception as e:
                logger.error(f"Error occurred: {e}")
                raise

    async def list_watches(self) -> dict:
        """List all watches."""
        return await self._request("GET", "/api/v1/watch")

    async def get_watch(self, watch_id: str) -> dict:
        """Get details of a specific watch."""
        return await self._request("GET", f"/api/v1/watch/{watch_id}")

    async def create_watch(self, url: str, tag: Optional[str] = None) -> dict:
        """Create a new watch."""
        data = {"url": url}
        if tag:
            data["tag"] = tag
        return await self._request("POST", "/api/v1/watch", data)

    async def delete_watch(self, watch_id: str) -> dict:
        """Delete a watch."""
        return await self._request("DELETE", f"/api/v1/watch/{watch_id}")

    async def trigger_check(self, watch_id: str) -> dict:
        """Trigger a check for a specific watch."""
        return await self._request("GET", f"/api/v1/watch/{watch_id}/trigger")

    async def get_history(self, watch_id: str) -> dict:
        """Get history of changes for a watch."""
        return await self._request("GET", f"/api/v1/watch/{watch_id}/history")

    async def system_info(self) -> dict:
        """Get system information."""
        return await self._request("GET", "/api/v1/systeminfo")


# Initialize client
client = ChangeDetectionClient(BASE_URL, API_KEY)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="list_watches",
            description="List all website watches configured in changedetection.io",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_watch",
            description="Get detailed information about a specific watch including URL, last check time, and change detection settings",
            inputSchema={
                "type": "object",
                "properties": {
                    "watch_id": {
                        "type": "string",
                        "description": "The UUID of the watch to retrieve",
                    }
                },
                "required": ["watch_id"],
            },
        ),
        Tool(
            name="create_watch",
            description="Create a new watch to monitor a website for changes",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to monitor for changes",
                    },
                    "tag": {
                        "type": "string",
                        "description": "Optional tag to categorize the watch",
                    },
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="delete_watch",
            description="Delete a watch and stop monitoring the associated URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "watch_id": {
                        "type": "string",
                        "description": "The UUID of the watch to delete",
                    }
                },
                "required": ["watch_id"],
            },
        ),
        Tool(
            name="trigger_check",
            description="Manually trigger a change detection check for a specific watch",
            inputSchema={
                "type": "object",
                "properties": {
                    "watch_id": {
                        "type": "string",
                        "description": "The UUID of the watch to check",
                    }
                },
                "required": ["watch_id"],
            },
        ),
        Tool(
            name="get_history",
            description="Get the history of detected changes for a specific watch",
            inputSchema={
                "type": "object",
                "properties": {
                    "watch_id": {
                        "type": "string",
                        "description": "The UUID of the watch to get history for",
                    }
                },
                "required": ["watch_id"],
            },
        ),
        Tool(
            name="system_info",
            description="Get system information about the changedetection.io instance",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "list_watches":
            result = await client.list_watches()
            return [TextContent(type="text", text=str(result))]

        elif name == "get_watch":
            watch_id = arguments.get("watch_id")
            if not watch_id:
                return [
                    TextContent(type="text", text="Error: watch_id is required")
                ]
            result = await client.get_watch(watch_id)
            return [TextContent(type="text", text=str(result))]

        elif name == "create_watch":
            url = arguments.get("url")
            tag = arguments.get("tag")
            if not url:
                return [TextContent(type="text", text="Error: url is required")]
            result = await client.create_watch(url, tag)
            return [TextContent(type="text", text=str(result))]

        elif name == "delete_watch":
            watch_id = arguments.get("watch_id")
            if not watch_id:
                return [
                    TextContent(type="text", text="Error: watch_id is required")
                ]
            result = await client.delete_watch(watch_id)
            return [TextContent(type="text", text=str(result))]

        elif name == "trigger_check":
            watch_id = arguments.get("watch_id")
            if not watch_id:
                return [
                    TextContent(type="text", text="Error: watch_id is required")
                ]
            result = await client.trigger_check(watch_id)
            return [TextContent(type="text", text=str(result))]

        elif name == "get_history":
            watch_id = arguments.get("watch_id")
            if not watch_id:
                return [
                    TextContent(type="text", text="Error: watch_id is required")
                ]
            result = await client.get_history(watch_id)
            return [TextContent(type="text", text=str(result))]

        elif name == "system_info":
            result = await client.system_info()
            return [TextContent(type="text", text=str(result))]

        else:
            return [
                TextContent(
                    type="text", text=f"Error: Unknown tool '{name}'"
                )
            ]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _main_async():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main() -> None:
    """Console entrypoint for running the MCP server."""
    asyncio.run(_main_async())


if __name__ == "__main__":
    main()
