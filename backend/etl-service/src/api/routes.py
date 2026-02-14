"""API routes for ETL service."""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import shutil
from pathlib import Path

from ..database import get_db, Account, ImportLog, ImportStatus
from ..schemas import (
    AccountCreate,
    AccountResponse,
    UploadResponse,
    ImportLogResponse,
    CSVPreview,
    ImportRequest
)
from ..config import settings
from ..parsers.csv_parser import CSVParser
from ..transformers.transaction_transformer import TransactionTransformer
from ..loaders.database_loader import DatabaseLoader

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name}


@router.post("/accounts", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db)
):
    """Create a new account."""
    db_account = Account(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.get("/accounts", response_model=List[AccountResponse])
async def list_accounts(
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """List all accounts."""
    query = db.query(Account)
    if active_only:
        query = query.filter(Account.is_active == True)
    return query.all()


@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get account by ID."""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a CSV file."""
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {settings.allowed_extensions}"
        )

    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_file_size} bytes"
        )

    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = upload_dir / unique_filename

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Create import log
    loader = DatabaseLoader(db)
    import_log = loader.create_import_log(filename=file.filename)

    return UploadResponse(
        import_id=import_log.id,
        filename=file.filename,
        status="uploaded",
        message=f"File uploaded successfully. Import ID: {import_log.id}"
    )


@router.get("/upload/{import_id}/preview", response_model=CSVPreview)
async def preview_csv(
    import_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Preview uploaded CSV file."""
    import_log = db.query(ImportLog).filter(ImportLog.id == import_id).first()
    if not import_log:
        raise HTTPException(status_code=404, detail="Import not found")

    # Find uploaded file
    upload_dir = Path(settings.upload_dir)
    file_pattern = f"*_{import_log.filename}"
    matching_files = list(upload_dir.glob(file_pattern))

    if not matching_files:
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    file_path = matching_files[0]

    # Parse and preview
    try:
        parser = CSVParser(str(file_path))
        preview_data = parser.preview(nrows=10)
        return CSVPreview(**preview_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preview file: {str(e)}")


@router.post("/import/{import_id}/process")
async def process_import(
    import_id: uuid.UUID,
    import_request: ImportRequest,
    db: Session = Depends(get_db)
):
    """Process CSV import."""
    import_log = db.query(ImportLog).filter(ImportLog.id == import_id).first()
    if not import_log:
        raise HTTPException(status_code=404, detail="Import not found")

    if import_log.import_status != ImportStatus.pending:
        raise HTTPException(
            status_code=400,
            detail=f"Import already {import_log.import_status.value}"
        )

    # Verify account exists
    account = db.query(Account).filter(Account.id == import_request.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Find uploaded file
    upload_dir = Path(settings.upload_dir)
    file_pattern = f"*_{import_log.filename}"
    matching_files = list(upload_dir.glob(file_pattern))

    if not matching_files:
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    file_path = matching_files[0]

    # Update import log
    loader = DatabaseLoader(db)
    loader.update_import_log(
        import_id,
        ImportStatus.processing,
        None
    )

    try:
        # Parse CSV
        parser = CSVParser(str(file_path))
        df = parser.read_csv()

        # Default column mapping if not provided
        if not import_request.column_mapping:
            # Try to auto-detect common column names
            column_mapping = {}
            headers_lower = {h.lower(): h for h in df.columns}

            # Map common variations
            date_cols = ['date', 'transaction date', 'trans date', 'posting date']
            desc_cols = ['description', 'desc', 'memo', 'transaction']
            amount_cols = ['amount', 'debit', 'credit']

            for col in date_cols:
                if col in headers_lower:
                    column_mapping['transaction_date'] = headers_lower[col]
                    break

            for col in desc_cols:
                if col in headers_lower:
                    column_mapping['description'] = headers_lower[col]
                    break

            for col in amount_cols:
                if col in headers_lower:
                    column_mapping['amount'] = headers_lower[col]
                    break

            # Invert mapping (we need source -> target)
            import_request.column_mapping = {v: k for k, v in column_mapping.items()}

        # Transform data
        transformer = TransactionTransformer()
        df_transformed = transformer.transform_dataframe(
            df,
            import_request.column_mapping,
            import_request.date_format
        )

        # Get existing transactions for duplicate detection
        if not df_transformed.empty:
            min_date = df_transformed['transaction_date'].min()
            max_date = df_transformed['transaction_date'].max()
            existing_df = loader.get_existing_transactions(
                import_request.account_id,
                min_date,
                max_date
            )

            # Detect duplicates
            df_transformed = transformer.detect_duplicates(df_transformed, existing_df)

        # Load into database
        stats = loader.load_transactions(
            df_transformed,
            import_request.account_id,
            import_id
        )

        # Update import log
        import_log = loader.update_import_log(
            import_id,
            ImportStatus.completed,
            stats
        )

        # Update account_id in import log
        import_log.account_id = import_request.account_id
        db.commit()

        return {
            "import_id": import_id,
            "status": "completed",
            "stats": stats
        }

    except Exception as e:
        # Update import log with error
        loader.update_import_log(
            import_id,
            ImportStatus.failed,
            error_details={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.get("/import/{import_id}/status", response_model=ImportLogResponse)
async def get_import_status(
    import_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get import status."""
    import_log = db.query(ImportLog).filter(ImportLog.id == import_id).first()
    if not import_log:
        raise HTTPException(status_code=404, detail="Import not found")
    return import_log


@router.get("/imports", response_model=List[ImportLogResponse])
async def list_imports(
    account_id: Optional[uuid.UUID] = None,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """List import history."""
    query = db.query(ImportLog)
    if account_id:
        query = query.filter(ImportLog.account_id == account_id)
    query = query.order_by(ImportLog.created_at.desc()).limit(limit)
    return query.all()
