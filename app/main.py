from fastapi import FastAPI
from app.whatsapp import router

app = FastAPI(title="VA WhatsApp Consultant Bot (Twilio)")

app.include_router(router)

@app.get("/")
def health():
    return {"status": "running"}
