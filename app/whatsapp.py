from fastapi import APIRouter, Form
from twilio.twiml.messaging_response import MessagingResponse
from app.conversation import handle_message

router = APIRouter()

@router.post("/whatsapp")
def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)):
    user_id = From.replace("whatsapp:", "")
    message = Body

    reply = handle_message(user_id, message)

    twilio_response = MessagingResponse()
    twilio_response.message(reply)

    return str(twilio_response)
