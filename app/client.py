import requests

# Default user and role settings
API_KEY = "mysecretkey"
USER_ROLE = "notadmin"
USER_NAME = "atish"  # change if needed

# Ollama API configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

def query_llama3(prompt, user=USER_NAME):
    """
    Query the local Ollama LLaMA3 model via REST API.
    Returns the model's response or a clear error message if Ollama is not running.
    """
    try:
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "No response from model").strip()
        else:
            return f"Error: Ollama API returned status {response.status_code}\n{response.text}"
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Make sure Ollama is running on http://localhost:11434"
    except requests.exceptions.Timeout:
        return "Error: Request to Ollama timed out"
    except Exception as e:
        return f"Error: Ollama request failed: {e}"