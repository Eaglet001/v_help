from fastapi import APIRouter, Form, Response, BackgroundTasks
from twilio.twiml.messaging_response import MessagingResponse
from app.conversation import handle_message  # Your conversation logic
from app.twilio_client import place_agent_call
import logging

router = APIRouter()
logger = logging.getLogger("v_help.whatsapp")


@router.post("/whatsapp")
def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    background_tasks: BackgroundTasks = None,
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

        # If the user asked for an agent, schedule a background call to connect them.
        # We detect common forms of the agent request here to ensure the call is placed.
        if message and "agent" in message.lower():
            # normalize phone number from "whatsapp:+123..." to "+123..."
            user_phone = From.replace("whatsapp:", "")
            logger.info("scheduling agent call to %s", user_phone)
            if background_tasks is not None:
                background_tasks.add_task(place_agent_call, user_phone)
            else:
                # fallback synchronous attempt
                place_agent_call(user_phone)

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
