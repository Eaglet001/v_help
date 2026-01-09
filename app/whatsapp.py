# app/whatsapp.py
from fastapi import APIRouter, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

router = APIRouter()

@router.post("/whatsapp")
def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)):
    # Create Twilio response
    resp = MessagingResponse()
    resp.message(f"You said: {Body}")

    # Return XML with proper Content-Type
    return Response(content=str(resp), media_type="text/xml")
