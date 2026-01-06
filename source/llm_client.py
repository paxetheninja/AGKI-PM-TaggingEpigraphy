from abc import ABC, abstractmethod
import json
from typing import Any, Dict, Optional
import os
from openai import OpenAI
import google.generativeai as genai
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
        except Exception as e:
            print(f"OpenAI Error: {e}")
            raise e

class GoogleClient(LLMProvider):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_json(self, system_prompt: str, user_prompt: str, model: str) -> Dict[str, Any]:
        try:
            # For Gemini, we typically prepend the system prompt to the user message
            # or use the specific system_instruction parameter if supported by the model version
            generation_config = {
                "temperature": 0.0,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
            }
            
            gemini_model = genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config,
                system_instruction=system_prompt
            )
            
            response = gemini_model.generate_content(user_prompt)
            
            if not response.text:
                raise ValueError("Empty response from Gemini")
                
            return json.loads(response.text)
        except Exception as e:
            print(f"Google Gemini Error: {e}")
            raise e

def get_llm_client() -> LLMProvider:
    """Factory to get the configured LLM client."""
    from .config import DEFAULT_MODEL_PROVIDER, OPENAI_API_KEY, GOOGLE_API_KEY
    
    if DEFAULT_MODEL_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found.")
        return OpenAIClient(api_key=OPENAI_API_KEY)
    
    elif DEFAULT_MODEL_PROVIDER == "google":
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found.")
        return GoogleClient(api_key=GOOGLE_API_KEY)
    
    else:
        raise ValueError(f"Unknown provider: {DEFAULT_MODEL_PROVIDER}")