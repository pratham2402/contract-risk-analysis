"""Tests for document text extraction."""

import pytest

from contract_analyzer.document_parser.extractor import (
    ALLOWED_EXTENSIONS,
    ExtractionError,
    _validate_extension,
    extract_text,
)


class TestValidateExtension:
    def test_valid_extensions(self):
        for ext in [".pdf", ".docx", ".txt"]:
            assert _validate_extension(f"contract{ext}") == ext
            assert _validate_extension(f"CONTRACT{ext.upper()}") == ext

    def test_invalid_extension(self):
        with pytest.raises(ExtractionError) as exc:
            _validate_extension("contract.exe")
        assert "Unsupported file type" in str(exc.value)
        assert ".exe" in str(exc.value)

    def test_no_extension(self):
        with pytest.raises(ExtractionError) as exc:
            _validate_extension("contract")
        assert "Unsupported file type" in str(exc.value)


class TestTxtExtraction:
    def test_simple_txt(self):
        text = extract_text(b"Hello World Contract", "contract.txt")
        assert text == "Hello World Contract"

    def test_txt_with_unicode(self):
        text = extract_text(
            "Confidentialité — données personnelles © 2026".encode("utf-8"),
            "contract.txt",
        )
        assert "Confidentialité" in text
        assert "©" in text

    def test_empty_txt_raises(self):
        with pytest.raises(ExtractionError) as exc:
            extract_text(b"   \n  ", "empty.txt")
        assert "empty" in str(exc.value).lower()

    def test_txt_with_newlines(self):
        text = extract_text(
            b"Line 1\nLine 2\n\nLine 3\n",
            "contract.txt",
        )
        assert text == "Line 1\nLine 2\n\nLine 3"

    def test_size_limit_exceeded(self):
        # Create content larger than 10MB
        big = b"x" * (11 * 1024 * 1024)
        with pytest.raises(ExtractionError) as exc:
            extract_text(big, "big.txt")
        assert "exceeds limit" in str(exc.value).lower()

    def test_custom_size_limit(self):
        # 500KB with 1MB limit should pass
        content = b"x" * (500 * 1024)
        text = extract_text(content, "doc.txt", max_size_mb=1)
        assert len(text) > 0

    def test_size_at_limit(self):
        content = b"Hello" * 2000  # ~10KB
        text = extract_text(content, "doc.txt", max_size_mb=1)
        assert len(text) > 0


class TestDocxExtraction:
    def test_docx_validation(self):
        """DOCX files need python-docx to actually parse — test validation path."""
        # Just verify extension validation works for .docx
        assert _validate_extension("contract.docx") == ".docx"

    def test_docx_invalid_content(self):
        """A .docx that isn't really a docx should raise ExtractionError."""
        with pytest.raises(ExtractionError):
            extract_text(b"not a real docx file", "fake.docx")


class TestPdfExtraction:
    def test_pdf_validation(self):
        assert _validate_extension("contract.pdf") == ".pdf"

    def test_pdf_invalid_content(self):
        """A .pdf that isn't really a PDF should raise ExtractionError."""
        with pytest.raises(ExtractionError):
            extract_text(b"not a real pdf file", "fake.pdf")


class TestAllowedExtensions:
    def test_set_contains_expected(self):
        assert ALLOWED_EXTENSIONS == {".pdf", ".docx", ".txt"}
