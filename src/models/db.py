from datetime import datetime
from typing import Optional

from sqlmodel import JSON, Field, Relationship, SQLModel


class File(SQLModel, table=True):
    __tablename__ = "files"

    id: int | None = Field(default=None, primary_key=True)
    filename: str = Field(index=True)
    thread_id: str = Field(index=True)
    file_type: str
    description: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationship to pages
    pages: list["Page"] = Relationship(back_populates="file")


class Page(SQLModel, table=True):
    __tablename__ = "pages"

    id: int | None = Field(default=None, primary_key=True)
    file_id: int = Field(foreign_key="files.id", index=True)
    page_number: int
    ocr_text: str | None = None
    visual_inspection: str | None = None
    grid_content: list[list[str]] | None = Field(default=None, sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    file: File | None = Relationship(back_populates="pages")
    page_image: Optional["PageImage"] = Relationship(back_populates="page")


class PageImage(SQLModel, table=True):
    __tablename__ = "page_images"

    id: int | None = Field(default=None, primary_key=True)
    page_id: int = Field(foreign_key="pages.id", index=True, unique=True)
    image_data: str  # base64 encoded image
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationship
    page: Page | None = Relationship(back_populates="page_image")
