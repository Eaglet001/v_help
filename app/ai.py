import os
import requests

HF_API_TOKEN = os.getenv("HF_TOKEN")  # Hugging Face API token
MODEL = "meta-llama/Llama-3.1-8B-Instruct:novita"

def llm_fallback(user_message: str) -> str:
    """
    Calls Hugging Face LLaMA API as fallback.
    """
    if not HF_API_TOKEN:
        return "Sorry, I didn’t understand that. Type *AGENT* to speak with Esther."

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": f"You are a professional virtual assistant consultant.\nUser: {user_message}\nAssistant:",
        "parameters": {"max_new_tokens": 100, "temperature": 0.3}
    }

    try:
        response = requests.post(
            model="meta-llama/Llama-3.1-8B-Instruct:novita",
            headers=headers,
            json=payload,
            timeout=10
        )
        data = response.json()
        # Hugging Face returns list of outputs
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        else:
            return "Sorry, I didn’t understand that. Type *AGENT* to speak with Esther."
    except:
        return "Sorry, I didn’t understand that. Type *AGENT* to speak with Esther."
