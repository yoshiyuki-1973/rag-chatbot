import os
from pathlib import Path

import yaml

from chunker import count_tokens, split_text
from db import IngestRepository, SourceConfig, run_async
from embedder import EmbeddingBatchClient
from extractors.markdown import extract_markdown
from extractors.pdf import extract_pdf


def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required")

    sources = load_sources(Path("sources.yaml"))
    embedder = EmbeddingBatchClient(openai_api_key)
    repository = IngestRepository(database_url)
    completed = 0
    failed = 0

    for source in sources:
        try:
            print(f"[INFO] Processing: {source.path}")
            text = extract_text(source)
            print(f"[INFO]   Extracted {len(text)} chars")
            chunks = split_text(text)
            token_counts = [count_tokens(chunk) for chunk in chunks]
            print(f"[INFO]   Created {len(chunks)} chunks")
            embeddings = embedder.embed_many(chunks)
            print("[INFO]   Generated embeddings")
            document_id = run_async(
                repository.upsert_document_with_chunks(source, chunks, embeddings, token_counts)
            )
            print(f"[INFO]   Upserted document: {source.source_url} (id: {document_id})")
            print(f"[INFO]   Inserted {len(chunks)} chunks")
            completed += 1
        except Exception as exc:
            failed += 1
            print(f"[ERROR] {source.path}: {exc}")
            continue

    print(f"[INFO] Completed: {completed}/{len(sources)} files processed, {failed} files failed")


def load_sources(path: Path) -> list[SourceConfig]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return [SourceConfig(**item) for item in data.get("sources", [])]


def extract_text(source: SourceConfig) -> str:
    path = Path(source.path)
    if source.file_type == "markdown":
        return extract_markdown(path)
    if source.file_type == "pdf":
        return extract_pdf(path)
    raise ValueError(f"Unsupported file_type: {source.file_type}")


if __name__ == "__main__":
    main()
