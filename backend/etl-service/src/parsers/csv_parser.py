"""CSV parsing utilities."""

import pandas as pd
import chardet
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import csv

from ..config import settings


class CSVParser:
    """Parse CSV files with automatic encoding and delimiter detection."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.encoding: Optional[str] = None
        self.delimiter: Optional[str] = None

    def detect_encoding(self) -> str:
        """Detect file encoding."""
        with open(self.file_path, 'rb') as f:
            raw_data = f.read(10000)  # Read first 10KB
            result = chardet.detect(raw_data)
            self.encoding = result['encoding']

            # Fallback to UTF-8 if detection fails
            if not self.encoding or result['confidence'] < 0.7:
                self.encoding = settings.default_encoding

        return self.encoding

    def detect_delimiter(self, encoding: Optional[str] = None) -> str:
        """Detect CSV delimiter."""
        if encoding is None:
            encoding = self.encoding or self.detect_encoding()

        with open(self.file_path, 'r', encoding=encoding) as f:
            # Read first few lines
            sample = f.read(4096)

        # Use csv.Sniffer to detect delimiter
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample)
            self.delimiter = dialect.delimiter
        except Exception:
            # Default to comma
            self.delimiter = ','

        return self.delimiter

    def read_csv(
        self,
        encoding: Optional[str] = None,
        delimiter: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """Read CSV file into DataFrame."""
        if encoding is None:
            encoding = self.encoding or self.detect_encoding()
        if delimiter is None:
            delimiter = self.delimiter or self.detect_delimiter(encoding)

        try:
            df = pd.read_csv(
                self.file_path,
                encoding=encoding,
                delimiter=delimiter,
                **kwargs
            )
            return df
        except UnicodeDecodeError:
            # Try fallback encodings
            for fallback_encoding in settings.encoding_fallbacks:
                try:
                    df = pd.read_csv(
                        self.file_path,
                        encoding=fallback_encoding,
                        delimiter=delimiter,
                        **kwargs
                    )
                    self.encoding = fallback_encoding
                    return df
                except UnicodeDecodeError:
                    continue
            raise

    def preview(
        self,
        nrows: int = 10,
        encoding: Optional[str] = None,
        delimiter: Optional[str] = None
    ) -> Dict:
        """Preview CSV file."""
        if encoding is None:
            encoding = self.detect_encoding()
        if delimiter is None:
            delimiter = self.detect_delimiter(encoding)

        # Read sample
        df_sample = self.read_csv(
            encoding=encoding,
            delimiter=delimiter,
            nrows=nrows
        )

        # Get total row count
        with open(self.file_path, 'r', encoding=encoding) as f:
            total_rows = sum(1 for _ in f) - 1  # Subtract header

        # Convert all values to strings for Pydantic validation
        # Replace NaN with empty string
        df_sample = df_sample.fillna('')
        sample_rows = df_sample.astype(str).values.tolist()

        return {
            "headers": df_sample.columns.tolist(),
            "sample_rows": sample_rows,
            "total_rows": total_rows,
            "detected_delimiter": delimiter,
            "detected_encoding": encoding
        }

    def validate_columns(
        self,
        required_columns: List[str],
        column_mapping: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, List[str]]:
        """Validate that required columns exist."""
        df = self.read_csv(nrows=1)
        actual_columns = df.columns.tolist()

        if column_mapping:
            # Check if mapped columns exist
            mapped_columns = [column_mapping.get(req, req) for req in required_columns]
            missing = [col for col in mapped_columns if col not in actual_columns]
        else:
            missing = [col for col in required_columns if col not in actual_columns]

        return len(missing) == 0, missing
