from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import Row

from api.infra.db.model.file import FileChunk


class SearchFileResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    file_id: int
    file_name: str = None
    similarity: float = None
    file_chunk_id: int = Field(..., alias="id", serialization_alias="file_chunk_id")
    file_chunk_text: str = Field(
        ...,
        alias="chunk_text",
        serialization_alias="file_chunk_text",
    )

    @model_validator(mode="before")
    @classmethod
    def get_search_result_from_row(cls, data: Row) -> Any:
        data_file_chunk = data[0]
        min_distance = data[1]
        data_dict = data_file_chunk.__dict__
        if isinstance(data_file_chunk, FileChunk):
            data_dict["file_name"] = data_file_chunk.file.name
        data_dict["similarity"] = 1 - min_distance
        return data_dict
