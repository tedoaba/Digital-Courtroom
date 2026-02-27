import base64
import concurrent.futures
import os
from typing import Any

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

from src.config import detective_settings, judicial_settings


def extract_images_from_pdf(pdf_path: str) -> list[dict[str, Any]]:
    """
    Extracts images from a PDF using PyMuPDF.
    """
    if not fitz:
        return []

    if not os.path.exists(pdf_path):
        return []

    images = []
    try:
        doc = fitz.open(pdf_path)
        for page_index in range(len(doc)):
            page = doc[page_index]
            image_list = page.get_images(full=True)

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                # Convert to base64
                encoded = base64.b64encode(image_bytes).decode("utf-8")

                images.append(
                    {
                        "base64": encoded,
                        "page": page_index + 1,
                        "index": img_index,
                    }
                )
        doc.close()
    except Exception:
        # Log error or raise
        pass

    return images


def classify_diagram(image_base64: str) -> str:
    """
    Sends an image to Gemini Pro Vision for classification.
    """
    if detective_settings.vision_provider == "ollama":
        llm = ChatOllama(
            model=detective_settings.vision_model,
            temperature=detective_settings.llm_temperature,
        )
    else:
        api_key = judicial_settings.google_api_key or judicial_settings.gemini_api_key
        if not api_key:
            return "Image analysis skipped: Missing Google API Key."

        llm = ChatGoogleGenerativeAI(
            model=detective_settings.vision_model,
            temperature=detective_settings.llm_temperature,
            google_api_key=api_key,
        )

    # Construct multimodal message
    from langchain_core.messages import HumanMessage

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "Analyze this architectural diagram from a software engineering perspective. Identify if it shows a LangGraph StateMachine with parallel branches (fan-out/fan-in) for Detectives and Judges. Describe the flow accurately.",
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
            },
        ],
    )

    try:
        response = llm.invoke([message])
        return str(response.content)
    except Exception as e:
        return f"Image classification failed: {e!s}"


def _run_vision_classification(pdf_path: str) -> list[dict[str, Any]]:
    images = extract_images_from_pdf(pdf_path)
    results = []

    # Limit number of images to avoid token limits / 429
    for idx, img in enumerate(images[:5]):
        cls = classify_diagram(img["base64"])
        results.append(
            {
                "image_index": idx,
                "page": img["page"],
                "classification": cls,
            }
        )

    return results


def run_vision_classification(pdf_path: str, timeout: int = 60) -> list[dict[str, Any]]:
    """Runs vision classification with a timeout."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run_vision_classification, pdf_path)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            raise TimeoutError(
                f"Vision classification timed out after {timeout} seconds."
            )
        except Exception as e:
            raise RuntimeError(f"Vision classification failed: {e!s}")
