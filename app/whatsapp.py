from fastapi import APIRouter, Form
from twilio.twiml.messaging_response import MessagingResponse
from app.conversation import handle_message  # Your conversation logic

router = APIRouter()

@router.post("/whatsapp")
def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...)
):
    """
    Twilio webhook to handle incoming WhatsApp messages
    """
    # Clean user ID
    user_id = From.replace("whatsapp:", "")
    message = Body

    # Get reply from your conversation handler
    reply = handle_message(user_id, message)

    # Build TwiML response (XML)
    twiml = MessagingResponse()
    twiml.message(reply)
    return str(twiml)  # Twilio requires XML, not JSON
