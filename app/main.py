from fastapi import FastAPI
from app.whatsapp import router
import logging

app = FastAPI(title="VA WhatsApp Consultant Bot (Twilio)")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("v_help")

app.include_router(router)


@app.get("/")
def health():
    """Simple health endpoint for Render / uptime checks."""
    logger.debug("health check requested")
    return {"status": "running"}