"""Transaction data transformation utilities."""

import pandas as pd
import re
from typing import Optional, Dict
from datetime import datetime
from dateutil import parser as date_parser


class TransactionTransformer:
    """Transform and normalize transaction data."""

    @staticmethod
    def detect_date_format(dates_sample: pd.Series) -> Optional[str]:
        """Auto-detect date format from sample data.

        Args:
            dates_sample: Series of date strings to analyze

        Returns:
            Best matching date format string, or None for flexible parsing
        """
        # Common date formats to try
        formats = [
            '%m/%d/%Y',  # 12/30/2025
            '%m/%d/%y',  # 12/30/25
            '%Y-%m-%d',  # 2025-12-30
            '%d/%m/%Y',  # 30/12/2025
            '%d/%m/%y',  # 30/12/25
            '%Y/%m/%d',  # 2025/12/30
            '%m-%d-%Y',  # 12-30-2025
            '%m-%d-%y',  # 12-30-25
        ]

        # Take non-null sample
        sample = dates_sample.dropna().head(10)
        if len(sample) == 0:
            return None

        # Try each format and count successes
        format_scores = {}
        for fmt in formats:
            success_count = 0
            for date_val in sample:
                try:
                    datetime.strptime(str(date_val), fmt)
                    success_count += 1
                except:
                    pass
            if success_count > 0:
                format_scores[fmt] = success_count

        # Return format with highest success rate
        if format_scores:
            best_format = max(format_scores, key=format_scores.get)
            # Only use if it works for most samples
            if format_scores[best_format] >= len(sample) * 0.8:
                return best_format

        # Fall back to None (use flexible dateutil parser)
        return None

    @staticmethod
    def parse_date(
        date_value: str,
        date_format: Optional[str] = None
    ) -> Optional[datetime]:
        """Parse date string to datetime."""
        if pd.isna(date_value) or not date_value:
            return None

        try:
            if date_format:
                return datetime.strptime(str(date_value), date_format)
            else:
                # Use dateutil parser for flexible parsing
                # Force timezone-naive to prevent date shifting
                parsed = date_parser.parse(str(date_value), ignoretz=True)
                # Ensure we return a naive datetime (strip any timezone info)
                return parsed.replace(tzinfo=None) if parsed else None
        except Exception:
            return None

    @staticmethod
    def parse_amount(amount_value: str) -> Optional[float]:
        """Parse amount string to float."""
        if pd.isna(amount_value) or not amount_value:
            return None

        # Convert to string and clean
        amount_str = str(amount_value).strip()

        # Remove currency symbols and commas
        amount_str = re.sub(r'[$,]', '', amount_str)

        # Handle parentheses as negative (accounting format)
        if '(' in amount_str and ')' in amount_str:
            amount_str = '-' + amount_str.replace('(', '').replace(')', '')

        try:
            return float(amount_str)
        except ValueError:
            return None

    @staticmethod
    def determine_transaction_type(amount: float, negative_means_debit: bool = True) -> str:
        """Determine transaction type from amount.

        Args:
            amount: The transaction amount (can be positive or negative)
            negative_means_debit: If True (Chase style), negative=debit, positive=credit.
                                 If False (Amex style), positive=debit, negative=credit.
        """
        if negative_means_debit:
            # Chase convention: negative = debit (expense), positive = credit (refund/payment)
            return "debit" if amount < 0 else "credit"
        else:
            # Amex convention: positive = debit (expense), negative = credit (payment/refund)
            return "debit" if amount > 0 else "credit"

    @staticmethod
    def extract_merchant(description: str) -> Optional[str]:
        """Extract merchant name from description."""
        if pd.isna(description) or not description:
            return None

        # Clean up description
        merchant = str(description).strip()

        # Remove common prefixes
        prefixes = [
            r'^POS\s+',
            r'^DEBIT\s+CARD\s+',
            r'^CHECK\s+#?\d+\s+',
            r'^ACH\s+',
            r'^ONLINE\s+',
            r'^ATM\s+',
        ]

        for prefix in prefixes:
            merchant = re.sub(prefix, '', merchant, flags=re.IGNORECASE)

        # Take first part (often the merchant name)
        # Remove location/date info that often comes after
        merchant = re.split(r'\s+\d{2}/\d{2}|\s+#\d+', merchant)[0]

        return merchant.strip()[:255]  # Limit to 255 chars

    @staticmethod
    def clean_description(description: str) -> str:
        """Clean and normalize description."""
        if pd.isna(description) or not description:
            return ""

        # Clean whitespace
        clean = ' '.join(str(description).split())

        return clean

    def transform_dataframe(
        self,
        df: pd.DataFrame,
        column_mapping: Dict[str, str],
        date_format: Optional[str] = None,
        negative_means_debit: bool = True
    ) -> pd.DataFrame:
        """Transform DataFrame to standardized format."""
        # Rename columns based on mapping
        df_transformed = df.rename(columns=column_mapping)

        # Ensure required columns exist
        required = ['transaction_date', 'description', 'amount']
        for col in required:
            if col not in df_transformed.columns:
                raise ValueError(f"Required column '{col}' not found after mapping")

        # Auto-detect date format if not provided
        if not date_format:
            detected_format = self.detect_date_format(df_transformed['transaction_date'])
            if detected_format:
                date_format = detected_format
                print(f"DEBUG: Auto-detected date format: {date_format}")

        # Parse dates
        df_transformed['transaction_date'] = df_transformed['transaction_date'].apply(
            lambda x: self.parse_date(x, date_format)
        )

        # Parse amounts
        df_transformed['amount'] = df_transformed['amount'].apply(self.parse_amount)

        # Determine transaction type BEFORE converting to absolute value
        df_transformed['transaction_type'] = df_transformed['amount'].apply(
            lambda x: self.determine_transaction_type(x, negative_means_debit)
        )
        df_transformed['amount'] = df_transformed['amount'].abs()

        # Clean descriptions
        df_transformed['original_description'] = df_transformed['description']
        df_transformed['description'] = df_transformed['description'].apply(
            self.clean_description
        )

        # Extract merchant
        df_transformed['merchant'] = df_transformed['description'].apply(
            self.extract_merchant
        )

        # Handle optional post_date column
        if 'post_date' in df_transformed.columns:
            df_transformed['post_date'] = df_transformed['post_date'].apply(
                lambda x: self.parse_date(x, date_format)
            )
        else:
            df_transformed['post_date'] = df_transformed['transaction_date']

        # Drop rows with invalid data
        df_transformed = df_transformed.dropna(subset=['transaction_date', 'amount'])

        # Filter out zero amounts
        df_transformed = df_transformed[df_transformed['amount'] > 0]

        return df_transformed

    @staticmethod
    def detect_duplicates(
        df: pd.DataFrame,
        existing_transactions: pd.DataFrame
    ) -> pd.DataFrame:
        """Mark potential duplicate transactions."""
        if existing_transactions.empty:
            df['is_duplicate'] = False
            return df

        # Create composite key for duplicate detection
        df['_dup_key'] = (
            df['transaction_date'].astype(str) + '_' +
            df['amount'].astype(str) + '_' +
            df['description'].str[:50]
        )

        existing_transactions['_dup_key'] = (
            existing_transactions['transaction_date'].astype(str) + '_' +
            existing_transactions['amount'].astype(str) + '_' +
            existing_transactions['description'].str[:50]
        )

        # Mark duplicates
        df['is_duplicate'] = df['_dup_key'].isin(existing_transactions['_dup_key'])

        # Clean up
        df = df.drop(columns=['_dup_key'])

        return df
