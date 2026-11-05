
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Find the project root from this file's location.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Load credentials from the project's .env file.
load_dotenv(PROJECT_ROOT / ".env")


def get_engine():
    """Create a SQLAlchemy engine for PostgreSQL."""

    required_vars = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    missing = [name for name in required_vars if not os.getenv(name)]

    if missing:
        raise ValueError(
            f"Missing environment variables: {', '.join(missing)}"
        )

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
    )

    return create_engine(url, pool_pre_ping=True)


def test_connection():
    """Verify the database connection."""

    engine = get_engine()

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT current_database(), CURRENT_DATE")
            )
            database_name, today = result.one()

            print(f"Connected successfully to: {database_name}")
            print(f"Database date: {today}")

    finally:
        engine.dispose()


if __name__ == "__main__":
    test_connection()
