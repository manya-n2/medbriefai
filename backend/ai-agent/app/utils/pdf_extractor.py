
"""
pdf_extractor.py
Extracts clean text from uploaded PDF files using PyMuPDF.
Handles scanned PDFs gracefully by returning what text is available.
"""

import io
from app.utils.logger import get_logger

logger = get_logger("pdf_extractor")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF given its raw bytes.
    Returns cleaned text string.
    Raises ValueError if PDF is unreadable or contains no text.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("pymupdf is not installed. Run: pip install pymupdf")

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        logger.info(f"PDF opened: {doc.page_count} pages")

        all_text = []
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text = page.get_text("text")
            if text.strip():
                all_text.append(f"[Page {page_num + 1}]\n{text.strip()}")

        doc.close()

        if not all_text:
            raise ValueError(
                "No readable text found in PDF. "
                "This may be a scanned image-only PDF. "
                "Please paste the note as text instead."
            )

        full_text = "\n\n".join(all_text)
        logger.info(f"Extracted {len(full_text)} characters from PDF")

        # Clean up excessive whitespace while preserving structure
        lines = [line.strip() for line in full_text.splitlines()]
        cleaned = "\n".join(line for line in lines if line)

        return cleaned

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}", exc_info=True)
        raise ValueError(f"Could not read PDF: {str(e)}")


def validate_pdf_size(file_bytes: bytes, max_mb: float = 10.0) -> None:
    """Raise ValueError if file exceeds max size."""
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > max_mb:
        raise ValueError(f"PDF too large ({size_mb:.1f}MB). Maximum allowed: {max_mb}MB.")
