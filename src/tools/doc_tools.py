import concurrent.futures
import re

try:
    from docling.document_converter import DocumentConverter
except ImportError:
    DocumentConverter = None


def _convert_pdf(pdf_path: str) -> str:
    """Internal function to convert PDF; runs in isolated thread/process if possible."""
    if not DocumentConverter:
        return ""
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    return result.document.export_to_markdown()


def extract_pdf_markdown(pdf_path: str, timeout: int = 60) -> str:
    """Extracts text content from a PDF using Docling, wrapped in a timeout."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_convert_pdf, pdf_path)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            raise TimeoutError(f"PDF extraction timed out after {timeout} seconds.") from None
        except Exception as e:
            raise RuntimeError(f"PDF extraction failed: {e!s}") from e


def find_architectural_claims(
    markdown_text: str,
    keywords: list[str] = None,
) -> list[dict[str, str]]:
    """Simple finding for claims around specific keywords."""
    if not keywords:
        keywords = [
            "StateGraph",
            "Parallel",
            "BaseModel",
            "LangGraph",
            "Gemini",
            "multimodal",
            "architecture",
        ]

    findings = []
    chunks = markdown_text.split("\n\n")
    for idx, chunk in enumerate(chunks):
        if not chunk.strip():
            continue

        found_kws = [kw for kw in keywords if kw.lower() in chunk.lower()]
        for kw in found_kws:
            findings.append(
                {
                    "keyword": kw,
                    "chunk": chunk.strip()[:250],
                    "location": f"chunk_{idx}",
                },
            )

    return findings


def extract_file_paths(markdown_text: str) -> list[str]:
    """Finds referenced file paths in the document (e.g., src/main.py, tests/)."""
    # Look for patterns that look like paths (with / and an extension or just typical dir structures)
    # Simple regex for common code path mentions.
    pattern = r"`?((?:[a-zA-Z0-9_\-\.]+)?/[a-zA-Z0-9_\-\./]+(?:\.[a-zA-Z0-9]+)?)`?"
    paths = set()
    for match in re.finditer(pattern, markdown_text):
        path = match.group(1)
        if len(path) > 3 and "://" not in path:
            paths.add(path)
    return list(paths)
