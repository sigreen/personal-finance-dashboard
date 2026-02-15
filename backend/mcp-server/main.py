#!/usr/bin/env python3
"""Entry point for Personal Finance MCP Server."""

import os
import asyncio

if __name__ == "__main__":
    mode = os.getenv("MCP_TRANSPORT_MODE", "http")

    if mode == "stdio":
        # Legacy stdio mode for backward compatibility
        from src.server import main_stdio
        asyncio.run(main_stdio())
    else:
        # HTTP mode (default) - run FastAPI with uvicorn
        import uvicorn
        from src.config import settings

        uvicorn.run(
            "src.http_server:app",
            host=settings.http_host,
            port=settings.http_port,
            log_level=settings.log_level.lower()
        )
