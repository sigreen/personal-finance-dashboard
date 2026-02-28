"""Personal Finance MCP Server using FastMCP with HTTP/SSE transport."""
import logging
import os
from typing import Any, Optional
from dotenv import load_dotenv

from fastmcp import FastMCP
from starlette.responses import JSONResponse

from .database import DatabaseConnection
from .tools import accounts, transactions, analytics

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("personal-finance-mcp")

# Database connection (global for simplicity)
db: Optional[DatabaseConnection] = None


async def get_db() -> DatabaseConnection:
    """Get or initialize database connection."""
    global db
    if db is None:
        db = DatabaseConnection()
        await db.connect()
        logger.info("Database connected successfully")
    return db


@mcp.tool
async def get_account_summary(date_range: Optional[str] = None) -> dict[str, Any]:
    """Get summary of all accounts with current balances.

    Args:
        date_range: Optional date range in format 'YYYY-MM-DD,YYYY-MM-DD'

    Returns:
        Dictionary containing account summary data
    """
    db = await get_db()
    kwargs = {}
    if date_range:
        kwargs['date_range'] = date_range

    return await accounts.get_account_summary(db, **kwargs)


@mcp.tool
async def get_account_details(account_id: str) -> dict[str, Any]:
    """Get detailed information about a specific account.

    Args:
        account_id: UUID of the account

    Returns:
        Dictionary containing account details and transaction statistics
    """
    db = await get_db()
    return await accounts.get_account_details(db, account_id=account_id)


@mcp.tool
async def get_transactions(
    account_ids: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search_query: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> dict[str, Any]:
    """Get transactions with various filters.

    Args:
        account_ids: Comma-separated list of account UUIDs
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        category: Category name or UUID
        min_amount: Minimum transaction amount
        max_amount: Maximum transaction amount
        search_query: Search in description, merchant, notes
        limit: Maximum number of results (default 100, max 1000)
        offset: Number of results to skip

    Returns:
        Dictionary containing transactions and metadata
    """
    db = await get_db()
    kwargs = {}
    if account_ids:
        kwargs['account_ids'] = account_ids
    if start_date:
        kwargs['start_date'] = start_date
    if end_date:
        kwargs['end_date'] = end_date
    if category:
        kwargs['category'] = category
    if min_amount is not None:
        kwargs['min_amount'] = min_amount
    if max_amount is not None:
        kwargs['max_amount'] = max_amount
    if search_query:
        kwargs['search_query'] = search_query
    kwargs['limit'] = limit
    kwargs['offset'] = offset

    return await transactions.get_transactions(db, **kwargs)


@mcp.tool
async def search_transactions(
    query: str,
    account_ids: Optional[str] = None,
    date_range: Optional[str] = None,
    limit: int = 50
) -> dict[str, Any]:
    """Full-text search across transactions.

    Args:
        query: Search query
        account_ids: Comma-separated list of account UUIDs
        date_range: Date range in format 'YYYY-MM-DD,YYYY-MM-DD'
        limit: Maximum results

    Returns:
        Dictionary containing search results
    """
    db = await get_db()
    kwargs = {'query': query, 'limit': limit}
    if account_ids:
        kwargs['account_ids'] = account_ids
    if date_range:
        kwargs['date_range'] = date_range

    return await transactions.search_transactions(db, **kwargs)


@mcp.tool
async def get_spending_by_category(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    account_ids: Optional[str] = None,
    category_type: Optional[str] = None
) -> dict[str, Any]:
    """Get aggregated spending grouped by category.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        account_ids: Comma-separated account UUIDs
        category_type: Filter by category type (income, expense, transfer)

    Returns:
        Dictionary containing spending by category
    """
    db = await get_db()
    kwargs = {}
    if start_date:
        kwargs['start_date'] = start_date
    if end_date:
        kwargs['end_date'] = end_date
    if account_ids:
        kwargs['account_ids'] = account_ids
    if category_type:
        kwargs['category_type'] = category_type

    return await analytics.get_spending_by_category(db, **kwargs)


@mcp.tool
async def get_merchant_spending(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    top_n: int = 20
) -> dict[str, Any]:
    """Get spending grouped by merchant.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        top_n: Number of top merchants to return

    Returns:
        Dictionary containing merchant spending data
    """
    db = await get_db()
    kwargs = {'top_n': top_n}
    if start_date:
        kwargs['start_date'] = start_date
    if end_date:
        kwargs['end_date'] = end_date

    return await analytics.get_merchant_spending(db, **kwargs)


@mcp.tool
async def get_cash_flow(
    start_date: str,
    end_date: str,
    granularity: str = "monthly"
) -> dict[str, Any]:
    """Get income vs expenses over time.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        granularity: Time grouping (daily, weekly, monthly, yearly)

    Returns:
        Dictionary containing cash flow data
    """
    db = await get_db()
    return await analytics.get_cash_flow(
        db,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity
    )


@mcp.tool
async def get_budget_status(period: str = "current_month") -> dict[str, Any]:
    """Get budget vs actual spending.

    Args:
        period: Time period (current_month, current_quarter, current_year)

    Returns:
        Dictionary containing budget status
    """
    db = await get_db()
    return await analytics.get_budget_status(db, period=period)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for Kubernetes."""
    return JSONResponse({"status": "healthy", "server": "personal-finance-mcp"})


def main():
    """Run the MCP server with HTTP/SSE transport."""
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8081'))

    logger.info(f"Starting Personal Finance MCP Server on {host}:{port}")
    logger.info(f"SSE endpoint: http://{host}:{port}/sse")
    logger.info(f"Health check: http://{host}:{port}/health")

    try:
        mcp.run(transport="http", host=host, port=port)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        if db:
            import asyncio
            asyncio.run(db.disconnect())


if __name__ == "__main__":
    main()
