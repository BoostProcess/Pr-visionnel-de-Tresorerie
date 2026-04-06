"""Configuration de la base de données SQLAlchemy."""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import DATABASE_URL


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_session():
    """Context manager pour obtenir une session DB."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """Crée toutes les tables en base."""
    # Import des modèles pour que SQLAlchemy les connaisse
    import app.models.adjustments  # noqa: F401
    import app.models.assumptions  # noqa: F401
    import app.models.cash  # noqa: F401
    import app.models.fixed_charges  # noqa: F401
    import app.models.history  # noqa: F401
    import app.models.imports_log  # noqa: F401
    import app.models.invoices  # noqa: F401
    import app.models.orders  # noqa: F401
    import app.models.reference  # noqa: F401
    import app.models.versions  # noqa: F401

    Base.metadata.create_all(engine)
