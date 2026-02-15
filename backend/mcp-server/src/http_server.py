"""HTTP Server with SSE Transport for Personal Finance MCP Server.

Exposes the MCP server over HTTP using Server-Sent Events (SSE) for
bidirectional communication with MCP clients.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from mcp.server.sse import SseServerTransport

from .config import settings
from .database.connection import db

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.server_name,
    description="Personal Finance MCP Server with SSE Transport",
    version=settings.server_version
)

# CORS middleware - allow connections from MCP clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SSE transport
# The "/messages/" endpoint will be used for client POST requests
sse = SseServerTransport("/messages/")


@app.on_event("startup")
async def startup_event():
    """Initialize server on startup."""
    from .server import init_server
    await init_server()


@app.get("/")
async def root():
    """Root endpoint with server info."""
    return {
        "service": settings.server_name,
        "version": settings.server_version,
        "status": "running",
        "transport": "sse"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes."""
    # Simple health check - just verify the server is running
    # Database connection is tested at startup, not on every health check
    return {
        "status": "healthy",
        "service": settings.server_name
    }


@app.get("/sse")
async def handle_sse(request: Request):
    """Handle SSE connection establishment.

    This endpoint establishes a Server-Sent Events connection with the client.
    The client connects here to receive MCP protocol messages from the server.
    """
    from .server import server

    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await server.run(
            streams[0], streams[1],
            server.create_initialization_options()
        )
    return Response()


@app.post("/messages/")
async def handle_messages(request: Request):
    """Handle incoming client messages.

    This endpoint receives POST requests from the client containing
    MCP protocol messages (initialization, tool calls, etc.).
    The session ID links these messages to the SSE connection.
    """
    return await sse.handle_post_message(
        request.scope, request.receive, request._send
    )
