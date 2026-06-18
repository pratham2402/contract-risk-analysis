"""Format-specific text extractors for contract documents."""

import io
from pathlib import Path

ALLOWED_EXTENSIONS: set[str] = {".pdf", ".docx", ".txt"}


class ExtractionError(Exception):
    """Raised when text extraction from an uploaded file fails."""


def _validate_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ExtractionError(
            f"Unsupported file type '{suffix}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    return suffix


def _extract_pdf(file_bytes: bytes) -> str:
    import pdfplumber

    try:
        with io.BytesIO(file_bytes) as f:
            with pdfplumber.open(f) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
    except Exception as e:
        raise ExtractionError(
            f"Failed to read PDF: {e}. The file may be corrupted or image-based."
        )

    text = "\n\n".join(pages).strip()
    if not text:
        raise ExtractionError(
            "No extractable text found in PDF. The file may be scanned or image-based."
        )
    return text


def _extract_docx(file_bytes: bytes) -> str:
    from docx import Document

    try:
        with io.BytesIO(file_bytes) as f:
            doc = Document(f)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    except Exception as e:
        raise ExtractionError(
            f"Failed to read DOCX: {e}. The file may be corrupted or not a valid .docx."
        )

    text = "\n\n".join(paragraphs).strip()
    if not text:
        raise ExtractionError("No text found in DOCX document.")
    return text


def _extract_txt(file_bytes: bytes) -> str:
    text = file_bytes.decode("utf-8").strip()
    if not text:
        raise ExtractionError("File is empty.")
    return text


_EXTRACTORS = {
    ".pdf": _extract_pdf,
    ".docx": _extract_docx,
    ".txt": _extract_txt,
}


def extract_text(file_bytes: bytes, filename: str, max_size_mb: int = 10) -> str:
    """Extract plain text from an uploaded contract file.

    Args:
        file_bytes: Raw file content.
        filename: Original filename (used to detect format).
        max_size_mb: Maximum file size in megabytes.

    Returns:
        Extracted text as a string.

    Raises:
        ExtractionError: If the format is unsupported, the file is too large,
                         or no text could be extracted.
    """
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ExtractionError(
            f"File size ({size_mb:.1f}MB) exceeds limit ({max_size_mb}MB)."
        )

    suffix = _validate_extension(filename)
    return _EXTRACTORS[suffix](file_bytes)
