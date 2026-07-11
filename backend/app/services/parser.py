"""Module A — PDF ingestion and clause-level parsing."""
import re
import logging
import pdfplumber
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

# Common SEBI circular heading/section patterns
CHAPTER_PATTERN = re.compile(
    r"^(?:Chapter|CHAPTER)\s+([IVXLCDM]+|\d+)\s*[-–:.]?\s*(.*)", re.IGNORECASE
)
ITEM_PATTERN = re.compile(
    r"^(?:Item\s+(?:No\.?\s*)?|ITEM\s+(?:NO\.?\s*)?)(\d+)\s*[-–:.]?\s*(.*)", re.IGNORECASE
)
SECTION_PATTERN = re.compile(
    r"^(\d+(?:\.\d+)*)\s*[.)\s]\s*(.*)"
)
CLAUSE_PATTERN = re.compile(
    r"^\(([a-z]|[ivx]+|\d+)\)\s*(.*)", re.IGNORECASE
)


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """Extract text from each page of a PDF, preserving page numbers."""
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append({"page_number": i, "text": text})
    logger.info(f"Extracted {len(pages)} pages from {pdf_path}")
    return pages


def parse_into_chunks(
    pages: list[dict],
    source_document: str,
    effective_date: date | None = None,
    circular_id: int | None = None,
) -> list[dict]:
    """
    Parse page-level text into clause-level chunks with structural metadata.
    Returns a list of chunk dicts ready for DB insertion.
    """
    chunks = []
    current_chapter = "General"
    current_section = "0"
    chunk_counter = 0
    current_text_lines = []
    current_page = 1

    def _flush_chunk():
        nonlocal chunk_counter, current_text_lines
        if not current_text_lines:
            return
        text = "\n".join(current_text_lines).strip()
        if len(text) < 20:  # Skip very short fragments
            current_text_lines = []
            return
        chunk_counter += 1
        prefix = re.sub(r"[^A-Za-z0-9]", "", source_document[:20]).upper()
        chunk_id = f"{prefix}-CH{current_chapter[:10].replace(' ', '')}-S{current_section}-{chunk_counter:04d}"
        chunks.append({
            "circular_id": circular_id,
            "chunk_id": chunk_id,
            "chapter": current_chapter,
            "section_id": current_section,
            "page_number": current_page,
            "text": text,
            "effective_date": effective_date,
        })
        current_text_lines = []

    for page_data in pages:
        page_num = page_data["page_number"]
        lines = page_data["text"].split("\n")

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Detect chapter headings
            chapter_match = CHAPTER_PATTERN.match(stripped)
            if chapter_match:
                _flush_chunk()
                ch_num = chapter_match.group(1)
                ch_title = chapter_match.group(2).strip()
                current_chapter = f"Chapter {ch_num}" + (f" - {ch_title}" if ch_title else "")
                current_section = "0"
                current_page = page_num
                continue

            # Detect Item headings (SEBI style)
            item_match = ITEM_PATTERN.match(stripped)
            if item_match:
                _flush_chunk()
                item_num = item_match.group(1)
                item_title = item_match.group(2).strip()
                current_chapter = f"Item {item_num}" + (f" - {item_title}" if item_title else "")
                current_section = item_num
                current_page = page_num
                continue

            # Detect section numbers like 3.1, 4.2.1
            section_match = SECTION_PATTERN.match(stripped)
            if section_match:
                new_section = section_match.group(1)
                # Only flush if it's a new top-level or significant subsection
                if new_section != current_section:
                    _flush_chunk()
                    current_section = new_section
                    current_page = page_num

            current_text_lines.append(stripped)

    _flush_chunk()  # Flush remaining text

    logger.info(f"Parsed {len(chunks)} clause-level chunks from {source_document}")
    return chunks


def parse_circular_pdf(
    pdf_path: str,
    title: str,
    effective_date: date | None = None,
    circular_id: int | None = None,
) -> list[dict]:
    """
    End-to-end: PDF file → list of clause chunk dicts.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages = extract_text_from_pdf(pdf_path)
    chunks = parse_into_chunks(pages, title, effective_date, circular_id)
    return chunks
