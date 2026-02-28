"""Pydantic schemas for API validation."""

from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# Enums
class AccountTypeEnum(str, Enum):
    checking = "checking"
    savings = "savings"
    credit_card = "credit_card"
    brokerage = "brokerage"
    loan = "loan"


class TransactionTypeEnum(str, Enum):
    debit = "debit"
    credit = "credit"


class ImportStatusEnum(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


# Request/Response Schemas
class AccountCreate(BaseModel):
    account_type: AccountTypeEnum
    institution_name: str = Field(..., max_length=255)
    account_name: str = Field(..., max_length=255)
    account_number_last4: Optional[str] = Field(None, max_length=4)
    currency: str = Field("USD", max_length=3)
    notes: Optional[str] = None


class AccountResponse(BaseModel):
    id: UUID4
    account_type: AccountTypeEnum
    institution_name: str
    account_name: str
    account_number_last4: Optional[str]
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    id: UUID4
    account_id: UUID4
    transaction_date: date
    post_date: Optional[date]
    description: str
    original_description: Optional[str]
    amount: float
    transaction_type: TransactionTypeEnum
    merchant: Optional[str]
    category_id: Optional[UUID4]
    is_duplicate: bool
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class ImportLogResponse(BaseModel):
    id: UUID4
    filename: str
    account_id: Optional[UUID4]
    import_status: ImportStatusEnum
    rows_processed: int
    rows_imported: int
    rows_failed: int
    rows_duplicate: int
    error_details: Optional[Dict[str, Any]]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    import_id: UUID4
    filename: str
    status: str
    message: str


class CSVPreview(BaseModel):
    headers: list[str]
    sample_rows: list[list[str]]
    total_rows: int
    detected_delimiter: str
    detected_encoding: str


class ImportRequest(BaseModel):
    account_id: UUID4
    column_mapping: Optional[Dict[str, str]] = None
    date_format: Optional[str] = None  # Auto-detect if not provided
    has_header: bool = True
    negative_means_debit: bool = True  # True for Chase (negative=debit), False for Amex (positive=debit)
