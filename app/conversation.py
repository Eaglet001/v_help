"""
Advanced Virtual Assistant Conversation Manager
Professional AI-powered conversational framework with NLU, context awareness, and intelligent routing
"""

from typing import Dict, Optional, Tuple, List, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import logging
import re
from datetime import datetime, timedelta
from collections import deque

from app.services import (
    format_services_menu, 
    SERVICES, 
    FAQS, 
    BOOKING_LINK, 
    format_service_detail
)
from app.ai import llm_fallback

logger = logging.getLogger("v_help.conversation")


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class ConversationState(Enum):
    """Enumeration of all possible conversation states"""
    INITIAL = "initial"
    SERVICE_SELECTION = "service"
    SERVICE_DETAIL = "service_detail"
    HOURS_COLLECTION = "hours"
    BUSINESS_TYPE = "business"
    BUDGET_COLLECTION = "budget"
    CONFIRMATION = "confirm"
    COMPLETED = "booked"
    HUMAN_HANDOFF = "human_handoff"
    FAQ_MODE = "faq"
    ERROR = "error"


class Intent(Enum):
    """User intent classification"""
    GREETING = "greeting"
    SERVICE_INQUIRY = "service_inquiry"
    BOOKING = "booking"
    FAQ = "faq"
    HELP = "help"
    RESTART = "restart"
    CONFIRMATION = "confirmation"
    REJECTION = "rejection"
    HUMAN_REQUEST = "human_request"
    SMALL_TALK = "small_talk"
    COMPLAINT = "complaint"
    UNKNOWN = "unknown"


class SentimentScore(Enum):
    """Sentiment analysis scores"""
    VERY_POSITIVE = 2
    POSITIVE = 1
    NEUTRAL = 0
    NEGATIVE = -1
    VERY_NEGATIVE = -2


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ConversationContext:
    """Tracks conversation context and history"""
    messages: deque = field(default_factory=lambda: deque(maxlen=10))
    intents: deque = field(default_factory=lambda: deque(maxlen=5))
    sentiment_scores: List[int] = field(default_factory=list)
    topics_discussed: set = field(default_factory=set)
    clarification_attempts: int = 0
    
    def add_message(self, role: str, content: str, intent: Intent = None):
        """Add message to context history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
            "intent": intent.value if intent else None
        })
        if intent:
            self.intents.append(intent)
    
    def get_recent_intents(self, count: int = 3) -> List[Intent]:
        """Get recent intents for pattern detection"""
        return list(self.intents)[-count:]
    
    def add_sentiment(self, score: SentimentScore):
        """Track sentiment over time"""
        self.sentiment_scores.append(score.value)
    
    def get_average_sentiment(self) -> float:
        """Calculate average sentiment"""
        if not self.sentiment_scores:
            return 0.0
        return sum(self.sentiment_scores) / len(self.sentiment_scores)
    
    def is_frustrated(self) -> bool:
        """Detect user frustration"""
        if len(self.sentiment_scores) < 3:
            return False
        recent = self.sentiment_scores[-3:]
        return all(s < 0 for s in recent) or self.clarification_attempts > 2


@dataclass
class UserSession:
    """Enhanced user session with context awareness"""
    user_id: str
    state: ConversationState = ConversationState.INITIAL
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Collected data
    service: Optional[str] = None
    service_key: Optional[str] = None
    hours_per_week: Optional[int] = None
    business_type: Optional[str] = None
    budget: Optional[str] = None
    
    # Conversation metadata
    message_count: int = 0
    error_count: int = 0
    context: ConversationContext = field(default_factory=ConversationContext)
    
    # User preferences (learned over time)
    preferred_response_style: str = "professional"  # professional, casual, concise
    timezone: Optional[str] = None
    language_preference: str = "en"
    
    def update_timestamp(self):
        """Update last activity timestamp"""
        self.last_updated = datetime.now()
        self.message_count += 1
    
    def increment_error(self):
        """Track errors for user experience monitoring"""
        self.error_count += 1
    
    def reset(self, keep_preferences: bool = True):
        """Reset session to initial state"""
        old_style = self.preferred_response_style
        old_tz = self.timezone
        
        self.state = ConversationState.SERVICE_SELECTION
        self.service = None
        self.service_key = None
        self.hours_per_week = None
        self.business_type = None
        self.budget = None
        self.context = ConversationContext()
        
        if keep_preferences:
            self.preferred_response_style = old_style
            self.timezone = old_tz
        
        self.update_timestamp()
    
    def is_session_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has timed out"""
        return datetime.now() - self.last_updated > timedelta(minutes=timeout_minutes)
    
    def to_dict(self) -> Dict:
        """Serialize session for storage"""
        return {
            "user_id": self.user_id,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "service": self.service,
            "service_key": self.service_key,
            "hours_per_week": self.hours_per_week,
            "business_type": self.business_type,
            "budget": self.budget,
            "message_count": self.message_count,
            "preferred_response_style": self.preferred_response_style
        }


