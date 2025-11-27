from sqlmodel import select

from src.database import get_async_db_session
from src.models.db import File, Page


async def read_file(file_id: int):
    """Read the extracted contents of a file, including OCR text and visual descriptions."""

    async with get_async_db_session() as session:
        # First verify the file belongs to this thread
        file_stmt = select(File).where(File.id == file_id)
        file_result = await session.execute(file_stmt)
        file_record = file_result.scalar_one_or_none()

        if not file_record:
            return f"Error: File with id {file_id} not found or not accessible in this thread."

        # Get pages with their content, ordered by page number
        pages_stmt = select(Page).where(Page.file_id == file_id).order_by(Page.page_number)
        pages_result = await session.execute(pages_stmt)
        pages = pages_result.scalars().all()

        if not pages:
            return f"No pages found for file: {file_record.filename}"

        # Format the page content
        page_contents = []
        for page in pages:
            page_data = {"page_number": page.page_number, "content": {}}

            # Include OCR text if available
            if page.ocr_text:
                page_data["content"]["text"] = page.ocr_text

            # Include visual inspection if available
            if page.visual_inspection:
                page_data["content"]["visual_analysis"] = page.visual_inspection

            page_contents.append(page_data)

        return {
            "file": {
                "id": file_record.id,
                "filename": file_record.filename,
                "file_type": file_record.file_type,
                "description": file_record.description,
            },
            "pages": page_contents,
        }
