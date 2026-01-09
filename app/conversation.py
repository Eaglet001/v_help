from app.services import WELCOME_MESSAGE, SERVICES, FAQS, BOOKING_LINK
from app.ai import llm_fallback  # optional LLM support

# Memory store for state & data
user_state = {}
user_data = {}

def handle_message(message: str, user_id: str) -> str:
    """
    Process incoming user messages and return the bot's reply.
    """
    msg = message.lower().strip()

    # Human handoff
    if msg == "agent":
        user_state[user_id] = "handoff"
        return "👩‍💼 Esther has been notified and will respond shortly."

    # Check FAQs (case-insensitive)
    for key, answer in FAQS.items():
        if key.lower() in msg:
            return answer

    # New user
    if user_id not in user_state:
        user_state[user_id] = "service"
        user_data[user_id] = {}
        return WELCOME_MESSAGE

    state = user_state[user_id]

    # Rule-based conversation flow
    if state == "service":
        if msg in SERVICES:
            user_data[user_id]["service"] = SERVICES[msg]
            user_state[user_id] = "hours"
            return "Great choice! ✅\nHow many hours per week do you need?"
        return "Please select a valid option (1–5)."

    if state == "hours":
        user_data[user_id]["hours"] = msg
        user_state[user_id] = "business"
        return "What type of business do you run?"

    if state == "business":
        user_data[user_id]["business"] = msg
        user_state[user_id] = "budget"
        return "What is your budget range?"

    if state == "budget":
        user_data[user_id]["budget"] = msg
        user_state[user_id] = "booking"
        return (
            f"Perfect! 🎯\n\n"
            f"You can book a free discovery call here:\n👉 {BOOKING_LINK}\n\n"
            "Type *AGENT* to speak directly with Sarah."
        )

    # Human handoff or unknown state
    if state == "handoff":
        return "👩‍💼 Please wait, an agent will respond shortly."

    # Fallback: LLM support
    if llm_fallback:
        return llm_fallback(msg)

    return "Sorry, I didn't understand that. Please try again."
