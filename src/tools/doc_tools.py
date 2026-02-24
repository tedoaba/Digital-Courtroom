import time
from pathlib import Path
from typing import Union

# Importing docling components safely
try:
    from docling.document_converter import DocumentConverter
except ImportError:
    # Handle if docling is not successfully installed during some test steps
    DocumentConverter = None

from src.tools.base import ToolResult
from src.tools.utils import with_timeout, check_disk_limit

@with_timeout(seconds=60)
def ingest_pdf(pdf_path: Union[str, Path]) -> ToolResult[str]:
    """
    Ingest a PDF report and extract raw text safely without executing embedded scripts.
    Ref: FR-005 (graceful failure), FR-009 (disk limit), FR-010 (password protected).
    """
    start_time = time.time()
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        return ToolResult(status="failure", error="PDF path does not exist.")

    if not check_disk_limit(pdf_path.parent):
        return ToolResult(status="disk_limit_exceeded", error="Disk limit exceeded before reading PDF.")

    if DocumentConverter is None:
         return ToolResult(status="failure", error="docling library is not installed.")

    try:
        converter = DocumentConverter()
        doc_result = converter.convert(pdf_path)
        markdown_text = doc_result.document.export_to_markdown()

        return ToolResult(
            status="success",
            data=[markdown_text],
            execution_time=time.time() - start_time
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "password" in error_msg or "encrypt" in error_msg:
            return ToolResult(
                status="access_denied",
                error=f"Password or encryption detected: {e}",
                execution_time=time.time() - start_time
            )
        return ToolResult(
            status="failure",
            error=f"Failed to parse PDF: {e}",
            execution_time=time.time() - start_time
        )
