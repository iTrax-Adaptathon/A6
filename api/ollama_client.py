import os
import requests
import json
from typing import Dict, Any

def ask_ollama(prompt: str, json_format: bool = False) -> str:
    """
    Centralized client to communicate with the local Ollama instance.
    Handles fallbacks and ensures valid string returns even on connection failure.
    """
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    base_url = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
    url = f"{base_url}/api/generate"
    timeout = int(os.getenv("OLLAMA_TIMEOUT", "90"))
    
    payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    if json_format:
        payload["format"] = "json"
        
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "{}" if json_format else "")
    except requests.exceptions.Timeout:
        print(f"[Ollama Error] Request timed out after {timeout}s using model '{model}' at {url}")
        return "{}" if json_format else ""
    except requests.exceptions.RequestException as e:
        print(f"[Ollama Error] Could not connect to Ollama at {url}: {e}")
        return "{}" if json_format else ""
