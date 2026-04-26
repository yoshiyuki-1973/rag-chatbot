import re

try:
    import tiktoken
except ImportError:  # pragma: no cover
    tiktoken = None

_ENCODING = tiktoken.get_encoding("cl100k_base") if tiktoken is not None else None


def count_tokens(text: str) -> int:
    if not text:
        return 0
    if _ENCODING is None:
        return max(1, len(text) // 2)
    return len(_ENCODING.encode(text))


def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    current: list[str] = []

    for paragraph in paragraphs:
        candidate = "\n\n".join([*current, paragraph]) if current else paragraph
        if count_tokens(candidate) <= chunk_size:
            current.append(paragraph)
            continue
        if current:
            chunks.append("\n\n".join(current))
        if count_tokens(paragraph) > chunk_size:
            chunks.extend(_split_long_text(paragraph, chunk_size, overlap))
            current = []
        else:
            current = [paragraph]

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def _split_long_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    sentences = re.split(r"(?<=[。.!?])\s*", text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = current + sentence
        if count_tokens(candidate) <= chunk_size:
            current = candidate
            continue
        if current:
            chunks.append(current.strip())
            current = _tail(current, overlap) + sentence
        else:
            chunks.append(sentence.strip())
            current = ""
    if current.strip():
        chunks.append(current.strip())
    return chunks


def _tail(text: str, overlap: int) -> str:
    if count_tokens(text) <= overlap:
        return text + " "
    lo, hi = 0, len(text)
    while lo < hi - 1:
        mid = (lo + hi) // 2
        if count_tokens(text[mid:]) <= overlap:
            hi = mid
        else:
            lo = mid
    tail = text[hi:]
    return (tail + " ") if tail else ""
