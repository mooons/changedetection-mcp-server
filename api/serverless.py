"""
Vercel serverless function wrapper for changedetection-mcp-server.

This module provides a serverless-compatible interface for the MCP server
that can be deployed on Vercel or other serverless platforms.
"""

import os
import sys
import json
import asyncio
from typing import Any, Dict, Optional
from datetime import datetime
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from server import ChangeDetectionClient, BASE_URL, API_KEY

# Configure structured logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s","module":"%(module)s"}',
)
logger = logging.getLogger(__name__)

# Initialize client
client = ChangeDetectionClient(BASE_URL, API_KEY)

# Rate limiting configuration
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

# CORS configuration
ENABLE_CORS = os.getenv("ENABLE_CORS", "true").lower() == "true"
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")


class ServerlessError(Exception):
    """Custom exception for serverless function errors."""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


def validate_request(body: Dict[str, Any]) -> None:
    """Validate incoming request structure."""
    required_fields = ["action"]
    
    for field in required_fields:
        if field not in body:
            raise ServerlessError(
                f"Missing required field: {field}",
                status_code=400,
                details={"required_fields": required_fields}
            )
    
    valid_actions = [
        "list_watches",
        "get_watch",
        "create_watch",
        "delete_watch",
        "trigger_check",
        "get_history",
        "system_info",
        "health_check",
    ]
    
    if body["action"] not in valid_actions:
        raise ServerlessError(
            f"Invalid action: {body['action']}",
            status_code=400,
            details={"valid_actions": valid_actions}
        )


def sanitize_input(data: Any) -> Any:
    """Sanitize input to prevent injection attacks."""
    if isinstance(data, str):
        # Remove potential harmful characters
        dangerous_chars = ["<", ">", "\"", "'", "&", ";"]
        for char in dangerous_chars:
            data = data.replace(char, "")
        return data.strip()
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data


def create_response(
    status_code: int,
    body: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Create standardized response object."""
    default_headers = {
        "Content-Type": "application/json",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
    }
    
    if ENABLE_CORS:
        default_headers.update({
            "Access-Control-Allow-Origin": ALLOWED_ORIGINS[0] if ALLOWED_ORIGINS else "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        })
    
    if headers:
        default_headers.update(headers)
    
    # Add request metadata
    body["_metadata"] = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
    }
    
    return {
        "statusCode": status_code,
        "headers": default_headers,
        "body": json.dumps(body, indent=2),
    }


async def handle_action(action: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle different actions and route to appropriate client methods."""
    try:
        if action == "list_watches":
            result = await client.list_watches()
            return {"success": True, "data": result}
        
        elif action == "get_watch":
            watch_id = params.get("watch_id")
            if not watch_id:
                raise ServerlessError("watch_id is required", status_code=400)
            result = await client.get_watch(watch_id)
            return {"success": True, "data": result}
        
        elif action == "create_watch":
            url = params.get("url")
            tag = params.get("tag")
            if not url:
                raise ServerlessError("url is required", status_code=400)
            result = await client.create_watch(url, tag)
            return {"success": True, "data": result}
        
        elif action == "delete_watch":
            watch_id = params.get("watch_id")
            if not watch_id:
                raise ServerlessError("watch_id is required", status_code=400)
            result = await client.delete_watch(watch_id)
            return {"success": True, "data": result}
        
        elif action == "trigger_check":
            watch_id = params.get("watch_id")
            if not watch_id:
                raise ServerlessError("watch_id is required", status_code=400)
            result = await client.trigger_check(watch_id)
            return {"success": True, "data": result}
        
        elif action == "get_history":
            watch_id = params.get("watch_id")
            if not watch_id:
                raise ServerlessError("watch_id is required", status_code=400)
            result = await client.get_history(watch_id)
            return {"success": True, "data": result}
        
        elif action == "system_info":
            result = await client.system_info()
            return {"success": True, "data": result}
        
        elif action == "health_check":
            # Simple health check for serverless
            return {
                "success": True,
                "status": "healthy",
                "data": {
                    "changedetection_url": BASE_URL,
                    "api_key_configured": bool(API_KEY),
                }
            }
        
        else:
            raise ServerlessError(f"Unknown action: {action}", status_code=400)
    
    except ServerlessError:
        raise
    except Exception as e:
        logger.error(f"Error handling action {action}: {str(e)}", exc_info=True)
        raise ServerlessError(
            f"Internal server error: {str(e)}",
            status_code=500,
            details={"action": action, "error_type": type(e).__name__}
        )


async def async_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Async handler for the serverless function."""
    request_id = context.get("requestId", "unknown") if context else "unknown"
    logger.info(f"Request {request_id} started", extra={"request_id": request_id})
    
    try:
        # Handle OPTIONS request for CORS
        if event.get("httpMethod") == "OPTIONS":
            return create_response(200, {"message": "CORS preflight OK"})
        
        # Parse request body
        body_str = event.get("body", "{}")
        try:
            body = json.loads(body_str) if isinstance(body_str, str) else body_str
        except json.JSONDecodeError as e:
            raise ServerlessError(
                "Invalid JSON in request body",
                status_code=400,
                details={"error": str(e)}
            )
        
        # Validate request
        validate_request(body)
        
        # Sanitize inputs
        action = sanitize_input(body["action"])
        params = sanitize_input(body.get("params", {}))
        
        # Log request
        logger.info(
            f"Processing action: {action}",
            extra={
                "request_id": request_id,
                "action": action,
                "params": list(params.keys()) if params else []
            }
        )
        
        # Handle action
        result = await handle_action(action, params)
        
        # Log success
        logger.info(
            f"Request {request_id} completed successfully",
            extra={"request_id": request_id, "action": action}
        )
        
        return create_response(200, result)
    
    except ServerlessError as e:
        logger.warning(
            f"Request {request_id} failed: {e.message}",
            extra={
                "request_id": request_id,
                "status_code": e.status_code,
                "details": e.details
            }
        )
        return create_response(
            e.status_code,
            {
                "success": False,
                "error": e.message,
                "details": e.details,
            }
        )
    
    except Exception as e:
        logger.error(
            f"Request {request_id} encountered unexpected error: {str(e)}",
            extra={"request_id": request_id},
            exc_info=True
        )
        return create_response(
            500,
            {
                "success": False,
                "error": "Internal server error",
                "message": str(e) if os.getenv("DEBUG") == "true" else "An unexpected error occurred",
            }
        )


def handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """
    Main handler function for Vercel serverless deployment.
    
    Args:
        event: Event object from Vercel/AWS Lambda
        context: Context object from Vercel/AWS Lambda
    
    Returns:
        Response object with statusCode, headers, and body
    """
    # Run async handler
    return asyncio.run(async_handler(event, context))


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "httpMethod": "POST",
        "body": json.dumps({
            "action": "system_info",
            "params": {}
        })
    }
    
    result = handler(test_event)
    print(json.dumps(json.loads(result["body"]), indent=2))
