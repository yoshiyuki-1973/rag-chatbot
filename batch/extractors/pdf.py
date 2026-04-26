from pathlib import Path

import fitz


def extract_pdf(path: Path) -> str:
    parts: list[str] = []
    with fitz.open(path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()
            if text:
                parts.append(f"[page:{page_number}]\n{text}")
    return "\n\n".join(parts)

