"""Account-related MCP tools."""

from typing import Optional
from sqlalchemy import text
from decimal import Decimal

from ..database.connection import db


async def get_account_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> dict:
    """Get summary of all accounts with transaction statistics.

    Args:
        start_date: Optional start date for transaction stats
        end_date: Optional end date for transaction stats

    Returns:
        Dictionary with account summaries
    """
    with db.get_session() as session:
        # Get accounts with transaction statistics
        query = """
            SELECT
                a.id,
                a.account_type,
                a.institution_name,
                a.account_name,
                a.account_number_last4,
                a.currency,
                a.is_active,
                a.created_at,
                COUNT(t.id) as transaction_count,
                COALESCE(SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END), 0) as total_debits,
                COALESCE(SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END), 0) as total_credits,
                MIN(t.transaction_date) as earliest_transaction,
                MAX(t.transaction_date) as latest_transaction
            FROM accounts a
            LEFT JOIN transactions t ON a.id = t.account_id
        """

        params = {}
        if start_date or end_date:
            query += " WHERE 1=1"
            if start_date:
                query += " AND t.transaction_date >= :start_date"
                params["start_date"] = start_date
            if end_date:
                query += " AND t.transaction_date <= :end_date"
                params["end_date"] = end_date

        query += """
            GROUP BY a.id, a.account_type, a.institution_name, a.account_name,
                     a.account_number_last4, a.currency, a.is_active, a.created_at
            ORDER BY a.account_name
        """

        result = session.execute(text(query), params)
        rows = result.fetchall()

        accounts = []
        for row in rows:
            accounts.append({
                "id": str(row.id),
                "account_type": row.account_type,
                "institution_name": row.institution_name,
                "account_name": row.account_name,
                "account_number_last4": row.account_number_last4,
                "currency": row.currency,
                "is_active": row.is_active,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "statistics": {
                    "transaction_count": row.transaction_count,
                    "total_debits": float(row.total_debits) if isinstance(row.total_debits, Decimal) else row.total_debits,
                    "total_credits": float(row.total_credits) if isinstance(row.total_credits, Decimal) else row.total_credits,
                    "earliest_transaction": row.earliest_transaction.isoformat() if row.earliest_transaction else None,
                    "latest_transaction": row.latest_transaction.isoformat() if row.latest_transaction else None
                }
            })

        return {
            "accounts": accounts,
            "total_accounts": len(accounts),
            "active_accounts": sum(1 for a in accounts if a["is_active"])
        }
