import os
import logging
from typing import Optional

logger = logging.getLogger("v_help.twilio")


def place_agent_call(user_phone: str) -> bool:
    """Place an outbound call to the user and bridge to the agent number.

    This uses Twilio REST API. Environment variables required:
      - TWILIO_ACCOUNT_SID
      - TWILIO_AUTH_TOKEN
      - TWILIO_CALLER_NUMBER (your Twilio phone number, e.g. +1xxx)
      - AGENT_NUMBER (the agent/office phone to dial and bridge)

    Returns True on success, False otherwise.
    """
    try:
        from twilio.rest import Client
    except Exception:
        logger.exception("twilio library not available; cannot place call")
        return False

    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    caller = os.getenv("TWILIO_CALLER_NUMBER")
    agent = os.getenv("AGENT_NUMBER")

    if not all([sid, token, caller, agent]):
        logger.warning("Missing Twilio configuration; call not placed (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_CALLER_NUMBER, AGENT_NUMBER required)")
        return False

    try:
        client = Client(sid, token)

        # TwiML: when the user answers, Twilio will Dial the agent number and bridge both parties
        twiml = f"<Response><Say voice=\"alice\">Connecting you to an agent. Please hold.</Say><Dial>{agent}</Dial></Response>"

        call = client.calls.create(
            to=user_phone,
            from_=caller,
            twiml=twiml,
            timeout=60,
        )
        logger.info("Placed call to %s, sid=%s", user_phone, getattr(call, "sid", "-"))
        return True
    except Exception as exc:
        logger.exception("Failed to place call to %s: %s", user_phone, exc)
        return False
