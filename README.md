## Project Overview

This repo allows onboarding of pdfs to a context store. 
This onboarding has already been run on the files provided in `files/` and db.sqlite created. This will be provided seperately as `db.sqlite.zip` - please extract this to root of the repo.

It is intended that the candidate builds an agent for answering questions using that store.
Use of Agentic Coding Assistants is encouraged for this task.
- Agents can be used to code any part - but bear in mind you will be expected talk through the code created.


## Instructions
1. Starting with main.py, explain the current functionality of the app.
2. Develop an agent that can answer questions using the context store.
   - A snippet has been included to demo db access.
3. (Begin to) develop a frontend for this agent.

### Database
- SQLite database file: `db.sqlite`
- Tables: files, pages, page_images
- Example queries via sqlalchemy shown in snippet.py

## Architecture

### Core Components

1. **Database Layer** (`src/database.py`)
   - Async SQLite with SQLModel
   - Auto-initialization of tables
   - Session management utilities

2. **Models** (`src/models/`)
   - `db.py` - SQLModel entities: File, Page, PageImage

3. **Onboarding System** (`src/onboarding/`)
   - `router.py` - Main entry point with file type detection
   - `pdf_processor.py` - PDF text extraction and visual analysis

### Configuration

Environment variables (`.env` file):
- `ANTHROPIC_API_KEY` - Required Azure OpenAI API key
- `DATABASE_URL` - Default: sqlite+aiosqlite:///db.sqlite
- `MAX_CONCURRENCY` - Default: 20 (concurrent visual analysis tasks)

### Dependencies

Key libraries:
- `sqlmodel` + `aiosqlite` - Database ORM and async SQLite
- `langchain` + `langchain-openai` - AI integration
- `pdftotext` + `pdf2image` - PDF processing
- `pydantic` + `pydantic-settings` - Data validation and settings
