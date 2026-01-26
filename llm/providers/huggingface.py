import requests
from llm.types import LLMResponse
from app.config import HUGGINGFACE_API_KEY

class HuggingFaceProvider:
    name = "huggingface"
    
    # Using currently active models (as of 2026)
    # Option 1: Mistral (most reliable)
    model_id = "google/flan-t5-base"
    
    # Option 2: Microsoft Phi
    # model_id = "microsoft/Phi-3-mini-4k-instruct"
    
    # Option 3: Google Gemma
    # model_id = "google/gemma-2-2b-it"
    
    # Option 4: Qwen
    # model_id = "Qwen/Qwen2.5-7B-Instruct"
    
    def generate(self, prompt: str, context=None) -> LLMResponse:
        if not HUGGINGFACE_API_KEY:
            raise RuntimeError("HF API key missing")
        
        # Use the standard inference API
        url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            },
            "options": {
                "wait_for_model": True  # Wait if model is loading
            }
        }
        
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=120)
            
            if r.status_code == 410:
                raise RuntimeError(
                    f"Model '{self.model_id}' is deprecated. "
                    f"Try: 'mistralai/Mistral-7B-Instruct-v0.3' or 'microsoft/Phi-3-mini-4k-instruct'"
                )
            
            if r.status_code == 503:
                error_data = r.json()
                wait_time = error_data.get("estimated_time", 20)
                raise RuntimeError(
                    f"Model is loading. Estimated wait: {wait_time} seconds. Please retry."
                )
            
            if r.status_code == 401:
                raise RuntimeError("Invalid API key. Check HUGGINGFACE_API_KEY in your config.")
            
            if r.status_code == 404:
                raise RuntimeError(f"Model '{self.model_id}' not found.")
            
            r.raise_for_status()
            
            data = r.json()
            
            # Parse response
            if isinstance(data, list) and len(data) > 0:
                if "generated_text" in data[0]:
                    text = data[0]["generated_text"]
                elif "translation_text" in data[0]:
                    text = data[0]["translation_text"]
                else:
                    text = str(data[0])
            elif isinstance(data, dict) and "generated_text" in data:
                text = data["generated_text"]
            else:
                raise RuntimeError(f"Unexpected response format: {data}")
            
            return LLMResponse(
                text=text.strip(),
                model=self.model_id,
                provider="HuggingFace"
            )
            
        except requests.exceptions.Timeout:
            raise RuntimeError("Request timed out. The model might be loading - try again in a moment.")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"HuggingFace API error: {str(e)}")