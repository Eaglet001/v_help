WELCOME_MESSAGE = (
    "Hi 👋 Welcome!\n"
    "I’m Esther's virtual assistant.\n\n"
    "Choose a service from the list below by typing the number or the name.\n"
)

SERVICES = {
    "1": "Administrative Support",
    "2": "Social Media Management",
    "3": "Customer Support",
    "4": "Email & Calendar Management",
    "5": "Project Management",
    "6": "Bookkeeping & Invoicing",
    "7": "Content Writing & Copy",
    "8": "Other",
}

SERVICE_DETAILS = {
    "Administrative Support": "Email triage, scheduling, data entry, and general ops.",
    "Social Media Management": "Content calendars, post scheduling, and community engagement.",
    "Customer Support": "Tickets, FAQs, chat handling, and follow-ups.",
    "Email & Calendar Management": "Inbox management, meeting scheduling, and reminders.",
    "Project Management": "Task tracking, status updates, and coordination across teams.",
    "Bookkeeping & Invoicing": "Expense tracking, invoicing, and basic bookkeeping.",
    "Content Writing & Copy": "Blog posts, landing pages, captions, and email copy.",
    "Other": "Tell us more about what you need and we’ll match you with the right expertise.",
}

FAQS = {
    "pricing": "Pricing depends on workload and hours. A discovery call will help us decide.",
    "availability": "Available Monday–Friday with flexible hours.",
    "tools": "Google Workspace, Notion, Slack, Trello, common CRMs.",
    "trial": "We offer a short onboarding call and a trial period for new clients.",
}

BOOKING_LINK = "https://calendly.com/yourfriend"


def format_services_menu() -> str:
    """Return a nicely formatted services menu for display in WhatsApp."""
    lines = [WELCOME_MESSAGE, "Options:"]
    for k in sorted(SERVICES.keys(), key=lambda x: int(x)):
        name = SERVICES[k]
        desc = SERVICE_DETAILS.get(name, "")
        lines.append(f"{k}. {name} — {desc}")

    lines.append("\nReply with the number or service name. Type *AGENT* to speak to a human.")
    return "\n".join(lines)


