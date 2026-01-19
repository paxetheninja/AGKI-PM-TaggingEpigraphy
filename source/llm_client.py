from abc import ABC, abstractmethod
import json
from typing import Any, Dict, Optional
import os
import datetime
from pathlib import Path
from openai import OpenAI
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .config import LOGS_DIR

# Global session timestamp for this run
SESSION_TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def log_interaction(model: str, system: str, user: str, response: str):
    """Logs the full LLM interaction to a unique log file for this run."""
    log_file = LOGS_DIR / f"llm_trace_{SESSION_TIMESTAMP}.log"
    
    entry = f"""
{'='*80}
TIMESTAMP: {datetime.datetime.now().isoformat()}
MODEL: {model}
{'='*80}
[SYSTEM PROMPT]:
{system}
{'-'*40}
[USER PROMPT]:
{user}
{'-'*40}
[RAW RESPONSE]:
{response}
{'='*80}
"""
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)

import re

def clean_json_response(text: str) -> str:
    """Removes markdown code blocks and other common LLM artifacts from JSON strings."""
    # If it starts with ``` and ends with ```, extract the content
    if "```" in text:
        # Match ```json ... ``` or ``` ... ```
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            text = match.group(1)
        else:
            # Fallback: just remove the backticks
            text = re.sub(r"```(?:json)?", "", text)
            text = text.strip("` \n\r")
    
    text = text.strip()

    # If it doesn't end with } or ], it might be truncated.
    # We only want to cut off if we are SURE we found the last valid object/array.
    # For now, let's just let json.loads fail naturally if it's truncated, 
    # but try to strip trailing garbage if present.
    
    return text

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
            
            content = clean_json_response(content)
            log_interaction(model, system_prompt, user_prompt, content)
            return json.loads(content)
        except Exception as e:
            print(f"OpenAI Error: {e}")
            raise e

class GoogleClient(LLMProvider):
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=5, max=60),
        reraise=True
    )
    def generate_json(self, system_prompt: str, user_prompt: str, model: str) -> Dict[str, Any]:
        try:
            # Config for the new SDK
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0,
                top_p=0.95,
                top_k=64,
                max_output_tokens=65536,
                response_mime_type="application/json",
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT",
                        threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH",
                        threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="BLOCK_NONE"
                    ),
                ]
            )
            
            print(f"Calling Gemini model (new SDK): {model}")
            response = self.client.models.generate_content(
                model=model,
                contents=user_prompt,
                config=config
            )
            
            if not response.text:
                raise ValueError("Empty response text from Gemini")
                
            text = clean_json_response(response.text)
            log_interaction(model, system_prompt, user_prompt, text)
            return json.loads(text)
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