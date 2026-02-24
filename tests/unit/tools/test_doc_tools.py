import pytest
from pathlib import Path
import tempfile
import os
from src.tools.doc_tools import ingest_pdf
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_workspace():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

def test_ingest_pdf_success(mock_workspace):
    """Test successful ingestion of a PDF document."""
    pdf_path = mock_workspace / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%Fake PDF content for test")
    
    # We mock DocumentConverter here as docling needs a real valid PDF for its parse method.
    with patch("src.tools.doc_tools.DocumentConverter") as mock_converter:
        mock_instance = mock_converter.return_value
        mock_doc = MagicMock()
        mock_doc.export_to_markdown.return_value = "Mock Markdown Content"
        mock_instance.convert.return_value.document = mock_doc
        
        result = ingest_pdf(pdf_path)
        
        assert result.status == "success"
        assert result.data is not None
        assert "Mock Markdown Content" in result.data[0]

def test_ingest_pdf_corrupt_pdf(mock_workspace):
    """Test behavior with a completely invalid/corrupt PDF."""
    pdf_path = mock_workspace / "corrupt.pdf"
    pdf_path.write_text("Not a pdf file")
    
    with patch("src.tools.doc_tools.DocumentConverter") as mock_converter:
        mock_instance = mock_converter.return_value
        mock_instance.convert.side_effect = Exception("Invalid PDF format")
        
        result = ingest_pdf(pdf_path)
        
        assert result.status == "failure"

def test_ingest_pdf_password_protected(mock_workspace):
    """Test password protected error state."""
    pdf_path = mock_workspace / "locked.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")
    
    with patch("src.tools.doc_tools.DocumentConverter") as mock_converter:
        mock_instance = mock_converter.return_value
        # Docling raises a specific error for encryption/password
        mock_instance.convert.side_effect = Exception("File is encrypted")
        
        result = ingest_pdf(pdf_path)
        
        assert result.status == "access_denied"
        assert "encrypted" in result.error or "password" in result.error.lower()
