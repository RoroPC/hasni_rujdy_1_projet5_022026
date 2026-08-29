"""Cree le schema de base de donnees configure dans ``DATABASE_URL``."""

from app.db.database import init_db


def main() -> None:
    """Initialise les tables SQLAlchemy de maniere idempotente."""
    init_db()
    print("Schema de base de donnees initialise.")


if __name__ == "__main__":
    main()
