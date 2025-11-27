import os
from pathlib import Path

from src.models.db import File
from src.models.onboarding import FileInput
from src.onboarding.pdf_processor import onboard_pdf


def get_file_type(filename: str) -> str:
    """Determine file type based on file extension."""
    extension = Path(filename).suffix.lower()

    file_type_map = {
        ".pdf": "pdf",
    }

    return file_type_map.get(extension, "unknown")


async def onboard_file(file_input: FileInput, thread_id: str) -> File | None:
    """
    Main onboarding function that processes files based on their type.

    Args:
        file_input: FileInput pydantic model containing file info
        thread_id: Thread identifier for chat interface

    Returns:
        File: The created File record or None if processing failed
    """
    if not os.path.exists(file_input.file_path):
        raise FileNotFoundError(f"File not found: {file_input.file_path}")

    file_type = get_file_type(file_input.filename)

    if file_type == "pdf":
        return await onboard_pdf(file_input, thread_id)
    else:
        raise NotImplementedError(f"File type '{file_type}' is not yet supported")
