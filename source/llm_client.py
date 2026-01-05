from abc import ABC, abstractmethod
import json
from typing import Any, Dict, Optional
import os
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMProvider(ABC):
    @abstractmethod
    def generate_json(self, system_prompt: str, user_prompt: str, model: str) -> Dict[str, Any]:
        """Generates a JSON response from the LLM."""
        pass

class OpenAIClient(LLMProvider):
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_json(self, system_prompt: str, user_prompt: str, model: str) -> Dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from LLM")
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Simple retry logic could be added here or handled by the caller
            raise ValueError(f"Failed to parse JSON: {e}")
        except Exception as e:
            print(f"LLM Error: {e}")
            raise e

def get_llm_client() -> LLMProvider:
    """Factory to get the configured LLM client."""
    # For now, defaults to OpenAI. Could be expanded to switch based on config.
    from .config import OPENAI_API_KEY
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
    return OpenAIClient(api_key=OPENAI_API_KEY)
