"""Transaction-related MCP tools."""
from typing import Optional, List
import logging

from ..utils import parse_date

logger = logging.getLogger(__name__)


async def get_transactions(
    db,
    account_ids: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search_query: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get transactions with various filters.

    Args:
        db: Database connection
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
        List of transactions matching filters
    """
    limit = min(limit, 1000)  # Cap at 1000

    query = """
        SELECT
            t.id,
            t.transaction_date,
            t.post_date,
            t.description,
            t.original_description,
            t.amount,
            t.transaction_type,
            t.merchant,
            t.notes,
            t.is_duplicate,
            a.account_name,
            a.institution_name,
            a.account_type,
            c.name as category_name,
            c.category_type
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE 1=1
    """

    params = []
    param_count = 0

    # Filter by account IDs
    if account_ids:
        account_id_list = [aid.strip() for aid in account_ids.split(',')]
        param_count += 1
        placeholders = ','.join(f'${i}' for i in range(param_count, param_count + len(account_id_list)))
        query += f" AND t.account_id = ANY(ARRAY[{placeholders}]::uuid[])"
        params.extend(account_id_list)
        param_count += len(account_id_list) - 1

    # Filter by date range
    if start_date:
        parsed_start = parse_date(start_date)
        if parsed_start:
            param_count += 1
            query += f" AND t.transaction_date >= ${param_count}"
            params.append(parsed_start)

    if end_date:
        parsed_end = parse_date(end_date)
        if parsed_end:
            param_count += 1
            query += f" AND t.transaction_date <= ${param_count}"
            params.append(parsed_end)

    # Filter by category
    if category:
        param_count += 1
        query += f" AND (c.name ILIKE ${param_count} OR t.category_id::text = ${param_count})"
        params.append(category if '::' not in category else category.split('::')[0])

    # Filter by amount range
    if min_amount is not None:
        param_count += 1
        query += f" AND t.amount >= ${param_count}"
        params.append(min_amount)

    if max_amount is not None:
        param_count += 1
        query += f" AND t.amount <= ${param_count}"
        params.append(max_amount)

    # Search query
    if search_query:
        # Search in description, original_description, merchant, and notes
        # Also strip spaces from search term to match variations like "HOMEDEPOT" vs "HOME DEPOT"
        param_count += 1
        search_param = param_count
        param_count += 1
        search_no_space_param = param_count

        query += f" AND (t.description ILIKE ${search_param} OR t.original_description ILIKE ${search_param} OR t.merchant ILIKE ${search_param} OR t.notes ILIKE ${search_param} OR REPLACE(t.description, ' ', '') ILIKE ${search_no_space_param} OR REPLACE(t.original_description, ' ', '') ILIKE ${search_no_space_param})"
        params.append(f'%{search_query}%')
        # Also search with spaces removed for variations like "Home Depot" matching "HOMEDEPOT"
        params.append(f'%{search_query.replace(" ", "")}%')

    # Order and pagination
    query += " ORDER BY t.transaction_date DESC, t.created_at DESC"
    param_count += 1
    query += f" LIMIT ${param_count}"
    params.append(limit)
    param_count += 1
    query += f" OFFSET ${param_count}"
    params.append(offset)

    results = await db.execute_query(query, *params)

    transactions = []
    for row in results:
        transactions.append({
            "id": str(row['id']),
            "transaction_date": row['transaction_date'].isoformat(),
            "post_date": row['post_date'].isoformat() if row['post_date'] else None,
            "description": row['description'],
            "original_description": row['original_description'],
            "amount": float(row['amount']),
            "transaction_type": row['transaction_type'],
            "merchant": row['merchant'],
            "notes": row['notes'],
            "is_duplicate": row['is_duplicate'],
            "account": {
                "name": row['account_name'],
                "institution": row['institution_name'],
                "type": row['account_type']
            },
            "category": {
                "name": row['category_name'],
                "type": row['category_type']
            } if row['category_name'] else None
        })

    return {
        "transactions": transactions,
        "count": len(transactions),
        "limit": limit,
        "offset": offset
    }


async def search_transactions(
    db,
    query: str,
    account_ids: Optional[str] = None,
    date_range: Optional[str] = None,
    limit: int = 50
):
    """Full-text search across transactions.

    Args:
        db: Database connection
        query: Search query
        account_ids: Comma-separated list of account UUIDs
        date_range: Date range in format "start,end"
        limit: Maximum results

    Returns:
        Matching transactions
    """
    filters = {
        'search_query': query,
        'limit': limit
    }

    if account_ids:
        filters['account_ids'] = account_ids

    if date_range:
        try:
            start_date, end_date = date_range.split(',')
            filters['start_date'] = start_date.strip()
            filters['end_date'] = end_date.strip()
        except ValueError:
            logger.warning(f"Invalid date_range format: {date_range}")

    return await get_transactions(db, **filters)
