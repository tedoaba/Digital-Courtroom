import pytest
from pathlib import Path
import tempfile
import os
from unittest.mock import patch, MagicMock
from src.tools.vision_tools import extract_visuals


@pytest.fixture
def mock_workspace():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

def test_extract_visuals_success(mock_workspace):
    """Test successful extraction of images from document."""
    pdf_path = mock_workspace / "images.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")
    
    with patch("src.tools.vision_tools.DocumentConverter") as mock_converter:
        mock_instance = mock_converter.return_value
        
        # Mock what docling doc.pages[...].get_images() does
        mock_image = MagicMock()
        mock_image.image.save = MagicMock()
        
        mock_doc = MagicMock()
        mock_doc.pages = {
             1: MagicMock(get_images=MagicMock(return_value=[mock_image]))
        }
        mock_instance.convert.return_value.document = mock_doc
        
        result = extract_visuals(pdf_path, workspace=mock_workspace)
        
        assert result.status == "success"
        assert result.data is not None
        assert len(result.data) == 1
        
        # Check if saved was called
        mock_image.image.save.assert_called_once()
        
        # Ensure it returns Path string
        assert str(mock_workspace) in result.data[0]

def test_extract_visuals_disk_limit(mock_workspace):
    """Test disk limit exceeded gracefully exits."""
    pdf_path = mock_workspace / "images.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")
    
    with patch("src.tools.vision_tools.check_disk_limit", return_value=False):
        result = extract_visuals(pdf_path, workspace=mock_workspace)
        assert result.status == "disk_limit_exceeded"
