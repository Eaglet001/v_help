from fastapi import APIRouter, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from app.conversation import handle_message  # Your conversation logic
import logging

router = APIRouter()
logger = logging.getLogger("v_help.whatsapp")


@router.post("/whatsapp")
def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
):
    """
    Twilio webhook to handle incoming WhatsApp messages.
    Returns TwiML XML with content-type application/xml so Twilio can parse it.
    """
    try:
        # Clean user ID
        user_id = From.replace("whatsapp:", "")
        message = Body or ""

        logger.info("incoming message from %s", user_id)

        # Get reply from your conversation handler
        reply = handle_message(user_id, message)

        # Build TwiML response (XML)
        twiml = MessagingResponse()
        twiml.message(reply)

        return Response(content=str(twiml), media_type="application/xml")

    except Exception as exc:
        logger.exception("Error handling whatsapp webhook: %s", exc)
        # Return a safe TwiML so Twilio doesn't retry too aggressively
        safe = MessagingResponse()
        safe.message("Sorry, something went wrong. Our team has been notified.")
        return Response(content=str(safe), media_type="application/xml")
