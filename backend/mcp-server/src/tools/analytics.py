"""Analytics-related MCP tools."""

from typing import Optional
from sqlalchemy import text
from decimal import Decimal

from ..database.connection import db


async def get_spending_by_category(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    account_ids: Optional[list[str]] = None,
    category_type: Optional[str] = None
) -> dict:
    """Get spending aggregated by category.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        account_ids: Optional list of account UUIDs
        category_type: Filter by category type ('income' or 'expense')

    Returns:
        Dictionary with spending by category
    """
    with db.get_session() as session:
        query = """
            SELECT
                c.id as category_id,
                c.name as category_name,
                c.category_type,
                c.parent_category_id,
                pc.name as parent_category_name,
                COUNT(t.id) as transaction_count,
                SUM(t.amount) as total_amount,
                AVG(t.amount) as average_amount,
                MIN(t.amount) as min_amount,
                MAX(t.amount) as max_amount
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            LEFT JOIN categories pc ON c.parent_category_id = pc.id
            WHERE t.transaction_type = 'debit'
        """

        params = {}
        if start_date:
            query += " AND t.transaction_date >= :start_date"
            params["start_date"] = start_date

        if end_date:
            query += " AND t.transaction_date <= :end_date"
            params["end_date"] = end_date

        if account_ids:
            query += " AND t.account_id = ANY(:account_ids)"
            params["account_ids"] = account_ids

        if category_type:
            query += " AND c.category_type = :category_type"
            params["category_type"] = category_type

        query += """
            GROUP BY c.id, c.name, c.category_type, c.parent_category_id, pc.name
            ORDER BY total_amount DESC
        """

        result = session.execute(text(query), params)
        rows = result.fetchall()

        categories = []
        total_spending = 0

        for row in rows:
            amount = float(row.total_amount) if isinstance(row.total_amount, Decimal) else row.total_amount
            total_spending += amount

            categories.append({
                "category_id": str(row.category_id),
                "category_name": row.category_name,
                "category_type": row.category_type,
                "parent_category_id": str(row.parent_category_id) if row.parent_category_id else None,
                "parent_category_name": row.parent_category_name,
                "transaction_count": row.transaction_count,
                "total_amount": amount,
                "average_amount": float(row.average_amount) if isinstance(row.average_amount, Decimal) else row.average_amount,
                "min_amount": float(row.min_amount) if isinstance(row.min_amount, Decimal) else row.min_amount,
                "max_amount": float(row.max_amount) if isinstance(row.max_amount, Decimal) else row.max_amount
            })

        # Add percentage of total
        for category in categories:
            category["percentage_of_total"] = (category["total_amount"] / total_spending * 100) if total_spending > 0 else 0

        return {
            "categories": categories,
            "total_spending": total_spending,
            "category_count": len(categories)
        }


async def get_merchant_spending(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    top_n: int = 20
) -> dict:
    """Get spending grouped by merchant.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        top_n: Number of top merchants to return

    Returns:
        Dictionary with merchant spending
    """
    with db.get_session() as session:
        query = """
            SELECT
                t.merchant,
                COUNT(t.id) as transaction_count,
                SUM(t.amount) as total_amount,
                AVG(t.amount) as average_amount,
                MIN(t.transaction_date) as first_transaction,
                MAX(t.transaction_date) as last_transaction
            FROM transactions t
            WHERE t.merchant IS NOT NULL
              AND t.transaction_type = 'debit'
        """

        params = {"top_n": top_n}
        if start_date:
            query += " AND t.transaction_date >= :start_date"
            params["start_date"] = start_date

        if end_date:
            query += " AND t.transaction_date <= :end_date"
            params["end_date"] = end_date

        query += """
            GROUP BY t.merchant
            ORDER BY total_amount DESC
            LIMIT :top_n
        """

        result = session.execute(text(query), params)
        rows = result.fetchall()

        merchants = []
        for row in rows:
            merchants.append({
                "merchant": row.merchant,
                "transaction_count": row.transaction_count,
                "total_amount": float(row.total_amount) if isinstance(row.total_amount, Decimal) else row.total_amount,
                "average_amount": float(row.average_amount) if isinstance(row.average_amount, Decimal) else row.average_amount,
                "first_transaction": row.first_transaction.isoformat() if row.first_transaction else None,
                "last_transaction": row.last_transaction.isoformat() if row.last_transaction else None
            })

        return {
            "merchants": merchants,
            "merchant_count": len(merchants)
        }


async def get_cash_flow(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    granularity: str = "monthly"
) -> dict:
    """Get income vs expenses over time.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        granularity: Time granularity ('daily', 'weekly', 'monthly')

    Returns:
        Dictionary with cash flow data
    """
    with db.get_session() as session:
        # Determine date truncation based on granularity
        date_trunc_map = {
            "daily": "day",
            "weekly": "week",
            "monthly": "month"
        }
        date_trunc = date_trunc_map.get(granularity, "month")

        query = f"""
            SELECT
                DATE_TRUNC(:date_trunc, t.transaction_date) as period,
                SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END) as income,
                SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END) as expenses,
                SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE -t.amount END) as net_flow,
                COUNT(t.id) as transaction_count
            FROM transactions t
            WHERE 1=1
        """

        params = {"date_trunc": date_trunc}
        if start_date:
            query += " AND t.transaction_date >= :start_date"
            params["start_date"] = start_date

        if end_date:
            query += " AND t.transaction_date <= :end_date"
            params["end_date"] = end_date

        query += """
            GROUP BY period
            ORDER BY period ASC
        """

        result = session.execute(text(query), params)
        rows = result.fetchall()

        periods = []
        total_income = 0
        total_expenses = 0

        for row in rows:
            income = float(row.income) if isinstance(row.income, Decimal) else row.income
            expenses = float(row.expenses) if isinstance(row.expenses, Decimal) else row.expenses
            net_flow = float(row.net_flow) if isinstance(row.net_flow, Decimal) else row.net_flow

            total_income += income
            total_expenses += expenses

            periods.append({
                "period": row.period.isoformat() if row.period else None,
                "income": income,
                "expenses": expenses,
                "net_flow": net_flow,
                "transaction_count": row.transaction_count
            })

        return {
            "periods": periods,
            "granularity": granularity,
            "summary": {
                "total_income": total_income,
                "total_expenses": total_expenses,
                "net_total": total_income - total_expenses,
                "average_monthly_income": total_income / len(periods) if periods else 0,
                "average_monthly_expenses": total_expenses / len(periods) if periods else 0
            }
        }
