import asyncio
import base64
import logging
from io import BytesIO

import pdftotext
from langchain.schema import HumanMessage
from pdf2image import convert_from_path

from src.database import get_async_db_session
from src.llms import get_text_model, get_vision_model
from src.models.db import File, Page, PageImage
from src.models.onboarding import FileInput
from src.onboarding.prompts import DOCUMENT_SUMMARY_PROMPT, VISUALLY_ANALYSE_PAGE_PROMPT
from src.settings import settings


async def onboard_pdf(file_input: FileInput, thread_id: str) -> File:
    """
    Process a PDF file through the complete onboarding pipeline.

    Args:
        file_input: FileInput containing file information
        thread_id: Thread identifier for chat interface

    Returns:
        File: The created and processed File record
    """
    logger = logging.getLogger(__name__)

    async with get_async_db_session() as session:
        try:
            # 1. Create file record
            file_record = File(filename=file_input.filename, thread_id=thread_id, file_type="pdf")
            session.add(file_record)
            await session.flush()  # Get ID without full commit

            # 2. Extract text from each page (batch)
            logger.info(f"Extracting text from PDF: {file_input.filename}")
            pages_text = await extract_pdf_text(file_input.file_path)

            # 3. Convert pages to images (batch)
            logger.info(f"Converting PDF pages to images: {file_input.filename}")
            pages_images = await pdf_pages_to_images(file_input.file_path)

            # 4. Create page records and images in batch
            page_records: list[Page] = []
            for page_num, page_text in enumerate(pages_text, 1):
                logger.info(f"Creating page record {page_num} of {len(pages_text)}")

                # Create page record with OCR text
                page_record = Page(file_id=file_record.id, page_number=page_num, ocr_text=page_text)
                session.add(page_record)
                page_records.append(page_record)

            # Flush to get page IDs
            await session.flush()

            # Create page image records
            for page_record, page_image_b64 in zip(page_records, pages_images):
                page_image_record = PageImage(page_id=page_record.id, image_data=page_image_b64)
                session.add(page_image_record)

            # Flush to force the images to write to DB
            await session.flush()

            # 5. Process visual analysis in parallel with concurrency limit
            logger.info("Analyzing visual elements for all pages in parallel")

            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(settings.max_concurrency)

            async def analyze_with_semaphore(page_num: int, page_image_b64: str) -> tuple[int, str]:
                async with semaphore:
                    return (page_num, await analyze_page_visually(page_image_b64))

            # Run visual analysis in parallel
            analysis_tasks = [
                analyze_with_semaphore(page_num, page_image_b64)
                for page_num, page_image_b64 in enumerate(pages_images, 1)
            ]

            analysis_results = await asyncio.gather(*analysis_tasks)

            visual_page_description_by_page = {
                page_num: description for page_num, description in analysis_results
            }

            # 6. Update page records with visual analysis and collect content
            all_content = []
            for page_record in page_records:
                # Update page with visual analysis
                visual_content = visual_page_description_by_page.get(page_record.page_number, "")
                page_record.visual_inspection = visual_content
                session.add(page_record)

                # Combine content for document summary
                page_content = f"<Page {page_record.page_number}>:\n{visual_content}\n\n"
                all_content.append(page_content)

            await session.flush()

            # 7. Generate document summary
            logger.info("Generating document summary")
            combined_content = "\n".join(all_content[0:39])
            document_summary = await generate_document_summary(combined_content)

            # Update file record with summary
            file_record.description = document_summary
            session.add(file_record)

            # Single commit for all data at the end
            await session.commit()

            # Refresh to keep the object bound to session
            await session.refresh(file_record)

            logger.info(f"Successfully onboarded PDF: {file_input.filename}")
            return file_record

        except Exception as e:
            await session.rollback()
            logger.error(f"Error processing PDF {file_input.filename}: {str(e)}")
            raise


async def extract_pdf_text(pdf_path: str) -> list[str]:
    """Extract text from all pages of a PDF using pdftotext."""

    def _extract_pdf_text_sync(pdf_path: str) -> list[str]:
        """Extract text from all pages of a PDF using pdftotext (sync)."""
        with open(pdf_path, "rb") as file:
            pdf = pdftotext.PDF(file)
            return list(pdf)  # Convert to list of page texts

    return await asyncio.to_thread(_extract_pdf_text_sync, pdf_path)


async def pdf_pages_to_images(pdf_path: str) -> list[str]:
    """Convert PDF pages to base64 encoded images using pdf2image."""

    def _pdf_pages_to_images_sync(pdf_path: str) -> list[str]:
        """Convert PDF pages to base64 encoded images using pdf2image (sync)."""
        images = convert_from_path(pdf_path, dpi=150)
        base64_images = []

        for image in images:
            buffer = BytesIO()
            image.save(buffer, format="JPEG", quality=85, optimize=True)
            img_bytes = buffer.getvalue()
            base64_encoded = base64.b64encode(img_bytes).decode("utf-8")
            base64_images.append(base64_encoded)

        return base64_images

    return await asyncio.to_thread(_pdf_pages_to_images_sync, pdf_path)


async def analyze_page_visually(image_base64: str) -> str:
    """Use OpenAI to analyze visual elements in a page image."""
    llm = get_vision_model()

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": VISUALLY_ANALYSE_PAGE_PROMPT,
            },
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
        ]
    )

    try:
        response = await llm.ainvoke([message])
    except Exception as e:
        return "Error during visual analysis: " + str(e)
    return response.content


async def generate_document_summary(combined_content: str) -> str:
    """Generate a 10 bullet point summary of the document."""
    llm = get_text_model()

    message = HumanMessage(
        content=DOCUMENT_SUMMARY_PROMPT.format(document_content=combined_content)
    )

    response = await llm.ainvoke([message])
    return response.content
