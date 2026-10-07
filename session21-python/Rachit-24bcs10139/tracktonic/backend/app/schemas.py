from pydantic import BaseModel, Field
from typing import Optional

class AlbumCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    artist: str = Field(min_length=1, max_length=200)
    year: Optional[int] = None

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
    class Config:
        from_attributes = True
