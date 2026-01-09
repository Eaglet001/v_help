from app.services import format_services_menu, SERVICES, FAQS, BOOKING_LINK, SERVICE_DETAILS
from app.ai import llm_fallback  # optional LLM support
import logging
import re

logger = logging.getLogger("v_help.conversation")

# Memory stores for user state and collected data
user_state = {}
user_data = {}


def _is_affirmative(msg: str) -> bool:
    return msg in ("yes", "y", "sure", "ok", "confirm")


def _is_negative(msg: str) -> bool:
    return msg in ("no", "n", "not now", "later", "cancel")


def _match_service(msg: str):
    """Try to map user input to a service key or name. Returns (key, name) or (None, None)."""
    msg_norm = msg.strip().lower()

    # Direct number
    if msg_norm in SERVICES:
        return msg_norm, SERVICES[msg_norm]

    # Direct match on name
    for k, name in SERVICES.items():
        if msg_norm == name.lower():
            return k, name

    # Substring match on service names
    for k, name in SERVICES.items():
        if name.lower() in msg_norm or msg_norm in name.lower():
            return k, name

    # Word overlap heuristic
    words = set(re.findall(r"\w+", msg_norm))
    best = (None, None, 0)
    for k, name in SERVICES.items():
        name_words = set(re.findall(r"\w+", name.lower()))
        score = len(words & name_words)
        if score > best[2]:
            best = (k, name, score)

    if best[0] and best[2] >= 1:
        return best[0], best[1]

    return None, None


def handle_message(user_id: str, message: str) -> str:
    """
    Handles incoming WhatsApp messages from Twilio.

    Args:
        user_id (str): The normalized sender ID (From number without "whatsapp:")
        message (str): The incoming text message

    Returns:
        str: Bot reply
    """
    msg = (message or "").strip()
    msg_low = msg.lower()

    # Basic small-talk and control commands
    if msg_low in ("hi", "hello", "hey", "yo"):
        # show menu and initialize session state for the user so subsequent replies are handled
        user_state[user_id] = "service"
        user_data[user_id] = {}
        return format_services_menu()

    if "menu" in msg_low or "services" in msg_low:
        # explicitly reset to service selection
        user_state[user_id] = "service"
        user_data[user_id] = {}
        return format_services_menu()

    if "thank" in msg_low:
        return "You’re welcome! If you need anything else, type *MENU* to see options."

    # Check FAQs
    for key in FAQS:
        if key in msg_low:
            return FAQS[key]

    # New user: show menu
    if user_id not in user_state:
        user_state[user_id] = "service"
        user_data[user_id] = {}
        return format_services_menu()

    # Get current state
    state = user_state.get(user_id, "service")

    # Rule-based conversation
    if state == "service":
        # allow restart
        if msg_low in ("restart", "start", "start over", "clear"):
            user_state[user_id] = "service"
            user_data[user_id] = {}
            return format_services_menu()

        key, name = _match_service(msg_low)
        if key:
            # user chose a service — show details now and ask to proceed
            user_data[user_id]["service"] = name
            user_state[user_id] = "service_detail"
            # show the detailed description and prompt for confirmation
            try:
                from app.services import format_service_detail

                return format_service_detail(name)
            except Exception:
                # fallback simple message
                return f"You selected *{name}*. Reply YES to proceed or NO to pick another service."

        return "Please select a valid option from the menu (type the number or name). Type *MENU* to see options."

    if state == "hours":
        # validate hours as a small integer
        m = re.search(r"(\d+)", msg_low)
        if m:
            hours = int(m.group(1))
            if hours <= 0 or hours > 168:
                return "Please provide a realistic number of hours per week (1–168). How many hours per week do you need?"
            user_data[user_id]["hours"] = hours
            user_state[user_id] = "business"
            return "Thanks — what type of business do you run? (e.g. Ecommerce, Coaching, SaaS, Local biz)"
        return "I didn't catch the hours. Please reply with a number like '5' or '10'."

    if state == "business":
        user_data[user_id]["business"] = msg
        user_state[user_id] = "budget"
        return "What is your budget range? (e.g. $200–$500 per month)"

    if state == "budget":
        user_data[user_id]["budget"] = msg
        user_state[user_id] = "confirm"
        s = user_data[user_id].get("service")
        h = user_data[user_id].get("hours")
        b = user_data[user_id].get("business")
        bud = user_data[user_id].get("budget")
        summary = (
            f"Summary:\nService: {s}\nHours/week: {h}\nBusiness: {b}\nBudget: {bud}\n\n"
            "Reply *YES* to confirm and receive the booking link."
        )
        return summary

    if state == "confirm":
        if _is_affirmative(msg_low):
            user_state[user_id] = "booked"
            return f"Perfect! 🎯\nYou can book a discovery call here:\n👉 {BOOKING_LINK}\n\nIf you need human help, reply and someone will follow up via text."
        if _is_negative(msg_low):
            user_state[user_id] = "service"
            user_data[user_id] = {}
            return "No problem. I cleared your session. Type *MENU* to start again."
        return "Please reply YES to confirm."

    # removed handoff/agent call flow — this bot is personal-only

    if state == "service_detail":
        # waiting for user to confirm the selected service
        if _is_affirmative(msg_low):
            # proceed to hours collection
            user_state[user_id] = "hours"
            return "Great — how many hours per week would you like for this service? (e.g. 5)"
        if _is_negative(msg_low):
            # let user pick another service
            user_state[user_id] = "service"
            user_data[user_id].pop("service", None)
            return format_services_menu()
        return "Please reply YES to proceed with the selected service, or NO to choose a different one."

    # Fallback: optional LLM response for open-ended messages
    try:
        return llm_fallback(msg)
    except Exception:
        logger.exception("LLM fallback failed")
        return "Sorry, I didn’t understand that. Type *MENU* to see options."
