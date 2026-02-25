import pytest
import concurrent.futures
from src.tools.vision_tools import run_vision_classification

def test_run_vision_classification_timeout(mocker):
    def mock_run(*args, **kwargs):
        import time
        time.sleep(2)
        return []
        
    mocker.patch("src.tools.vision_tools.extract_images_from_pdf", side_effect=mock_run)
    with pytest.raises(TimeoutError, match="timed out"):
        run_vision_classification("fake.pdf", timeout=1)

def test_run_vision_classification_success(mocker):
    mocker.patch("src.tools.vision_tools.extract_images_from_pdf", return_value=[{"base64": "fake", "page": 1}])
    mocker.patch("src.tools.vision_tools.classify_diagram", return_value="Parallel Flow. It runs in parallel.")
    
    res = run_vision_classification("fake.pdf")
    assert len(res) == 1
    assert res[0]["classification"] == "Parallel Flow. It runs in parallel."
    assert res[0]["image_index"] == 0
