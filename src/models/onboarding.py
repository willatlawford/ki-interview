from sqlmodel import SQLModel


class FileInput(SQLModel):
    filename: str
    file_path: str
    content_type: str | None = None
