import datetime

from pydantic import BaseModel, Field, field_validator


class FileOut(BaseModel):
    id: int
    name: str
    size: int
    # convert the content field to resume_content, only keeps the first 200 characters
    resume_content: str = Field(
        ...,
        alias="content",
        serialization_alias="resume_content",
    )
    created_at: datetime.datetime
    updated_at: datetime.datetime

    @field_validator("resume_content")
    @classmethod
    def content_to_resume_content(cls, v):
        return v[:200] if v else ""

    class Config:
        # This tells Pydantic to use the `alias` specified in the Field declaration
        populate_by_name = True
