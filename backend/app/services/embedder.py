from openai import AsyncOpenAI


class EmbeddingClient:
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def embed(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding

