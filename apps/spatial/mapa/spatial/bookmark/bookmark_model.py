from uuid import UUID

from pydantic import BaseModel

# thumbnail = bookmark olarak oluşturulan bir datanın ön izleme / küçük resim değeri
# location = koordinat bilgisidir. x;y;srid;zoomLevel formatında gelmektedir.


class Bookmark(BaseModel):
    """Bookmark Modeli"""
    id: UUID
    name: str
    location: str
    thumbnail: str | None = None
    map_id: UUID
    user_id: UUID | None = None


class CreateBookmark(BaseModel):
    name: str
    location: str
    thumbnail: str | None = None
    map_id: UUID
    user_id: UUID | None = None


class UpdateBookmark(BaseModel):
    name: str
    location: str
    thumbnail: str | None = None
    map_id: UUID
    user_id: UUID | None = None


class UpdateAllBookmark(BaseModel):
    thumbnail: str | None = None
