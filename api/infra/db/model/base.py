from sqlalchemy.orm import DeclarativeBase

from api.infra.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