# ============================================================================
# NLU - NATURAL LANGUAGE UNDERSTANDING
# ============================================================================

class IntentClassifier:
    """Classifies user intent from messages"""
    
    # Intent patterns
    PATTERNS = {
        Intent.GREETING: [
            r'\b(hi|hello|hey|good morning|good afternoon|good evening|yo|sup)\b',
        ],
        Intent.RESTART: [
            r'\b(restart|reset|start over|clear|begin again|new session)\b',
        ],
        Intent.CONFIRMATION: [
            r'\b(yes|yep|yeah|sure|ok|okay|correct|right|confirm|proceed|continue|absolutely|definitely)\b',
        ],
        Intent.REJECTION: [
            r'\b(no|nope|not now|later|cancel|back|nevermind|nah|negative|wrong)\b',
        ],
        Intent.HUMAN_REQUEST: [
            r'\b(speak to|talk to|human|person|agent|representative|real person|someone|help me)\b',
            r'\b(customer service|support|assistance)\b',
        ],
        Intent.HELP: [
            r'\b(help|assist|support|guide|how do|how to|what can you|confused)\b',
        ],
        Intent.FAQ: [
            r'\b(pricing|price|cost|hours|availability|how long|when|location|contact)\b',
        ],
        Intent.COMPLAINT: [
            r'\b(terrible|horrible|bad|worst|disappointed|frustrated|angry|upset|useless)\b',
        ],
    }
    
    @classmethod
    def classify(cls, message: str, context: ConversationContext) -> Intent:
        """
        Classify user intent with context awareness
        
        Args:
            message: User's message
            context: Conversation context for pattern detection
            
        Returns:
            Detected Intent
        """
        msg_low = message.lower().strip()
        
        # Check patterns in priority order
        for intent, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, msg_low):
                    logger.info(f"Intent detected: {intent.value} from pattern: {pattern}")
                    return intent
        
        # Context-based intent detection
        recent_intents = context.get_recent_intents(2)
        
        # If user previously rejected and now provides info, it's likely a correction
        if Intent.REJECTION in recent_intents:
            if len(msg_low.split()) > 2:  # Substantial response
                return Intent.SERVICE_INQUIRY
        
        # Check if message contains numbers (likely hours or budget)
        if re.search(r'\d+', msg_low):
            return Intent.SERVICE_INQUIRY
        
        return Intent.UNKNOWN


class SentimentAnalyzer:
    """Analyzes sentiment of user messages"""
    
    POSITIVE_WORDS = {
        "great", "awesome", "perfect", "excellent", "wonderful", "fantastic",
        "love", "amazing", "good", "nice", "thanks", "thank you", "appreciate"
    }
    
    NEGATIVE_WORDS = {
        "bad", "terrible", "horrible", "worst", "hate", "awful", "poor",
        "frustrated", "angry", "upset", "disappointed", "useless", "waste"
    }
    
    @classmethod
    def analyze(cls, message: str) -> SentimentScore:
        """
        Analyze sentiment of message
        
        Returns:
            SentimentScore indicating message sentiment
        """
        msg_low = message.lower()
        words = set(re.findall(r'\b\w+\b', msg_low))
        
        positive_count = len(words & cls.POSITIVE_WORDS)
        negative_count = len(words & cls.NEGATIVE_WORDS)
        
        # Check for exclamation marks (can indicate strong emotion)
        exclamation_count = message.count('!')
        
        if negative_count > positive_count + 1:
            return SentimentScore.VERY_NEGATIVE if negative_count >= 3 else SentimentScore.NEGATIVE
        elif positive_count > negative_count + 1:
            return SentimentScore.VERY_POSITIVE if positive_count >= 3 else SentimentScore.POSITIVE
        elif positive_count > negative_count:
            return SentimentScore.POSITIVE
        elif negative_count > positive_count:
            return SentimentScore.NEGATIVE
        
        return SentimentScore.NEUTRAL


class EntityExtractor:
    """Extracts structured entities from messages"""
    
    @staticmethod
    def extract_hours(message: str) -> Optional[int]:
        """Extract hours with advanced pattern matching"""
        patterns = [
            r'(\d+)\s*(?:hours?|hrs?|h)\s*(?:per|\/|a)?\s*(?:week|wk)',
            r'(?:need|want|require)\s*(\d+)\s*(?:hours?|hrs?)',
            r'(\d+)\s*(?:hours?|hrs?)',
            r'\b(\d+)(?:\s*(?:hour|hr))?\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                hours = int(match.group(1))
                if 1 <= hours <= 168:
                    return hours
        
        return None
    
    @staticmethod
    def extract_budget(message: str) -> Optional[str]:
        """Extract budget information"""
        patterns = [
            r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?(?:\s*-\s*\$?\s*\d+(?:,\d{3})*(?:\.\d{2})?)?',
            r'\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|usd|\$)',
            r'(?:up to|around|about|approximately)\s*\$?\s*\d+(?:,\d{3})*'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                return match.group(0)
        
        return None
    
    @staticmethod
    def extract_service_preference(message: str, services: Dict) -> Tuple[Optional[str], Optional[str]]:
        """Extract service with fuzzy matching and synonyms"""
        msg_norm = message.strip().lower()
        
        # Service synonyms for better matching
        SYNONYMS = {
            "admin": ["administration", "administrative", "admin support"],
            "social": ["social media", "sm", "social marketing"],
            "content": ["content creation", "content writing", "copywriting"],
            "virtual": ["va", "virtual assistant", "assistant"],
        }
        
        # Direct match
        if msg_norm in services:
            return msg_norm, services[msg_norm]
        
        # Exact name match
        for key, name in services.items():
            if msg_norm == name.lower():
                return key, name
        
        # Synonym matching
        for key, synonyms in SYNONYMS.items():
            for synonym in synonyms:
                if synonym in msg_norm:
                    for svc_key, svc_name in services.items():
                        if key in svc_name.lower():
                            return svc_key, svc_name
        
        # Substring matching
        for key, name in services.items():
            if name.lower() in msg_norm or msg_norm in name.lower():
                return key, name
        
        # Word overlap with higher threshold
        msg_words = set(re.findall(r'\w+', msg_norm))
        best_match = (None, None, 0)
        
        for key, name in services.items():
            name_words = set(re.findall(r'\w+', name.lower()))
            overlap = len(msg_words & name_words)
            
            if overlap > best_match[2]:
                best_match = (key, name, overlap)
        
        if best_match[0] and best_match[2] >= 2:
            return best_match[0], best_match[1]
        
        return None, None


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

class SessionManager:
    """Enhanced session manager with persistence ready"""
    
    def __init__(self, session_timeout: int = 30):
        self._sessions: Dict[str, UserSession] = {}
        self.session_timeout = session_timeout
    
    def get_or_create(self, user_id: str) -> UserSession:
        """Get existing session or create new one"""
        session = self._sessions.get(user_id)
        
        if session:
            # Check for timeout
            if session.is_session_expired(self.session_timeout):
                logger.info(f"Session expired for user {user_id}, creating new session")
                session = UserSession(user_id=user_id)
                self._sessions[user_id] = session
        else:
            session = UserSession(user_id=user_id)
            self._sessions[user_id] = session
            logger.info(f"Created new session for user {user_id}")
        
        return session
    
    def get(self, user_id: str) -> Optional[UserSession]:
        """Get session if exists"""
        return self._sessions.get(user_id)
    
    def reset_session(self, user_id: str, keep_preferences: bool = True) -> UserSession:
        """Reset user session"""
        session = self.get_or_create(user_id)
        session.reset(keep_preferences=keep_preferences)
        logger.info(f"Reset session for user {user_id}")
        return session
    
    def delete_session(self, user_id: str):
        """Delete user session"""
        if user_id in self._sessions:
            del self._sessions[user_id]
            logger.info(f"Deleted session for user {user_id}")
    
    def export_session(self, user_id: str) -> Optional[Dict]:
        """Export session for persistence"""
        session = self.get(user_id)
        return session.to_dict() if session else None
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self._sessions)


# ============================================================================
# RESPONSE GENERATOR
# ============================================================================

class ResponseGenerator:
    """Generates context-aware, personalized responses"""
    
    @staticmethod
    def generate_empathetic_response(sentiment: SentimentScore, base_message: str) -> str:
        """Add empathy based on sentiment"""
        if sentiment == SentimentScore.VERY_NEGATIVE:
            prefix = "I understand your frustration. "
        elif sentiment == SentimentScore.NEGATIVE:
            prefix = "I hear you. "
        elif sentiment == SentimentScore.VERY_POSITIVE:
            prefix = "I'm so glad to hear that! "
        elif sentiment == SentimentScore.POSITIVE:
            prefix = "Great! "
        else:
            prefix = ""
        
        return prefix + base_message
    
    @staticmethod
    def format_for_style(message: str, style: str) -> str:
        """Format response based on user's preferred style"""
        if style == "casual":
            # More casual, friendly tone
            message = message.replace("Please", "").strip()
            message = message.replace("Thank you", "Thanks")
        elif style == "concise":
            # Remove extra pleasantries
            message = re.sub(r'(Great!|Perfect!|Awesome!)\s*', '', message)
        # professional is default, no changes needed
        
        return message
    
    @staticmethod
    def add_helpful_hints(state: ConversationState, message: str) -> str:
        """Add contextual hints based on state"""
        hints = {
            ConversationState.SERVICE_SELECTION: "\n\n💡 Tip: You can type the number or name of the service.",
            ConversationState.HOURS_COLLECTION: "\n\n💡 Tip: Just type a number like '10' or '20'.",
        }
        
        hint = hints.get(state, "")
        return message + hint


# ============================================================================
# STATE HANDLERS
# ============================================================================

class StateHandler(ABC):
    """Enhanced base class for state handlers"""
    
    def __init__(self, session_manager: SessionManager, entity_extractor: EntityExtractor):
        self.session_manager = session_manager
        self.entity_extractor = entity_extractor
    
    @abstractmethod
    def handle(self, session: UserSession, message: str, intent: Intent) -> Tuple[str, ConversationState]:
        """Handle message with intent awareness"""
        pass
    
    def handle_human_request(self, session: UserSession) -> Tuple[str, ConversationState]:
        """Handle request for human assistance"""
        logger.info(f"User {session.user_id} requested human assistance")
        
        response = (
            "🤝 I'll connect you with our team!\n\n"
            "A team member will reach out to you shortly via this number.\n"
            "Typical response time: 2-4 hours during business hours.\n\n"
            "In the meantime, would you like me to continue helping you, "
            "or would you prefer to wait for human assistance?"
        )
        
        return response, ConversationState.HUMAN_HANDOFF


class ServiceSelectionHandler(StateHandler):
    """Enhanced service selection with intent awareness"""
    
    def handle(self, session: UserSession, message: str, intent: Intent) -> Tuple[str, ConversationState]:
        # Handle human request
        if intent == Intent.HUMAN_REQUEST:
            return self.handle_human_request(session)
        
        # Handle restart
        if intent == Intent.RESTART:
            session.reset()
            return format_services_menu(), ConversationState.SERVICE_SELECTION
        
        # Try to extract service
        key, name = self.entity_extractor.extract_service_preference(message, SERVICES)
        
        if key and name:
            session.service = name
            session.service_key = key
            session.context.topics_discussed.add(name)
            logger.info(f"User {session.user_id} selected service: {name}")
            
            try:
                detail_message = format_service_detail(name)
            except Exception as e:
                logger.error(f"Error formatting service detail: {e}")
                detail_message = (
                    f"✅ You selected *{name}*.\n\n"
                    "Reply *YES* to proceed or *NO* to choose another service."
                )
            
            return detail_message, ConversationState.SERVICE_DETAIL
        
        # Intelligent clarification
        session.context.clarification_attempts += 1
        
        if session.context.clarification_attempts == 1:
            response = (
                "⚠️ I didn't quite catch which service you'd like.\n\n"
                "Type the *number* or *name* from the menu, like '1' or 'Admin Support'."
            )
        elif session.context.clarification_attempts == 2:
            response = (
                "Let me show you the menu again:\n\n" +
                format_services_menu() +
                "\n\nJust reply with the number (like 1, 2, or 3)."
            )
        else:
            # After multiple attempts, offer human help
            response = (
                "I'm having trouble understanding which service you need.\n\n"
                "Would you like to speak with a team member? Reply *YES* for human help, "
                "or try selecting a service number from the menu."
            )
        
        return response, ConversationState.SERVICE_SELECTION


class ServiceDetailHandler(StateHandler):
    """Handles service confirmation with intent"""
    
    def handle(self, session: UserSession, message: str, intent: Intent) -> Tuple[str, ConversationState]:
        if intent == Intent.CONFIRMATION:
            session.context.clarification_attempts = 0  # Reset
            return (
                "Great choice! 🎯\n\n"
                "How many *hours per week* would you like for this service?\n"
                "(Please provide a number between 1-40 hours)"
            ), ConversationState.HOURS_COLLECTION
        
        if intent == Intent.REJECTION:
            session.service = None
            session.service_key = None
            return (
                "No problem! Let's choose a different service.\n\n" +
                format_services_menu()
            ), ConversationState.SERVICE_SELECTION
        
        return (
            "Please reply:\n"
            "• *YES* to proceed with this service\n"
            "• *NO* to choose a different service"
        ), ConversationState.SERVICE_DETAIL


class HoursCollectionHandler(StateHandler):
    """Collects hours with advanced extraction"""
    
    def handle(self, session: UserSession, message: str, intent: Intent) -> Tuple[str, ConversationState]:
        hours = self.entity_extractor.extract_hours(message)
        
        if hours:
            session.hours_per_week = hours
            session.context.clarification_attempts = 0
            logger.info(f"User {session.user_id} specified {hours} hours/week")
            
            return (
                f"Perfect! {hours} hours per week noted. ✅\n\n"
                "What *type of business* do you run?\n"
                "(e.g., E-commerce, Coaching, SaaS, Local Business, Agency)"
            ), ConversationState.BUSINESS_TYPE
        
        session.context.clarification_attempts += 1
        
        if session.context.clarification_attempts > 2:
            response = (
                "I'm having trouble understanding the hours you need.\n\n"
                "Let me ask differently: Do you need:\n"
                "• Part-time support (5-20 hours/week)?\n"
                "• Full-time support (30-40 hours/week)?\n"
                "• Just a few hours (1-10 hours/week)?"
            )
        else:
            response = (
                "⚠️ Please provide a valid number of hours.\n\n"
                "Example: Type '10' for 10 hours per week\n"
                "(Between 1-40 hours recommended)"
            )
        
        return response, ConversationState.HOURS_COLLECTION


class BusinessTypeHandler(StateHandler):
    """Collects business type information"""
    
    def handle(self, session: UserSession, message: str, intent: Intent) -> Tuple[str, ConversationState]:
        if len(message.strip()) < 2:
            return (
                "⚠️ Please tell me about your business.\n\n"
                "Examples: E-commerce Store, Coaching Business, SaaS Company, Local Retail"
            ), ConversationState.BUSINESS_TYPE
        
        session.business_type = message.strip()
        session.context.clarification_attempts = 0
        logger.info(f"User {session.user_id} business type: {message}")
        
        return (
            f"Got it - {message}! 💼\n\n"
            "What is your *monthly budget* for this service?\n"
            "(e.g., $500-$1000, $2000+, or just type an amount)"
        ), ConversationState.BUDGET_COLLECTION


class BudgetCollectionHandler(StateHandler):
    """Collects budget with extraction"""
    
    def handle(self, session: UserSession, message: str, intent: Intent) -> Tuple[str, ConversationState]:
        # Try to extract structured budget
        budget = self.entity_extractor.extract_budget(message)
        
        if not budget and len(message.strip()) >= 2:
            budget = message.strip()  # Accept free-form input
        
        if budget:
            session.budget = budget
            session.context.clarification_attempts = 0
            logger.info(f"User {session.user_id} budget: {budget}")
            
            # Generate confirmation summary
            summary = (
                "📋 *Booking Summary*\n"
                "━━━━━━━━━━━━━━━━\n"
                f"Service: *{session.service}*\n"
                f"Hours/Week: *{session.hours_per_week}*\n"
                f"Business: *{session.business_type}*\n"
                f"Budget: *{session.budget}*\n"
                "━━━━━━━━━━━━━━━━\n\n"
                "Does everything look correct?\n"
                "Reply *YES* to confirm and get your booking link."
            )
            
            return summary, ConversationState.CONFIRMATION
        
        return (
            "⚠️ Please provide your budget range.\n\n"
            "Examples:\n"
            "• $500-$1000\n"
            "• Around $2000/month\n"
            "• Up to $5000"
        ), ConversationState.BUDGET_COLLECTION


class ConfirmationHandler(StateHandler):
    """Final confirmation handler"""
    
    def handle(self, session: UserSession, message: str, intent: Intent) -> Tuple[str, ConversationState]:
        if intent == Intent.CONFIRMATION:
            logger.info(f"User {session.user_id} confirmed booking")
            
            response = (
                "🎉 *Perfect! You're all set!*\n\n"
                f"📅 Book your discovery call here:\n👉 {BOOKING_LINK}\n\n"
                "📱 *What happens next?*\n"
                "1. Schedule your call using the link above\n"
                "2. We'll discuss your needs in detail\n"
                "3. Get a customized proposal\n\n"
                "Need to speak with someone now? Just reply and our team will follow up!\n\n"
                "Type *MENU* anytime to start over."
            )
            
            return response, ConversationState.COMPLETED
        
        if intent == Intent.REJECTION:
            session.reset()
            return (
                "No worries! I've cleared your information. 🔄\n\n" +
                format_services_menu()
            ), ConversationState.SERVICE_SELECTION
        
        return (
            "Please reply:\n"
            "• *YES* to confirm and receive booking link\n"
            "• *NO* to start over"
        ), ConversationState.CONFIRMATION


# ============================================================================
# MAIN CONVERSATION MANAGER
# ============================================================================

class ConversationManager:
    """Advanced AI conversation orchestrator"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.entity_extractor = EntityExtractor()
        self.intent_classifier = IntentClassifier()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.response_generator = ResponseGenerator()
        
        # Initialize state handlers
        self.handlers: Dict[ConversationState, StateHandler] = {
            ConversationState.SERVICE_SELECTION: ServiceSelectionHandler(
                self.session_manager, self.entity_extractor
            ),
            ConversationState.SERVICE_DETAIL: ServiceDetailHandler(
                self.session_manager, self.entity_extractor
            ),
            ConversationState.HOURS_COLLECTION: HoursCollectionHandler(
                self.session_manager, self.entity_extractor
            ),
            ConversationState.BUSINESS_TYPE: BusinessTypeHandler(
                self.session_manager, self.entity_extractor
            ),
            ConversationState.BUDGET_COLLECTION: BudgetCollectionHandler(
                self.session_manager, self.entity_extractor
            ),
            ConversationState.CONFIRMATION: ConfirmationHandler(
                self.session_manager, self.entity_extractor
            ),
        }
    
    def _handle_global_commands(
        self, 
        message: str, 
        session: UserSession, 
        intent: Intent
    ) -> Optional[str]:
        """Handle commands that work in any state"""
        msg_low = message.lower().strip()
        
        # Greeting commands
        if intent == Intent.GREETING:
            session.state = ConversationState.SERVICE_SELECTION
            return (
                "👋 Welcome! I'm your Virtual Assistant.\n\n" +
                format_services_menu()
            )
        
        # Menu request
        if "menu" in msg_low or "services" in msg_low:
            session.state = ConversationState.SERVICE_SELECTION
            return format_services_menu()
        
        # Thank you
        if "thank" in msg_low:
            return (
                "You're very welcome! 😊\n\n"
                "Need anything else? Type *MENU* to see options."
            )
        
        # Check FAQs
        for faq_key, faq_answer in FAQS.items():
            if faq_key in msg_low:
                session.context.add_message("user", message, Intent.FAQ)
                return faq_answer
        
        # Handle frustration
        if session.context.is_frustrated():
            return (
                "I sense you might be frustrated. I'm here to help! 🤝\n\n"
                "Would you like to:\n"
                "• Speak with a team member? (Reply *HUMAN*)\n"
                "• Start fresh? (Reply *RESTART*)\n"
                "• See the menu again? (Reply *MENU*)"
            )
        
        return None
    
    def _analyze_and_log(self, session: UserSession, message: str, intent: Intent):
        """Analyze message and update context"""
        sentiment = self.sentiment_analyzer.analyze(message)
        session.context.add_sentiment(sentiment)
        session.context.add_message("user", message, intent)
        
        logger.info(
            f"User {session.user_id} | State: {session.state.value} | "
            f"Intent: {intent.value} | Sentiment: {sentiment.value}"
        )
    
    def handle_message(self, user_id: str, message: str) -> str:
        """
        Main entry point for handling messages with advanced AI processing
        
        Args:
            user_id: Unique user identifier
            message: User's message text
            
        Returns:
            Bot's response message
        """
        try:
            # Normalize input
            message = (message or "").strip()
            if not message:
                return "Please send a message to continue. Type *MENU* for options."
            
            # Get or create session
            session = self.session_manager.get_or_create(user_id)
            session.update_timestamp()
            
            # Classify intent
            intent = self.intent_classifier.classify(message, session.context)
            
            # Analyze and log
            self._analyze_and_log(session, message, intent)
            
            # Handle global commands first
            global_response = self._handle_global_commands(message, session, intent)
            if global_response:
                session.context.add_message("assistant", global_response)
                return global_response
            
            # Handle completed state
            if session.state == ConversationState.COMPLETED:
                # Allow restart from completed state
                if intent == Intent.RESTART or "menu" in message.lower():
                    session.reset()
                    response = format_services_menu()
                else:
                    response = (
                        "Your booking is complete! ✅\n\n"
                        f"Booking link: {BOOKING_LINK}\n\n"
                        "Type *MENU* to start a new request."
                    )
                session.context.add_message("assistant", response)
                return response
            
            # Handle human handoff state
            if session.state == ConversationState.HUMAN_HANDOFF:
                if intent == Intent.CONFIRMATION:
                    response = (
                        "Perfect! 👤\n\n"
                        "Our team has been notified and will reach out shortly.\n"
                        "You'll receive a message within 2-4 business hours.\n\n"
                        "Feel free to close this chat. We'll contact you soon!"
                    )
                else:
                    # Continue with bot
                    session.state = ConversationState.SERVICE_SELECTION
                    response = (
                        "Great! Let me help you right now. 😊\n\n" +
                        format_services_menu()
                    )
                session.context.add_message("assistant", response)
                return response
            
            # Route to appropriate state handler
            handler = self.handlers.get(session.state)
            
            if handler:
                response, next_state = handler.handle(session, message, intent)
                
                # Apply personalization
                sentiment = session.context.sentiment_scores[-1] if session.context.sentiment_scores else 0
                sentiment_enum = SentimentScore(sentiment)
                
                # Add empathy if sentiment is negative
                if sentiment < 0:
                    response = self.response_generator.generate_empathetic_response(
                        sentiment_enum, response
                    )
                
                # Format for user's style preference
                response = self.response_generator.format_for_style(
                    response, session.preferred_response_style
                )
                
                session.state = next_state
                session.context.add_message("assistant", response)
                
                return response
            
            # Fallback for unknown state
            logger.warning(f"Unknown state {session.state} for user {user_id}")
            session.reset()
            response = (
                "⚠️ Something went wrong. Let's start fresh.\n\n" +
                format_services_menu()
            )
            session.context.add_message("assistant", response)
            return response
        
        except Exception as e:
            logger.exception(f"Error handling message from {user_id}: {e}")
            session = self.session_manager.get(user_id)
            if session:
                session.increment_error()
            
            # Try LLM fallback for graceful degradation
            try:
                llm_response = llm_fallback(message)
                if session:
                    session.context.add_message("assistant", llm_response, Intent.UNKNOWN)
                return llm_response
            except Exception:
                return (
                    "⚠️ I encountered an error. Please try again.\n"
                    "Type *MENU* to see options or reply *HUMAN* for assistance."
                )


# ============================================================================
# ANALYTICS & MONITORING
# ============================================================================

class ConversationAnalytics:
    """Track conversation metrics and insights"""
    
    @staticmethod
    def get_session_summary(session: UserSession) -> Dict[str, Any]:
        """Get comprehensive session summary"""
        return {
            "user_id": session.user_id,
            "state": session.state.value,
            "duration_minutes": (datetime.now() - session.created_at).total_seconds() / 60,
            "message_count": session.message_count,
            "error_count": session.error_count,
            "avg_sentiment": session.context.get_average_sentiment(),
            "is_frustrated": session.context.is_frustrated(),
            "topics_discussed": list(session.context.topics_discussed),
            "completion_percentage": ConversationAnalytics._calculate_completion(session)
        }
    
    @staticmethod
    def _calculate_completion(session: UserSession) -> float:
        """Calculate how far user progressed through flow"""
        state_weights = {
            ConversationState.INITIAL: 0,
            ConversationState.SERVICE_SELECTION: 20,
            ConversationState.SERVICE_DETAIL: 40,
            ConversationState.HOURS_COLLECTION: 60,
            ConversationState.BUSINESS_TYPE: 75,
            ConversationState.BUDGET_COLLECTION: 85,
            ConversationState.CONFIRMATION: 95,
            ConversationState.COMPLETED: 100,
        }
        return state_weights.get(session.state, 0)


# ============================================================================
# PUBLIC API
# ============================================================================

# Global conversation manager instance
_conversation_manager = ConversationManager()


def handle_message(user_id: str, message: str) -> str:
    """
    Public API for handling WhatsApp messages
    
    Args:
        user_id: The normalized sender ID (From number without "whatsapp:")
        message: The incoming text message
    
    Returns:
        Bot reply message
    """
    return _conversation_manager.handle_message(user_id, message)


def reset_user_session(user_id: str, keep_preferences: bool = True):
    """Reset a specific user's session"""
    _conversation_manager.session_manager.reset_session(user_id, keep_preferences)


def get_user_session(user_id: str) -> Optional[UserSession]:
    """Get user session for debugging/monitoring"""
    return _conversation_manager.session_manager.get(user_id)


def get_session_analytics(user_id: str) -> Optional[Dict[str, Any]]:
    """Get analytics for a user session"""
    session = get_user_session(user_id)
    if session:
        return ConversationAnalytics.get_session_summary(session)
    return None


def get_active_sessions() -> int:
    """Get count of active sessions"""
    return _conversation_manager.session_manager.get_active_sessions_count()
                "