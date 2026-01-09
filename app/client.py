import subprocess

# Default user and role settings
API_KEY = "mysecretkey"
USER_ROLE = "admin"
USER_NAME = "atish"  # change if needed

def query_llama3(prompt, user=USER_NAME):
    """
    Query the local Ollama LLaMA3 model.
    Returns the model's response or a clear error message if Ollama is not running.
    """
    try:
        # Call Ollama CLI with the llama3 model
        result = subprocess.run(
            ["ollama", "run", "llama3", prompt],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: Ollama returned code {result.returncode}\n{result.stderr}"
    except Exception as e:
        return f"Ollama not running or failed: {e}"