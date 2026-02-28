"""Database connection management for MCP server."""
import asyncpg
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages PostgreSQL database connections."""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize database connection manager.

        Args:
            database_url: PostgreSQL connection URL. If None, reads from DATABASE_URL env var.
        """
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL must be provided or set in environment")

        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Create connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise

    async def disconnect(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    async def execute_query(self, query: str, *args):
        """Execute a query and return results.

        Args:
            query: SQL query string
            *args: Query parameters

        Returns:
            List of records
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Call connect() first.")

        async with self.pool.acquire() as conn:
            try:
                return await conn.fetch(query, *args)
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise

    async def execute_one(self, query: str, *args):
        """Execute a query and return single result.

        Args:
            query: SQL query string
            *args: Query parameters

        Returns:
            Single record or None
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Call connect() first.")

        async with self.pool.acquire() as conn:
            try:
                return await conn.fetchrow(query, *args)
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise
