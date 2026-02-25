import time
from pathlib import Path
from typing import Union

try:
    from docling.document_converter import DocumentConverter
except ImportError:
    DocumentConverter = None

from src.tools.base import ToolResult
from src.tools.utils import with_timeout, check_disk_limit

@with_timeout(seconds=60)
def extract_visuals(pdf_path: Union[str, Path], workspace: Union[str, Path]) -> ToolResult[str]:
    """
    Extract embedded images from a PDF and save them safely to the isolated workspace.
    Ref: FR-007 (visuals isolation), FR-009 (disk limit check per image).
    """
    start_time = time.time()
    pdf_path = Path(pdf_path)
    workspace = Path(workspace)

    if not check_disk_limit(workspace):
        return ToolResult(status="disk_limit_exceeded", error="Disk limit exceeded before visual extraction.")

    if DocumentConverter is None:
        return ToolResult(status="failure", error="docling library is not installed.")

    image_paths = []
    
    try:
        converter = DocumentConverter()
        doc_result = converter.convert(pdf_path)
        
        img_id = 0
        for page_no, page in doc_result.document.pages.items():
            if not hasattr(page, 'get_images'):
                continue
                
            for img in page.get_images():
                 filename = f"image_{page_no}_{img_id}.png"
                 out_path = workspace / filename
                 
                 # Save image
                 if hasattr(img.image, 'save'):
                     img.image.save(out_path)
                 else:
                     # Some docling versions API differs slightly
                     continue
                     
                 # Check disk limit after saving each image
                 if not check_disk_limit(workspace):
                     out_path.unlink() # Delete potentially partial/over-limit image
                     return ToolResult(
                         status="disk_limit_exceeded",
                         error="Disk limit reached during image extraction."
                     )
                     
                 image_paths.append(str(out_path))
                 img_id += 1

        return ToolResult(
             status="success",
             data=image_paths,
             execution_time=time.time() - start_time
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "password" in error_msg or "encrypt" in error_msg:
             return ToolResult(
                  status="access_denied",
                  error=f"Cannot extract from encrypted PDF: {e}",
                  execution_time=time.time() - start_time
             )
        return ToolResult(
            status="failure",
            error=f"Error extracting images: {e}",
            execution_time=time.time() - start_time
        )
