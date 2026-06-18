"""Document parsing for contract uploads.

Extracts text from PDF, DOCX, and plain text files.
"""

from contract_analyzer.document_parser.extractor import (
    ALLOWED_EXTENSIONS,
    ExtractionError,
    extract_text,
)

__all__ = ["ALLOWED_EXTENSIONS", "ExtractionError", "extract_text"]
