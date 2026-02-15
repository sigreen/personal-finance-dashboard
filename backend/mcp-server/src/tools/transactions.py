"""Transaction-related MCP tools."""

from typing import Optional
from datetime import datetime, date
from sqlalchemy import text
from decimal import Decimal

from ..database.connection import db


async def get_transactions(
    account_ids: Optional[list[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search_query: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> dict:
    """Get transactions with optional filters.

    Args:
        account_ids: List of account UUIDs to filter by
        start_date: Start date (YYYY-MM-DD format)
        end_date: End date (YYYY-MM-DD format)
        category: Category name to filter by
        min_amount: Minimum transaction amount
        max_amount: Maximum transaction amount
        search_query: Search term for description/merchant
        limit: Maximum number of results
        offset: Pagination offset

    Returns:
        Dictionary with transactions and metadata
    """
    with db.get_session() as session:
        # Build query dynamically
        query = """
            SELECT
                t.id,
                t.account_id,
                a.account_name,
                a.institution_name,
                t.transaction_date,
                t.post_date,
                t.description,
                t.original_description,
                t.amount,
                t.transaction_type,
                t.merchant,
                t.category_id,
                c.name as category_name,
                t.is_duplicate,
                t.created_at
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE 1=1
        """
        params = {}

        # Add filters
        if account_ids:
            query += " AND t.account_id = ANY(:account_ids)"
            params["account_ids"] = account_ids

        if start_date:
            query += " AND t.transaction_date >= :start_date"
            params["start_date"] = start_date

        if end_date:
            query += " AND t.transaction_date <= :end_date"
            params["end_date"] = end_date

        if category:
            query += " AND c.name ILIKE :category"
            params["category"] = f"%{category}%"

        if min_amount is not None:
            query += " AND t.amount >= :min_amount"
            params["min_amount"] = min_amount

        if max_amount is not None:
            query += " AND t.amount <= :max_amount"
            params["max_amount"] = max_amount

        if search_query:
            query += " AND (t.description ILIKE :search OR t.merchant ILIKE :search)"
            params["search"] = f"%{search_query}%"

        # Add ordering and pagination
        query += " ORDER BY t.transaction_date DESC, t.created_at DESC"
        query += " LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset

        # Execute query
        result = session.execute(text(query), params)
        rows = result.fetchall()

        # Get total count
        count_query = """
            SELECT COUNT(*) as total
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE 1=1
        """
        if account_ids:
            count_query += " AND t.account_id = ANY(:account_ids)"
        if start_date:
            count_query += " AND t.transaction_date >= :start_date"
        if end_date:
            count_query += " AND t.transaction_date <= :end_date"
        if category:
            count_query += " AND c.name ILIKE :category"
        if min_amount is not None:
            count_query += " AND t.amount >= :min_amount"
        if max_amount is not None:
            count_query += " AND t.amount <= :max_amount"
        if search_query:
            count_query += " AND (t.description ILIKE :search OR t.merchant ILIKE :search)"

        count_result = session.execute(text(count_query), params)
        total = count_result.scalar()

        # Format results
        transactions = []
        for row in rows:
            transactions.append({
                "id": str(row.id),
                "account_id": str(row.account_id),
                "account_name": row.account_name,
                "institution_name": row.institution_name,
                "transaction_date": row.transaction_date.isoformat() if row.transaction_date else None,
                "post_date": row.post_date.isoformat() if row.post_date else None,
                "description": row.description,
                "original_description": row.original_description,
                "amount": float(row.amount) if isinstance(row.amount, Decimal) else row.amount,
                "transaction_type": row.transaction_type,
                "merchant": row.merchant,
                "category_id": str(row.category_id) if row.category_id else None,
                "category_name": row.category_name,
                "is_duplicate": row.is_duplicate,
                "created_at": row.created_at.isoformat() if row.created_at else None
            })

        return {
            "transactions": transactions,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + len(transactions)) < total
        }


async def search_transactions(
    query: str,
    account_ids: Optional[list[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50
) -> dict:
    """Full-text search across transactions.

    Args:
        query: Search query string
        account_ids: Optional list of account UUIDs to filter by
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of results

    Returns:
        Dictionary with matching transactions
    """
    return await get_transactions(
        account_ids=account_ids,
        start_date=start_date,
        end_date=end_date,
        search_query=query,
        limit=limit
    )
