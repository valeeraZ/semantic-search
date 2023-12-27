from pgvector.sqlalchemy import Vector
from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from api.infra.db.model.base import Base


class File(Base):
    """File model."""

    __tablename__ = "file"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    content = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    chunks = relationship("FileChunk", uselist=True, back_populates="file")
    model_config = ConfigDict(from_attributes=True)


class FileChunk(Base):
    """FileChunk model."""

    __tablename__ = "file_chunk"

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("file.id", ondelete="CASCADE"))
    file = relationship("File", uselist=False, back_populates="chunks")
    chunk_text = Column(Text)
    embedding_vector = Column(Vector(1536))
    model_config = ConfigDict(from_attributes=True)
