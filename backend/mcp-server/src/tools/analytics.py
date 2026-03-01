"""Analytics and aggregation MCP tools."""
from typing import Optional
import logging
from datetime import datetime, timedelta
import calendar

from ..utils import parse_date

logger = logging.getLogger(__name__)


async def get_spending_by_category(
    db,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    account_ids: Optional[str] = None,
    category_type: Optional[str] = None
):
    """Get aggregated spending grouped by category.

    Args:
        db: Database connection
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        account_ids: Comma-separated account UUIDs
        category_type: Filter by category type (income, expense, transfer)

    Returns:
        Spending aggregated by category
    """
    query = """
        SELECT
            c.id as category_id,
            c.name as category_name,
            c.category_type,
            c.parent_category_id,
            COUNT(t.id) as transaction_count,
            SUM(CASE
                WHEN t.transaction_type = 'debit' THEN t.amount
                ELSE 0
            END) as total_debits,
            SUM(CASE
                WHEN t.transaction_type = 'credit' THEN t.amount
                ELSE 0
            END) as total_credits,
            SUM(CASE
                WHEN t.transaction_type = 'credit' THEN t.amount
                ELSE -t.amount
            END) as net_amount,
            MIN(t.transaction_date) as first_transaction,
            MAX(t.transaction_date) as last_transaction
        FROM categories c
        LEFT JOIN transactions t ON c.id = t.category_id
        WHERE 1=1
    """

    params = []
    param_count = 0

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

    if account_ids:
        account_id_list = [aid.strip() for aid in account_ids.split(',')]
        param_count += 1
        placeholders = ','.join(f'${i}' for i in range(param_count, param_count + len(account_id_list)))
        query += f" AND t.account_id = ANY(ARRAY[{placeholders}]::uuid[])"
        params.extend(account_id_list)
        param_count += len(account_id_list) - 1

    if category_type:
        param_count += 1
        query += f" AND c.category_type = ${param_count}"
        params.append(category_type)

    query += """
        GROUP BY c.id, c.name, c.category_type, c.parent_category_id
        HAVING COUNT(t.id) > 0
        ORDER BY ABS(SUM(CASE
            WHEN t.transaction_type = 'credit' THEN t.amount
            ELSE -t.amount
        END)) DESC
    """

    results = await db.execute_query(query, *params)

    categories = []
    total_debits = 0
    total_credits = 0

    for row in results:
        category_data = {
            "category_id": str(row['category_id']),
            "category_name": row['category_name'],
            "category_type": row['category_type'],
            "parent_category_id": str(row['parent_category_id']) if row['parent_category_id'] else None,
            "transaction_count": row['transaction_count'],
            "total_debits": float(row['total_debits']),
            "total_credits": float(row['total_credits']),
            "net_amount": float(row['net_amount']),
            "first_transaction": row['first_transaction'].isoformat() if row['first_transaction'] else None,
            "last_transaction": row['last_transaction'].isoformat() if row['last_transaction'] else None
        }
        categories.append(category_data)
        total_debits += category_data['total_debits']
        total_credits += category_data['total_credits']

    return {
        "categories": categories,
        "summary": {
            "total_categories": len(categories),
            "total_debits": total_debits,
            "total_credits": total_credits,
            "net_amount": total_credits - total_debits
        }
    }


async def get_merchant_spending(
    db,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    top_n: int = 20
):
    """Get spending grouped by merchant.

    Args:
        db: Database connection
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        top_n: Number of top merchants to return

    Returns:
        Top merchants by spending
    """
    query = """
        SELECT
            COALESCE(merchant, 'Unknown') as merchant_name,
            COUNT(*) as transaction_count,
            SUM(amount) as total_spent,
            AVG(amount) as avg_transaction,
            MIN(transaction_date) as first_transaction,
            MAX(transaction_date) as last_transaction
        FROM transactions
        WHERE merchant IS NOT NULL
    """

    params = []
    param_count = 0

    if start_date:
        parsed_start = parse_date(start_date)
        if parsed_start:
            param_count += 1
            query += f" AND transaction_date >= ${param_count}"
            params.append(parsed_start)

    if end_date:
        parsed_end = parse_date(end_date)
        if parsed_end:
            param_count += 1
            query += f" AND transaction_date <= ${param_count}"
            params.append(parsed_end)

    query += """
        GROUP BY merchant
        ORDER BY total_spent DESC
    """

    param_count += 1
    query += f" LIMIT ${param_count}"
    params.append(top_n)

    results = await db.execute_query(query, *params)

    merchants = []
    for row in results:
        merchants.append({
            "merchant": row['merchant_name'],
            "transaction_count": row['transaction_count'],
            "total_spent": float(row['total_spent']),
            "avg_transaction": float(row['avg_transaction']),
            "first_transaction": row['first_transaction'].isoformat(),
            "last_transaction": row['last_transaction'].isoformat()
        })

    return {
        "merchants": merchants,
        "count": len(merchants)
    }


