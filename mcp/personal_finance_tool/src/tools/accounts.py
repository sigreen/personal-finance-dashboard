"""Account-related MCP tools."""
from typing import Optional
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parse date string to date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        logger.warning(f"Invalid date format: {date_str}")
        return None


async def get_account_summary(db, date_range: Optional[str] = None):
    """Get summary of all accounts with current balances.

    Args:
        db: Database connection
        date_range: Optional date range filter (e.g., "2024-01-01,2024-12-31")

    Returns:
        List of accounts with balances
    """
    query = """
        SELECT
            a.id,
            a.account_name,
            a.institution_name,
            a.account_type,
            a.currency,
            a.account_number_last4,
            COUNT(t.id) as transaction_count,
            COALESCE(
                SUM(CASE
                    WHEN t.transaction_type = 'credit' THEN t.amount
                    ELSE -t.amount
                END),
                0
            ) as balance,
            MAX(t.transaction_date) as last_transaction_date
        FROM accounts a
        LEFT JOIN transactions t ON a.id = t.account_id
        WHERE a.is_active = true
    """

    params = []
    if date_range:
        try:
            start_str, end_str = date_range.split(',')
            start_date = parse_date(start_str.strip())
            end_date = parse_date(end_str.strip())
            if start_date and end_date:
                query += " AND t.transaction_date BETWEEN $1 AND $2"
                params.extend([start_date, end_date])
        except ValueError:
            logger.warning(f"Invalid date_range format: {date_range}")

    query += """
        GROUP BY a.id, a.account_name, a.institution_name, a.account_type,
                 a.currency, a.account_number_last4
        ORDER BY a.institution_name, a.account_name
    """

    results = await db.execute_query(query, *params)

    accounts = []
    for row in results:
        accounts.append({
            "id": str(row['id']),
            "account_name": row['account_name'],
            "institution_name": row['institution_name'],
            "account_type": row['account_type'],
            "currency": row['currency'],
            "account_number_last4": row['account_number_last4'],
            "transaction_count": row['transaction_count'],
            "balance": float(row['balance']),
            "last_transaction_date": row['last_transaction_date'].isoformat() if row['last_transaction_date'] else None
        })

    return {
        "accounts": accounts,
        "total_accounts": len(accounts),
        "total_balance": sum(acc['balance'] for acc in accounts)
    }


async def get_account_details(db, account_id: str):
    """Get detailed information about a specific account.

    Args:
        db: Database connection
        account_id: UUID of the account

    Returns:
        Account details with transaction statistics
    """
    query = """
        SELECT
            a.*,
            COUNT(t.id) as total_transactions,
            COALESCE(
                SUM(CASE
                    WHEN t.transaction_type = 'credit' THEN t.amount
                    ELSE -t.amount
                END),
                0
            ) as current_balance,
            MIN(t.transaction_date) as first_transaction_date,
            MAX(t.transaction_date) as last_transaction_date,
            COALESCE(
                SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END),
                0
            ) as total_credits,
            COALESCE(
                SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END),
                0
            ) as total_debits
        FROM accounts a
        LEFT JOIN transactions t ON a.id = t.account_id
        WHERE a.id = $1
        GROUP BY a.id
    """

    result = await db.execute_one(query, account_id)

    if not result:
        raise ValueError(f"Account {account_id} not found")

    return {
        "id": str(result['id']),
        "account_name": result['account_name'],
        "institution_name": result['institution_name'],
        "account_type": result['account_type'],
        "currency": result['currency'],
        "account_number_last4": result['account_number_last4'],
        "is_active": result['is_active'],
        "notes": result['notes'],
        "created_at": result['created_at'].isoformat(),
        "updated_at": result['updated_at'].isoformat(),
        "statistics": {
            "total_transactions": result['total_transactions'],
            "current_balance": float(result['current_balance']),
            "first_transaction_date": result['first_transaction_date'].isoformat() if result['first_transaction_date'] else None,
            "last_transaction_date": result['last_transaction_date'].isoformat() if result['last_transaction_date'] else None,
            "total_credits": float(result['total_credits']),
            "total_debits": float(result['total_debits'])
        }
    }
