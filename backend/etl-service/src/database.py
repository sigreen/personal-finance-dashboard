"""Database connection and models."""

from sqlalchemy import create_engine, Column, String, Numeric, DateTime, Boolean, Date, Text, Enum, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import enum

from .config import settings

# Create database engine
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Enum types
class AccountType(str, enum.Enum):
    checking = "checking"
    savings = "savings"
    credit_card = "credit_card"
    brokerage = "brokerage"
    loan = "loan"


class TransactionType(str, enum.Enum):
    debit = "debit"
    credit = "credit"


class ImportStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


# Database Models
class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_type = Column(Enum(AccountType), nullable=False)
    institution_name = Column(String(255), nullable=False)
    account_name = Column(String(255), nullable=False)
    account_number_last4 = Column(String(4))
    currency = Column(String(3), default="USD")
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=False)
    transaction_date = Column(Date, nullable=False)
    post_date = Column(Date)
    description = Column(Text, nullable=False)
    original_description = Column(Text)
    amount = Column(Numeric(15, 2), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    category_id = Column(UUID(as_uuid=True))
    merchant = Column(String(255))
    notes = Column(Text)
    is_duplicate = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ImportLog(Base):
    __tablename__ = "import_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    account_id = Column(UUID(as_uuid=True))
    import_status = Column(Enum(ImportStatus), nullable=False, default=ImportStatus.pending)
    rows_processed = Column(Integer, default=0)
    rows_imported = Column(Integer, default=0)
    rows_failed = Column(Integer, default=0)
    rows_duplicate = Column(Integer, default=0)
    error_details = Column(JSONB)
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class CSVMappingRule(Base):
    __tablename__ = "csv_mapping_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_name = Column(String(255), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    column_mappings = Column(JSONB, nullable=False)
    date_format = Column(String(50), default="MM/DD/YYYY")
    amount_format = Column(String(50), default="US")
    has_header = Column(Boolean, default=True)
    delimiter = Column(String(1), default=",")
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# Database dependency
def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
