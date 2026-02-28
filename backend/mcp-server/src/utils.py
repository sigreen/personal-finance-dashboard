"""Shared utility functions for MCP server tools."""
from typing import Optional
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parse date string to date object.

    Args:
        date_str: Date string in YYYY-MM-DD format

    Returns:
        Parsed date object or None if invalid/empty
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        logger.warning(f"Invalid date format: {date_str}")
        return None
