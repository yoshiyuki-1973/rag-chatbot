import time

from openai import OpenAI


class EmbeddingBatchClient:
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed_many(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        embeddings: list[list[float]] = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            response = None
            for attempt in range(1, 4):
                try:
                    response = self.client.embeddings.create(model=self.model, input=batch)
                    break
                except Exception:
                    if attempt == 3:
                        raise
                    time.sleep(2 ** (attempt - 1))
            embeddings.extend(item.embedding for item in response.data)
        return embeddings
