"""Database loading utilities."""

import pandas as pd
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from ..database import Transaction, ImportLog, ImportStatus


class DatabaseLoader:
    """Load transformed data into the database."""

    def __init__(self, db: Session):
        self.db = db

    def get_existing_transactions(
        self,
        account_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Get existing transactions for duplicate detection."""
        query = self.db.query(Transaction).filter(
            Transaction.account_id == account_id
        )

        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)

        transactions = query.all()

        if not transactions:
            return pd.DataFrame()

        # Convert to DataFrame
        data = [{
            'transaction_date': t.transaction_date,
            'amount': float(t.amount),
            'description': t.description
        } for t in transactions]

        return pd.DataFrame(data)

    def load_transactions(
        self,
        df: pd.DataFrame,
        account_id: uuid.UUID,
        import_log_id: uuid.UUID
    ) -> Dict[str, int]:
        """Load transactions into database."""
        stats = {
            'processed': 0,
            'imported': 0,
            'failed': 0,
            'duplicate': 0
        }

        for idx, row in df.iterrows():
            stats['processed'] += 1

            try:
                # Check if marked as duplicate
                if row.get('is_duplicate', False):
                    stats['duplicate'] += 1
                    continue

                # Create transaction
                transaction = Transaction(
                    account_id=account_id,
                    transaction_date=row['transaction_date'].date() if pd.notna(row['transaction_date']) else None,
                    post_date=row.get('post_date').date() if pd.notna(row.get('post_date')) else None,
                    description=row['description'],
                    original_description=row.get('original_description'),
                    amount=float(row['amount']),
                    transaction_type=row['transaction_type'],
                    merchant=row.get('merchant'),
                    is_duplicate=False
                )

                self.db.add(transaction)
                stats['imported'] += 1

            except Exception as e:
                stats['failed'] += 1
                print(f"Error loading row {idx}: {e}")
                continue

        # Commit all transactions
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

        return stats

    def create_import_log(
        self,
        filename: str,
        account_id: Optional[uuid.UUID] = None
    ) -> ImportLog:
        """Create a new import log entry."""
        import_log = ImportLog(
            filename=filename,
            account_id=account_id,
            import_status=ImportStatus.pending
        )
        self.db.add(import_log)
        self.db.commit()
        self.db.refresh(import_log)
        return import_log

    def update_import_log(
        self,
        import_log_id: uuid.UUID,
        status: ImportStatus,
        stats: Optional[Dict[str, int]] = None,
        error_details: Optional[Dict[str, Any]] = None
    ):
        """Update import log with results."""
        import_log = self.db.query(ImportLog).filter(
            ImportLog.id == import_log_id
        ).first()

        if not import_log:
            raise ValueError(f"Import log {import_log_id} not found")

        import_log.import_status = status

        if stats:
            import_log.rows_processed = stats.get('processed', 0)
            import_log.rows_imported = stats.get('imported', 0)
            import_log.rows_failed = stats.get('failed', 0)
            import_log.rows_duplicate = stats.get('duplicate', 0)

        if error_details:
            import_log.error_details = error_details

        if status in [ImportStatus.completed, ImportStatus.failed]:
            import_log.completed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(import_log)
        return import_log
