"""Personal Finance MCP Server.

Exposes financial data through the Model Context Protocol for AI model queries.
"""

import asyncio
import logging
from mcp.server import Server
from mcp.types import Tool, TextContent

from .config import settings
from .database.connection import db
from .tools.transactions import get_transactions, search_transactions
from .tools.accounts import get_account_summary
from .tools.analytics import (
    get_spending_by_category,
    get_merchant_spending,
    get_cash_flow
)

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server(settings.server_name)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_account_summary",
            description="Get summary of all financial accounts with transaction statistics",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date for statistics (YYYY-MM-DD format)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for statistics (YYYY-MM-DD format)",
                    },
                },
            },
        ),
        Tool(
            name="get_transactions",
            description="Get transactions with optional filters (account, date range, category, amount, search)",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of account UUIDs to filter by",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "category": {
                        "type": "string",
                        "description": "Category name to filter by",
                    },
                    "min_amount": {
                        "type": "number",
                        "description": "Minimum transaction amount",
                    },
                    "max_amount": {
                        "type": "number",
                        "description": "Maximum transaction amount",
                    },
                    "search_query": {
                        "type": "string",
                        "description": "Search term for description/merchant",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 100,
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Pagination offset",
                        "default": 0,
                    },
                },
            },
        ),
        Tool(
            name="search_transactions",
            description="Full-text search across transaction descriptions and merchants",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string",
                    },
                    "account_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of account UUIDs to filter by",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Optional start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Optional end date (YYYY-MM-DD)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 50,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_spending_by_category",
            description="Get spending aggregated and grouped by category",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "account_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of account UUIDs",
                    },
                    "category_type": {
                        "type": "string",
                        "enum": ["income", "expense"],
                        "description": "Filter by category type",
                    },
                },
            },
        ),
        Tool(
            name="get_merchant_spending",
            description="Get spending grouped by merchant/vendor",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Number of top merchants to return",
                        "default": 20,
                    },
                },
            },
        ),
        Tool(
            name="get_cash_flow",
            description="Get income vs expenses over time with configurable granularity",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "granularity": {
                        "type": "string",
                        "enum": ["daily", "weekly", "monthly"],
                        "description": "Time granularity for aggregation",
                        "default": "monthly",
                    },
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        logger.info(f"Calling tool: {name} with arguments: {arguments}")

        # Route to appropriate tool handler
        if name == "get_account_summary":
            result = await get_account_summary(**arguments)
        elif name == "get_transactions":
            result = await get_transactions(**arguments)
        elif name == "search_transactions":
            result = await search_transactions(**arguments)
        elif name == "get_spending_by_category":
            result = await get_spending_by_category(**arguments)
        elif name == "get_merchant_spending":
            result = await get_merchant_spending(**arguments)
        elif name == "get_cash_flow":
            result = await get_cash_flow(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        # Return result as text content
        import json
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error calling tool {name}: {str(e)}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    # Test database connection
    logger.info("Testing database connection...")
    if not db.test_connection():
        logger.warning("Failed to connect to database - will retry on first request")
    else:
        logger.info("Database connection successful")

    logger.info(f"Starting {settings.server_name} v{settings.server_version}")

    # Run the server
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
