"""Personal Finance MCP Server with SSE support."""
import asyncio
import logging
import os
import sys
from typing import Any
import json

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

from starlette.applications import Starlette
from starlette.routing import Route
import uvicorn

from .database import DatabaseConnection
from .tools import accounts, transactions, analytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
app_name = "personal-finance-mcp"
mcp_server = Server(app_name)

# Database connection
db = None


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="get_account_summary",
            description="Get summary of all accounts with current balances. Optionally filter by date range.",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_range": {
                        "type": "string",
                        "description": "Optional date range in format 'YYYY-MM-DD,YYYY-MM-DD'"
                    }
                }
            }
        ),
        Tool(
            name="get_account_details",
            description="Get detailed information about a specific account including transaction statistics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "UUID of the account"
                    }
                },
                "required": ["account_id"]
            }
        ),
        Tool(
            name="get_transactions",
            description="Get transactions with various filters (account, date range, category, amount, search). Returns up to 1000 transactions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_ids": {
                        "type": "string",
                        "description": "Comma-separated list of account UUIDs"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Category name or UUID"
                    },
                    "min_amount": {
                        "type": "number",
                        "description": "Minimum transaction amount"
                    },
                    "max_amount": {
                        "type": "number",
                        "description": "Maximum transaction amount"
                    },
                    "search_query": {
                        "type": "string",
                        "description": "Search in description, merchant, notes"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default 100, max 1000)",
                        "default": 100
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of results to skip",
                        "default": 0
                    }
                }
            }
        ),
        Tool(
            name="search_transactions",
            description="Full-text search across transactions. Search in description, merchant, and notes fields.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "account_ids": {
                        "type": "string",
                        "description": "Comma-separated list of account UUIDs"
                    },
                    "date_range": {
                        "type": "string",
                        "description": "Date range in format 'YYYY-MM-DD,YYYY-MM-DD'"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results",
                        "default": 50
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_spending_by_category",
            description="Get aggregated spending grouped by category. Shows debits, credits, and net amounts per category.",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)"
                    },
                    "account_ids": {
                        "type": "string",
                        "description": "Comma-separated account UUIDs"
                    },
                    "category_type": {
                        "type": "string",
                        "description": "Filter by category type",
                        "enum": ["income", "expense", "transfer"]
                    }
                }
            }
        ),
        Tool(
            name="get_merchant_spending",
            description="Get spending grouped by merchant. Shows top merchants by total spending.",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)"
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Number of top merchants to return",
                        "default": 20
                    }
                }
            }
        ),
        Tool(
            name="get_cash_flow",
            description="Get income vs expenses over time. Shows cash flow by period (daily, weekly, monthly, yearly).",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)"
                    },
                    "granularity": {
                        "type": "string",
                        "description": "Time grouping",
                        "enum": ["daily", "weekly", "monthly", "yearly"],
                        "default": "monthly"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        ),
        Tool(
            name="get_budget_status",
            description="Get budget vs actual spending. Shows budgeted amounts, actual spending, and remaining budget by category.",
            inputSchema={
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "description": "Time period",
                        "enum": ["current_month", "current_quarter", "current_year"],
                        "default": "current_month"
                    }
                }
            }
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution."""
    global db

    if db is None:
        return [TextContent(type="text", text="Error: Database not connected")]

    try:
        # Route to appropriate tool handler
        if name == "get_account_summary":
            result = await accounts.get_account_summary(db, **arguments)
        elif name == "get_account_details":
            result = await accounts.get_account_details(db, **arguments)
        elif name == "get_transactions":
            result = await transactions.get_transactions(db, **arguments)
        elif name == "search_transactions":
            result = await transactions.search_transactions(db, **arguments)
        elif name == "get_spending_by_category":
            result = await analytics.get_spending_by_category(db, **arguments)
        elif name == "get_merchant_spending":
            result = await analytics.get_merchant_spending(db, **arguments)
        elif name == "get_cash_flow":
            result = await analytics.get_cash_flow(db, **arguments)
        elif name == "get_budget_status":
            result = await analytics.get_budget_status(db, **arguments)
        else:
            return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

        # Return formatted result
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


# Create SSE transport
sse = SseServerTransport("/messages/")

# SSE endpoint handler
async def handle_sse(request):
    """Handle SSE connections."""
    from starlette.responses import Response
    logger.info(f"SSE connection request from {request.client}")
    try:
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            logger.info("SSE streams established, starting MCP server")
            await mcp_server.run(
                streams[0], streams[1], mcp_server.create_initialization_options()
            )
        logger.info("SSE connection closed")
    except Exception as e:
        logger.error(f"SSE handler error: {e}", exc_info=True)
        raise
    return Response()


# Health check endpoint
async def health_check(request):
    """Health check endpoint."""
    from starlette.responses import JSONResponse
    return JSONResponse({"status": "healthy", "server": app_name})


# Create Starlette app
from starlette.routing import Mount

routes = [
    Route("/sse", endpoint=handle_sse, methods=["GET"]),
    Mount("/messages/", app=sse.handle_post_message),
    Route("/health", endpoint=health_check),
]

async def startup():
    """Startup event handler."""
    await init_database()

async def shutdown():
    """Shutdown event handler."""
    await cleanup()

starlette_app = Starlette(
    routes=routes,
    on_startup=[startup],
    on_shutdown=[shutdown]
)


async def init_database():
    """Initialize database connection."""
    global db
    try:
        db = DatabaseConnection()
        await db.connect()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


async def cleanup():
    """Cleanup resources."""
    global db
    if db:
        await db.disconnect()
        logger.info("Database disconnected")


def main():
    """Run the MCP server."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', '8081'))

    logger.info(f"Starting Personal Finance MCP Server on {host}:{port}")
    logger.info(f"SSE endpoint: http://{host}:{port}/sse")
    logger.info(f"Health check: http://{host}:{port}/health")

    try:
        uvicorn.run(
            starlette_app,
            host=host,
            port=port,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")


if __name__ == "__main__":
    main()
