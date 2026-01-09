import os
import logging
import requests

HF_API_TOKEN = os.getenv("HF_TOKEN")  # Hugging Face API token
MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct:novita")

logger = logging.getLogger("v_help.ai")


def llm_fallback(user_message: str) -> str:
    """
    Calls Hugging Face Inference API as a fallback LLM.
    Returns a short string reply or a polite fallback message on error.
    """
    if not HF_API_TOKEN:
        logger.debug("HF_TOKEN not set; skipping LLM call")
        return "Sorry, I didn’t understand that. Type *AGENT* to speak with Esther."

    url = f"https://api-inference.huggingface.co/models/{MODEL}"
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "inputs": f"You are a professional virtual assistant consultant.\nUser: {user_message}\nAssistant:",
        "parameters": {"max_new_tokens": 100, "temperature": 0.3},
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()

        # HF Inference can return a list with 'generated_text' or a dict with 'error'
        if isinstance(data, list) and data and isinstance(data[0], dict):
            if "generated_text" in data[0]:
                return data[0]["generated_text"].strip()

        if isinstance(data, dict) and "error" in data:
            logger.warning("HF inference returned error: %s", data.get("error"))
            return "Sorry, I didn’t understand that. Type *AGENT* to speak with Esther."

        # Fallback generic message
        logger.debug("HF inference returned unexpected shape: %s", type(data))
        return "Sorry, I didn’t understand that. Type *AGENT* to speak with Esther."
    except Exception as exc:
        logger.exception("Error calling HF inference: %s", exc)
        return "Sorry, I didn’t understand that. Type *AGENT* to speak with Esther."
