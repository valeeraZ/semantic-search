from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from api.infra.db.meta import meta
from api.infra.db.model import load_all_models
from api.settings import settings


def _setup_db(app: FastAPI) -> None:  # pragma: no cover
    """
    Creates connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    :param app: fastAPI application.
    """
    engine = create_engine(str(settings.db_url))
    session_factory = sessionmaker(
        engine,
        expire_on_commit=False,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory
    with session_factory() as session:
        session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        session.commit()


def _create_tables() -> None:  # pragma: no cover
    """Populates tables in the database."""
    load_all_models()
    engine = create_engine(str(settings.db_url))
    with engine.begin() as connection:
        meta.create_all(connection, checkfirst=True)
        # create index on vector column
        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_vector ON file_chunk USING hnsw (embedding_vector vector_l2_ops);
                """,
            ),
        )
    engine.dispose()


def _startup(app: FastAPI) -> None:  # noqa: WPS430
    _setup_db(app)
    _create_tables()


def _shutdown(app: FastAPI) -> None:  # noqa: WPS430
    app.state.db_engine.dispose()


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:  # pragma: no cover
    """
    Context manager to run startup and shutdown events.

    :param app: fastAPI application.
    """
    _startup(app)
    try:
        yield
    finally:
        _shutdown(app)