async def get_cash_flow(
    db,
    start_date: str,
    end_date: str,
    granularity: str = 'monthly'
):
    """Get income vs expenses over time.

    Args:
        db: Database connection
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        granularity: Time grouping (daily, weekly, monthly, yearly)

    Returns:
        Cash flow data by time period
    """
    # Validate and sanitize granularity input - SECURITY: Whitelist approach
    # Only allow known safe values to prevent SQL injection
    allowed_truncations = {
        'daily': 'day',
        'weekly': 'week',
        'monthly': 'month',
        'yearly': 'year'
    }

    if granularity not in allowed_truncations:
        granularity = 'monthly'  # Default to monthly if invalid

    trunc = allowed_truncations[granularity]

    # Parse dates
    parsed_start = parse_date(start_date)
    parsed_end = parse_date(end_date)

    if not parsed_start or not parsed_end:
        return {"periods": [], "summary": {"granularity": granularity, "total_income": 0, "total_expenses": 0, "net_flow": 0, "period_count": 0}}

    # SECURITY FIX: Use parameterized query with validated trunc value
    # The trunc value is validated against whitelist above
    query = f"""
        SELECT
            DATE_TRUNC('{trunc}', transaction_date) as period,
            SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) as expenses,
            SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE -amount END) as net_flow,
            COUNT(*) as transaction_count
        FROM transactions
        WHERE transaction_date BETWEEN $1 AND $2
        GROUP BY period
        ORDER BY period
    """

    results = await db.execute_query(query, parsed_start, parsed_end)

    periods = []
    total_income = 0
    total_expenses = 0

    for row in results:
        period_data = {
            "period": row['period'].isoformat(),
            "income": float(row['income']),
            "expenses": float(row['expenses']),
            "net_flow": float(row['net_flow']),
            "transaction_count": row['transaction_count']
        }
        periods.append(period_data)
        total_income += period_data['income']
        total_expenses += period_data['expenses']

    return {
        "periods": periods,
        "summary": {
            "granularity": granularity,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_flow": total_income - total_expenses,
            "period_count": len(periods)
        }
    }


async def get_budget_status(db, period: str = 'current_month'):
    """Get budget vs actual spending.

    Args:
        db: Database connection
        period: Time period (current_month, current_quarter, current_year)

    Returns:
        Budget status with actual vs budgeted amounts
    """
    # SECURITY FIX: Calculate dates in Python instead of SQL string interpolation
    # Validate period against whitelist
    allowed_periods = ['current_month', 'current_quarter', 'current_year']
    if period not in allowed_periods:
        period = 'current_month'

    # Calculate date range based on period using Python datetime
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    if period == 'current_month':
        start_date = now.replace(day=1)
        # Get last day of month and add 1 day to get first day of next month
        last_day = calendar.monthrange(now.year, now.month)[1]
        if now.month == 12:
            end_date = now.replace(year=now.year + 1, month=1, day=1)
        else:
            end_date = now.replace(month=now.month + 1, day=1)
    elif period == 'current_quarter':
        quarter = (now.month - 1) // 3
        start_month = quarter * 3 + 1
        start_date = now.replace(month=start_month, day=1)
        # End is 3 months later
        end_month = start_month + 3
        if end_month > 12:
            end_date = now.replace(year=now.year + 1, month=end_month - 12, day=1)
        else:
            end_date = now.replace(month=end_month, day=1)
    else:  # current_year
        start_date = now.replace(month=1, day=1)
        end_date = now.replace(year=now.year + 1, month=1, day=1)

    # Use parameterized query to prevent SQL injection
    query = """
        WITH period_spending AS (
            SELECT
                category_id,
                SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) as actual_spent
            FROM transactions
            WHERE transaction_date >= $1
              AND transaction_date < $2
            GROUP BY category_id
        )
        SELECT
            b.id as budget_id,
            c.id as category_id,
            c.name as category_name,
            c.category_type,
            b.amount as budgeted_amount,
            b.period as budget_period,
            COALESCE(ps.actual_spent, 0) as actual_spent,
            b.amount - COALESCE(ps.actual_spent, 0) as remaining,
            CASE
                WHEN b.amount > 0 THEN (COALESCE(ps.actual_spent, 0) / b.amount * 100)
                ELSE 0
            END as percent_used
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        LEFT JOIN period_spending ps ON b.category_id = ps.category_id
        WHERE b.is_active = true
          AND b.start_date <= CURRENT_DATE
          AND (b.end_date IS NULL OR b.end_date >= CURRENT_DATE)
        ORDER BY percent_used DESC
    """

    results = await db.execute_query(query, start_date, end_date)

    budgets = []
    total_budgeted = 0
    total_spent = 0

    for row in results:
        budget_data = {
            "budget_id": str(row['budget_id']),
            "category_id": str(row['category_id']),
            "category_name": row['category_name'],
            "category_type": row['category_type'],
            "budgeted_amount": float(row['budgeted_amount']),
            "actual_spent": float(row['actual_spent']),
            "remaining": float(row['remaining']),
            "percent_used": float(row['percent_used']),
            "status": "over_budget" if row['remaining'] < 0 else "on_track" if row['percent_used'] < 90 else "warning"
        }
        budgets.append(budget_data)
        total_budgeted += budget_data['budgeted_amount']
        total_spent += budget_data['actual_spent']

    return {
        "budgets": budgets,
        "summary": {
            "period": period,
            "total_budgeted": total_budgeted,
            "total_spent": total_spent,
            "total_remaining": total_budgeted - total_spent,
            "budget_count": len(budgets),
            "over_budget_count": sum(1 for b in budgets if b['status'] == 'over_budget')
        }
    }
