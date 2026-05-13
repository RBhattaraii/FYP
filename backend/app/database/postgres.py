"""
PostgreSQL Database Connection using asyncpg
No SQLAlchemy, No ORM - Direct SQL queries only
"""

import os
import asyncpg
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Global connection pool variable
pool: Optional[asyncpg.Pool] = None


async def create_pool():
    """
    Create a connection pool to PostgreSQL database.
    
    Connection pool maintains multiple database connections that can be reused,
    which is more efficient than creating a new connection for each request.
    
    This function should be called once when the FastAPI app starts.
    """
    global pool
    
    # Get database URL from environment variables
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")
    
    # Create connection pool
    # min_size: minimum number of connections to keep open
    # max_size: maximum number of connections allowed
    pool = await asyncpg.create_pool(
        database_url,
        min_size=2,      # Keep at least 2 connections open
        max_size=10,     # Allow up to 10 concurrent connections
        command_timeout=60  # Timeout for queries (60 seconds)
    )
    
    print("✅ PostgreSQL connection pool created successfully")
    return pool


async def close_pool():
    """
    Close the connection pool.
    
    This function should be called when the FastAPI app shuts down
    to properly close all database connections.
    """
    global pool
    
    if pool:
        await pool.close()
        print("✅ PostgreSQL connection pool closed")


async def get_db() -> asyncpg.Connection:
    """
    Get a database connection from the pool.
    
    This function is used as a dependency in FastAPI routes.
    It acquires a connection from the pool and returns it.
    
    Usage in routes:
        async def my_route(db = Depends(get_db)):
            result = await db.fetch("SELECT * FROM users")
    
    Returns:
        asyncpg.Connection: A database connection from the pool
    """
    global pool
    
    if not pool:
        raise RuntimeError("Database pool not initialized. Call create_pool() first.")
    
    # Acquire a connection from the pool
    # The connection will be automatically returned to the pool when done
    async with pool.acquire() as connection:
        yield connection


# Example query functions demonstrating parameterized queries

async def example_safe_query(db: asyncpg.Connection, user_email: str):
    """
    ✅ SAFE: Using parameterized query with $1 placeholder
    
    This prevents SQL injection attacks because user input is treated as data,
    not as part of the SQL command.
    """
    query = "SELECT * FROM users WHERE email = $1"
    result = await db.fetchrow(query, user_email)
    return result


async def example_unsafe_query_DO_NOT_USE(db: asyncpg.Connection, user_email: str):
    """
    ❌ UNSAFE: Never do this! SQL injection vulnerability!
    
    This is vulnerable to SQL injection because user input is directly
    inserted into the SQL string.
    
    Example attack:
        user_email = "'; DROP TABLE users; --"
        This would delete the entire users table!
    """
    # DO NOT USE THIS PATTERN!
    query = f"SELECT * FROM users WHERE email = '{user_email}'"
    result = await db.fetchrow(query)
    return result


# Common database operations

async def fetch_one(db: asyncpg.Connection, query: str, *args):
    """
    Fetch a single row from the database.
    
    Args:
        db: Database connection
        query: SQL query with $1, $2, etc. placeholders
        *args: Values to substitute for placeholders
    
    Returns:
        A single row as a Record object, or None if no rows found
    
    Example:
        user = await fetch_one(db, "SELECT * FROM users WHERE id = $1", user_id)
    """
    return await db.fetchrow(query, *args)


async def fetch_all(db: asyncpg.Connection, query: str, *args):
    """
    Fetch all rows from the database.
    
    Args:
        db: Database connection
        query: SQL query with $1, $2, etc. placeholders
        *args: Values to substitute for placeholders
    
    Returns:
        List of rows as Record objects
    
    Example:
        users = await fetch_all(db, "SELECT * FROM users WHERE role = $1", "admin")
    """
    return await db.fetch(query, *args)


async def execute_query(db: asyncpg.Connection, query: str, *args):
    """
    Execute a query that doesn't return rows (INSERT, UPDATE, DELETE).
    
    Args:
        db: Database connection
        query: SQL query with $1, $2, etc. placeholders
        *args: Values to substitute for placeholders
    
    Returns:
        Status string (e.g., "INSERT 0 1", "UPDATE 1", "DELETE 1")
    
    Example:
        await execute_query(
            db,
            "INSERT INTO users (email, password_hash) VALUES ($1, $2)",
            email,
            hashed_password
        )
    """
    return await db.execute(query, *args)


async def execute_many(db: asyncpg.Connection, query: str, args_list):
    """
    Execute the same query multiple times with different parameters.
    Useful for bulk inserts.
    
    Args:
        db: Database connection
        query: SQL query with $1, $2, etc. placeholders
        args_list: List of tuples, each containing values for one execution
    
    Example:
        await execute_many(
            db,
            "INSERT INTO products (name, price) VALUES ($1, $2)",
            [("Product 1", 10.99), ("Product 2", 20.99)]
        )
    """
    return await db.executemany(query, args_list)


# Transaction example

async def example_transaction(db: asyncpg.Connection):
    """
    Example of using a transaction.
    
    Transactions ensure that either all operations succeed or none do.
    If any operation fails, all changes are rolled back.
    """
    async with db.transaction():
        # All queries here are part of the same transaction
        await db.execute(
            "INSERT INTO users (email, password_hash) VALUES ($1, $2)",
            "user@example.com",
            "hashed_password"
        )
        await db.execute(
            "INSERT INTO user_profiles (user_id, bio) VALUES ($1, $2)",
            "user_id",
            "User bio"
        )
        # If any query fails, both inserts are rolled back
        # If all succeed, changes are committed automatically
