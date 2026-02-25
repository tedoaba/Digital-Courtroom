import pytest
import concurrent.futures
from src.tools.doc_tools import extract_file_paths, find_architectural_claims, extract_pdf_markdown

def test_extract_file_paths():
    md = "Here we test `src/main.py` and also testing/dir/file.txt without ticks. Skip http://google.com."
    paths = extract_file_paths(md)
    assert "src/main.py" in paths
    assert "testing/dir/file.txt" in paths
    assert "http://google.com" not in paths

def test_find_architectural_claims():
    md = "This text doesn't have it.\\n\\nThis one uses a StateGraph to build out nodes.\\n\\nAnd some Multimodal behavior."
    # Since find_architectural_claims splits by '\n\n', we need proper newlines
    md = md.replace('\\n', '\n')
    findings = find_architectural_claims(md)
    assert len(findings) == 2
    keys = {f["keyword"].lower() for f in findings}
    assert "stategraph" in keys
    assert "multimodal" in keys

def test_extract_pdf_markdown_timeout(mocker):
    # Mock _convert_pdf to sleep longer than timeout
    def mock_convert(*args, **kwargs):
        import time
        time.sleep(2)
        return "Not reached"
        
    mocker.patch("src.tools.doc_tools._convert_pdf", side_effect=mock_convert)
    with pytest.raises(TimeoutError, match="timed out"):
        extract_pdf_markdown("fake.pdf", timeout=1)

def test_extract_pdf_markdown_success(mocker):
    mocker.patch("src.tools.doc_tools._convert_pdf", return_value="Extracted markdown")
    res = extract_pdf_markdown("fake.pdf")
    assert res == "Extracted markdown"
