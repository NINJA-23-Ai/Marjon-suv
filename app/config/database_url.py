from urllib.parse import urlsplit, urlunsplit

SUPPORTED_ASYNC_DRIVER = "postgresql+asyncpg"
SUPPORTED_SCHEMES = {"postgres", "postgresql", SUPPORTED_ASYNC_DRIVER}


class DatabaseUrlError(ValueError):
    """Raised when DATABASE_URL cannot be used by SQLAlchemy async engine."""


def normalize_database_url(raw_url: str | None) -> str:
    """Return an async SQLAlchemy PostgreSQL URL with a clear error for bad input."""

    database_url = (raw_url or "").strip().strip('"').strip("'")
    if not database_url:
        raise DatabaseUrlError(
            "DATABASE_URL bo'sh. PostgreSQL connection string kiriting, masalan: "
            "postgresql+asyncpg://user:password@host:5432/dbname"
        )

    parsed_url = urlsplit(database_url)
    if (
        parsed_url.scheme not in SUPPORTED_SCHEMES
        or not parsed_url.netloc
        or not parsed_url.path.strip("/")
    ):
        raise DatabaseUrlError(
            "DATABASE_URL noto'g'ri formatda. Railway/PostgreSQL URL to'liq connection "
            "string bo'lishi kerak, masalan: "
            "postgresql+asyncpg://user:password@host:5432/dbname"
        )

    return urlunsplit(
        (
            SUPPORTED_ASYNC_DRIVER,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.query,
            parsed_url.fragment,
        )
    )
