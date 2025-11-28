from pydantic import BaseModel


class FileInput(BaseModel):
    filename: str
    file_path: str
    content_type: str | None = None
