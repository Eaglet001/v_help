from fastapi import APIRouter, Form
from twilio.twiml.messaging_response import MessagingResponse
from app.conversation import handle_message  # your corrected handler

router = APIRouter()

@router.post("/whatsapp")
def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...)
):
    """
    Handles incoming WhatsApp messages via Twilio.
    """
    user_id = From.replace("whatsapp:", "")  # normalize user ID
    message = Body

    # Get bot reply
    reply_text = handle_message(message, user_id)

    # Prepare Twilio response
    response = MessagingResponse()
    response.message(reply_text)

    return str(response)
