import asyncio
import random
import time

import httpx

from app.core.config import get_settings
from app.providers.base import ProviderError, ProviderResult


RETRYABLE = {408, 429, 502, 503}
STOP_NOW = {401, 402}


class OpenRouterClient:
    def __init__(self):
        self.settings = get_settings()

    async def chat(self, messages: list[dict], models: list[str], max_retries: int | None = None) -> ProviderResult:
        max_retries = max_retries or self.settings.max_retries
        fallback_used = False
        last_error: ProviderError | None = None
        for model_idx, model in enumerate(models):
            if model_idx > 0:
                fallback_used = True
            attempt = 0
            while attempt <= max_retries:
                attempt += 1
                start = time.time()
                try:
                    payload = {"model": model, "messages": messages, "temperature": 0.2}
                    async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                        resp = await client.post(
                            f"{self.settings.openrouter_base_url}/chat/completions",
                            headers={"Authorization": f"Bearer {self.settings.openrouter_api_key}", "Content-Type": "application/json"},
                            json=payload,
                        )
                    if resp.status_code >= 400:
                        raise ProviderError(f"OpenRouter error {resp.status_code}: {resp.text[:200]}", code=resp.status_code)
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    _ = int((time.time() - start) * 1000)
                    return ProviderResult(content=content, model=model, attempts=attempt, fallback_used=fallback_used)
                except ProviderError as exc:
                    last_error = exc
                    if exc.code in STOP_NOW:
                        raise
                    if exc.code == 404:
                        break
                    if exc.code not in RETRYABLE or attempt > max_retries:
                        break
                    delay = min(8, (2 ** (attempt - 1)) + random.random())
                    await asyncio.sleep(delay)
                except (httpx.TimeoutException, httpx.RequestError) as exc:
                    last_error = ProviderError(str(exc), code=408)
                    if attempt > max_retries:
                        break
                    delay = min(8, (2 ** (attempt - 1)) + random.random())
                    await asyncio.sleep(delay)

        if last_error:
            raise last_error
        raise ProviderError("All models failed")
