import asyncio
import logging
import os

from src.database import init_db
from src.models.onboarding import FileInput
from src.onboarding import onboard_file


async def onboard(thread_id: str = "example-thread-id"):
    logger = logging.getLogger(__name__)

    # Set up basic logging
    logging.basicConfig(level=logging.INFO)

    logger.info("Starting chi2 PDF onboarding...")

    # Initialize database
    await init_db()

    for filename in [
        # "beazley_annual_report_2024.pdf",
        "brit_annual_report_2024.pdf",
        "travelers_annual_report_2024.pdf",
    ]:
        file_path = "files/" + filename
        if not os.path.exists(file_path):
            logger.error(f"PDF not found: {file_path}")
            return

        try:
            # Create file input
            file_input = FileInput(
                filename=filename, file_path=file_path, content_type="application/pdf"
            )

            # Onboard the file
            logger.info("Starting PDF onboarding process...")
            file_record = await onboard_file(file_input, thread_id)

            logger.info(f"✅ Successfully onboarded PDF with ID: {file_record.id}")
            logger.info(f"Description: {file_record.description}")

        except Exception as e:
            logger.error(f"❌ Error during onboarding: {e}")
            raise


if __name__ == "__main__":
    thread_id = "test-thread"

    asyncio.run(onboard(thread_id))
