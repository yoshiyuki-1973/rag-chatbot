from openai import AsyncOpenAI

from app.adapters.llm.base import BaseLLMClient


class GrokLLMClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str):
        self.client = AsyncOpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
        self.model = model

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1000,
        temperature: float = 0.1,
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

