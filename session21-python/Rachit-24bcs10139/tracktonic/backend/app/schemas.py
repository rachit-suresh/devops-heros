from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional

class AlbumCreate(BaseModel):
    @field_validator("title", "artist", mode="before")
    @classmethod
    def strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    title: str = Field(min_length=1, max_length=200)
    artist: str = Field(min_length=1, max_length=200)
    year: Optional[int] = Field(default=None, ge=1000, le=2100)

class AlbumUpdate(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    status: Optional[str] = Field(default=None, pattern="^(queued|listening|listened)$")

class AlbumOut(BaseModel):
    id: int
    title: str
    artist: str
    year: Optional[int]
    rating: Optional[int]
    status: str
    model_config = ConfigDict(from_attributes=True)
