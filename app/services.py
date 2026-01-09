"""
Advanced Service Configuration & Management Module
Professional service catalog with dynamic pricing, recommendations, and analytics
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger("v_help.services")


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class ServiceCategory(Enum):
    """Service categorization for better organization"""
    ADMINISTRATIVE = "administrative"
    MARKETING = "marketing"
    CUSTOMER_SERVICE = "customer_service"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    FINANCIAL = "financial"


class ServiceComplexity(Enum):
    """Complexity level for service scoping"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    CUSTOM = "custom"


class PricingTier(Enum):
    """Pricing tiers for different service levels"""
    STARTER = "starter"  # $300-$800/month
    PROFESSIONAL = "professional"  # $800-$2000/month
    BUSINESS = "business"  # $2000-$5000/month
    ENTERPRISE = "enterprise"  # $5000+/month


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ServicePackage:
    """Detailed service package definition"""
    id: str
    name: str
    display_name: str
    description: str
    detailed_description: str
    category: ServiceCategory
    complexity: ServiceComplexity
    
    # Deliverables and scope
    key_deliverables: List[str] = field(default_factory=list)
    typical_hours_range: Tuple[int, int] = (5, 40)  # Min, Max hours/week
    pricing_tier: PricingTier = PricingTier.PROFESSIONAL
    
    # Requirements and prerequisites
    required_tools: List[str] = field(default_factory=list)
    optional_tools: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    
    # Metadata
    tags: Set[str] = field(default_factory=set)
    related_services: List[str] = field(default_factory=list)
    ideal_business_types: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    requires_consultation: bool = False
    
    def matches_business_type(self, business_type: str) -> bool:
        """Check if service is ideal for given business type"""
        if not self.ideal_business_types:
            return True  # Service is for all business types
        
        business_low = business_type.lower()
        return any(bt.lower() in business_low for bt in self.ideal_business_types)
    
    def get_estimated_price_range(self, hours_per_week: int) -> str:
        """Calculate estimated price based on hours"""
        # Base hourly rates by tier
        hourly_rates = {
            PricingTier.STARTER: (15, 25),
            PricingTier.PROFESSIONAL: (25, 40),
            PricingTier.BUSINESS: (40, 60),
            PricingTier.ENTERPRISE: (60, 100),
        }
        
        min_rate, max_rate = hourly_rates[self.pricing_tier]
        monthly_hours = hours_per_week * 4
        
        min_price = min_rate * monthly_hours
        max_price = max_rate * monthly_hours
        
        return f"${min_price:,.0f} - ${max_price:,.0f}/month"


@dataclass
class FAQ:
    """FAQ item with metadata"""
    id: str
    question: str
    answer: str
    category: str
    keywords: List[str] = field(default_factory=list)
    related_services: List[str] = field(default_factory=list)
    priority: int = 0  # Higher = shown first


# ============================================================================
# SERVICE CATALOG
# ============================================================================

class ServiceCatalog:
    """Comprehensive service catalog with intelligent features"""
    
    def __init__(self):
        self._services: Dict[str, ServicePackage] = {}
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all service packages"""
        
        # 1. Administrative Support
        self.add_service(ServicePackage(
            id="1",
            name="admin_support",
            display_name="Administrative Support",
            description="Email triage, scheduling, data entry, and general ops.",
            detailed_description=(
                "Comprehensive administrative support to keep your business running smoothly. "
                "From inbox management to data organization, we handle the details so you can "
                "focus on growth."
            ),
            category=ServiceCategory.ADMINISTRATIVE,
            complexity=ServiceComplexity.BASIC,
            key_deliverables=[
                "Email triage and response management",
                "Calendar scheduling and coordination",
                "Data entry and database management",
                "Document preparation and filing",
                "Travel arrangements",
                "Meeting preparation and notes"
            ],
            typical_hours_range=(10, 40),
            pricing_tier=PricingTier.PROFESSIONAL,
            required_tools=["Google Workspace", "Microsoft Office"],
            optional_tools=["Notion", "Airtable", "Asana"],
            tags={"admin", "email", "scheduling", "organization"},
            ideal_business_types=["All business types"],
            related_services=["4", "5"]
        ))
        
        # 2. Social Media Management
        self.add_service(ServicePackage(
            id="2",
            name="social_media",
            display_name="Social Media Management",
            description="Content calendars, post scheduling, and community engagement.",
            detailed_description=(
                "Full-service social media management to build your brand presence. "
                "We create engaging content, manage posting schedules, and interact with "
                "your community across all major platforms."
            ),
            category=ServiceCategory.MARKETING,
            complexity=ServiceComplexity.INTERMEDIATE,
            key_deliverables=[
                "Monthly content calendar creation",
                "Daily post scheduling (3-5 posts/day)",
                "Community engagement and responses",
                "Hashtag research and optimization",
                "Analytics reporting (weekly/monthly)",
                "Brand voice consistency"
            ],
            typical_hours_range=(15, 40),
            pricing_tier=PricingTier.PROFESSIONAL,
            required_tools=["Hootsuite/Buffer", "Canva", "Social platforms"],
            optional_tools=["Later", "Sprout Social", "Adobe Creative"],
            tags={"social", "marketing", "content", "engagement"},
            ideal_business_types=["E-commerce", "Coaching", "Agency", "B2C"],
            related_services=["7"]
        ))
        
        # 3. Customer Support
        self.add_service(ServicePackage(
            id="3",
            name="customer_support",
            display_name="Customer Support",
            description="Tickets, FAQs, chat handling, and follow-ups.",
            detailed_description=(
                "Professional customer support that delights your clients. "
                "We handle inquiries, resolve issues, and ensure every customer "
                "interaction reflects your brand values."
            ),
            category=ServiceCategory.CUSTOMER_SERVICE,
            complexity=ServiceComplexity.INTERMEDIATE,
            key_deliverables=[
                "Email and chat support responses",
                "Ticket management and tracking",
                "FAQ documentation",
                "Customer follow-up sequences",
                "Issue escalation handling",
                "Satisfaction surveys"
            ],
            typical_hours_range=(20, 40),
            pricing_tier=PricingTier.PROFESSIONAL,
            required_tools=["Zendesk/Freshdesk", "Email", "Live Chat"],
            optional_tools=["Intercom", "Help Scout", "Slack"],
            tags={"support", "customer service", "tickets", "chat"},
            ideal_business_types=["E-commerce", "SaaS", "Service Business"],
            related_services=["1"]
        ))
        
        # 4. Email & Calendar Management
        self.add_service(ServicePackage(
            id="4",
            name="email_calendar",
            display_name="Email & Calendar Management",
            description="Inbox management, meeting scheduling, and reminders.",
            detailed_description=(
                "Take control of your time with expert email and calendar management. "
                "We organize your inbox, schedule meetings efficiently, and ensure "
                "you never miss important deadlines."
            ),
            category=ServiceCategory.ADMINISTRATIVE,
            complexity=ServiceComplexity.BASIC,
            key_deliverables=[
                "Inbox zero methodology",
                "Priority email flagging",
                "Meeting coordination (with multiple parties)",
                "Calendar optimization",
                "Reminder setup and management",
                "Email template creation"
            ],
            typical_hours_range=(5, 20),
            pricing_tier=PricingTier.STARTER,
            required_tools=["Gmail/Outlook", "Google Calendar"],
            optional_tools=["Calendly", "Notion", "Todoist"],
            tags={"email", "calendar", "scheduling", "inbox"},
            ideal_business_types=["Executives", "Entrepreneurs", "Consultants"],
            related_services=["1"]
        ))
        
        # 5. Project Management
        self.add_service(ServicePackage(
            id="5",
            name="project_management",
            display_name="Project Management",
            description="Task tracking, status updates, and coordination across teams.",
            detailed_description=(
                "Keep projects on track with professional project management support. "
                "We coordinate tasks, track progress, and ensure seamless communication "
                "across all team members."
            ),
            category=ServiceCategory.ADMINISTRATIVE,
            complexity=ServiceComplexity.INTERMEDIATE,
            key_deliverables=[
                "Project planning and roadmaps",
                "Task creation and assignment",
                "Progress tracking and reporting",
                "Team coordination",
                "Deadline management",
                "Stakeholder updates"
            ],
            typical_hours_range=(15, 40),
            pricing_tier=PricingTier.PROFESSIONAL,
            required_tools=["Asana/Trello/Monday", "Slack"],
            optional_tools=["Notion", "ClickUp", "Jira"],
            tags={"project", "management", "coordination", "tracking"},
            ideal_business_types=["Agencies", "SaaS", "Startups", "Teams"],
            related_services=["1"]
        ))
        
        # 6. Bookkeeping & Invoicing
        self.add_service(ServicePackage(
            id="6",
            name="bookkeeping",
            display_name="Bookkeeping & Invoicing",
            description="Expense tracking, invoicing, and basic bookkeeping.",
            detailed_description=(
                "Maintain financial clarity with professional bookkeeping support. "
                "We track expenses, manage invoices, and keep your books organized "
                "for smooth tax season and business decisions."
            ),
            category=ServiceCategory.FINANCIAL,
            complexity=ServiceComplexity.ADVANCED,
            key_deliverables=[
                "Expense categorization and tracking",
                "Invoice generation and follow-up",
                "Receipt management",
                "Monthly financial reports",
                "Accounts receivable tracking",
                "Basic reconciliation"
            ],
            typical_hours_range=(10, 30),
            pricing_tier=PricingTier.BUSINESS,
            required_tools=["QuickBooks/Xero", "Excel/Sheets"],
            optional_tools=["FreshBooks", "Wave", "Expensify"],
            prerequisites=["Must provide access to accounting software"],
            tags={"finance", "bookkeeping", "invoicing", "accounting"},
            ideal_business_types=["Small Business", "Freelancers", "Consultants"],
            related_services=[]
        ))
        
        # 7. Content Writing & Copy
        self.add_service(ServicePackage(
            id="7",
            name="content_writing",
            display_name="Content Writing & Copy",
            description="Blog posts, landing pages, captions, and email copy.",
            detailed_description=(
                "Engage your audience with compelling content that converts. "
                "From blog posts to marketing copy, we create content that "
                "reflects your brand voice and drives results."
            ),
            category=ServiceCategory.CREATIVE,
            complexity=ServiceComplexity.INTERMEDIATE,
            key_deliverables=[
                "Blog posts (4-8 per month)",
                "Landing page copy",
                "Email campaigns and sequences",
                "Social media captions",
                "Product descriptions",
                "SEO optimization"
            ],
            typical_hours_range=(10, 30),
            pricing_tier=PricingTier.PROFESSIONAL,
            required_tools=["Google Docs", "Grammarly"],
            optional_tools=["Hemingway", "Surfer SEO", "WordPress"],
            tags={"content", "writing", "copy", "blog", "seo"},
            ideal_business_types=["E-commerce", "Coaching", "SaaS", "Agencies"],
            related_services=["2"]
        ))
        
        # 8. Other / Custom
        self.add_service(ServicePackage(
            id="8",
            name="custom",
            display_name="Custom Service Package",
            description="Tell us your unique needs and we'll create a custom solution.",
            detailed_description=(
                "Every business is unique. If your needs don't fit our standard packages, "
                "we'll work with you to create a custom service plan tailored specifically "
                "to your requirements and goals."
            ),
            category=ServiceCategory.ADMINISTRATIVE,
            complexity=ServiceComplexity.CUSTOM,
            key_deliverables=[
                "Customized based on consultation",
                "Flexible scope and deliverables",
                "Tailored to your specific needs"
            ],
            typical_hours_range=(5, 40),
            pricing_tier=PricingTier.PROFESSIONAL,
            tags={"custom", "flexible", "tailored"},
            ideal_business_types=["All business types"],
            requires_consultation=True
        ))
    
    def add_service(self, service: ServicePackage):
        """Add a service to the catalog"""
        self._services[service.id] = service
        logger.info(f"Added service: {service.display_name} (ID: {service.id})")
    
    def get_service(self, service_id: str) -> Optional[ServicePackage]:
        """Get service by ID"""
        return self._services.get(service_id)
    
    def get_service_by_name(self, name: str) -> Optional[ServicePackage]:
        """Get service by display name"""
        name_lower = name.lower()
        for service in self._services.values():
            if service.display_name.lower() == name_lower:
                return service
        return None
    
    def get_all_services(self, active_only: bool = True) -> List[ServicePackage]:
        """Get all services"""
        services = list(self._services.values())
        if active_only:
            services = [s for s in services if s.is_active]
        return sorted(services, key=lambda x: int(x.id))
    
    def search_services(self, query: str) -> List[ServicePackage]:
        """Search services by query"""
        query_lower = query.lower()
        results = []
        
        for service in self._services.values():
            # Search in name, description, tags
            if (query_lower in service.display_name.lower() or
                query_lower in service.description.lower() or
                any(query_lower in tag for tag in service.tags)):
                results.append(service)
        
        return results
    
    def get_recommendations(
        self, 
        business_type: Optional[str] = None,
        budget: Optional[str] = None,
        hours: Optional[int] = None
    ) -> List[ServicePackage]:
        """Get personalized service recommendations"""
        services = self.get_all_services()
        scored_services = []
        
        for service in services:
            score = 0
            
            # Business type matching
            if business_type and service.matches_business_type(business_type):
                score += 3
            
            # Hours matching
            if hours:
                min_h, max_h = service.typical_hours_range
                if min_h <= hours <= max_h:
                    score += 2
            
            # Budget matching (simplified)
            if budget and "$" in budget:
                try:
                    budget_num = int(''.join(filter(str.isdigit, budget.split('-')[0])))
                    tier_ranges = {
                        PricingTier.STARTER: (300, 800),
                        PricingTier.PROFESSIONAL: (800, 2000),
                        PricingTier.BUSINESS: (2000, 5000),
                        PricingTier.ENTERPRISE: (5000, 100000),
                    }
                    tier_min, tier_max = tier_ranges[service.pricing_tier]
                    if tier_min <= budget_num <= tier_max:
                        score += 2
                except:
                    pass
            
            if score > 0:
                scored_services.append((service, score))
        
        # Sort by score and return top recommendations
        scored_services.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored_services[:5]]


# ============================================================================
# FAQ MANAGER
# ============================================================================

class FAQManager:
    """Manages FAQs with intelligent search"""
    
    def __init__(self):
        self._faqs: Dict[str, FAQ] = {}
        self._initialize_faqs()
    
    def _initialize_faqs(self):
        """Initialize FAQ database"""
        
        faqs = [
            FAQ(
                id="pricing",
                question="How much does your service cost?",
                answer=(
                    "💰 *Pricing:*\n"
                    "Our pricing depends on the service and hours you need. "
                    "Typical ranges:\n"
                    "• Starter: $300-$800/month (5-15 hours)\n"
                    "• Professional: $800-$2,000/month (15-30 hours)\n"
                    "• Business: $2,000-$5,000/month (30+ hours)\n\n"
                    "Book a discovery call for a custom quote!"
                ),
                category="pricing",
                keywords=["price", "cost", "how much", "pricing", "rate", "fee"],
                priority=10
            ),
            FAQ(
                id="availability",
                question="What are your working hours?",
                answer=(
                    "🕐 *Availability:*\n"
                    "We work Monday–Friday, with flexible hours to match your timezone. "
                    "Standard coverage is 9 AM - 5 PM, with extended hours available "
                    "for certain services. We accommodate most US, UK, and AU time zones."
                ),
                category="general",
                keywords=["hours", "availability", "available", "when", "time", "timezone"],
                priority=8
            ),
            FAQ(
                id="tools",
                question="What tools do you use?",
                answer=(
                    "🛠️ *Tools & Platforms:*\n"
                    "We're experienced with:\n"
                    "• Google Workspace, Microsoft Office\n"
                    "• Notion, Asana, Trello, Monday.com\n"
                    "• Slack, Zoom, Teams\n"
                    "• QuickBooks, Xero, FreshBooks\n"
                    "• Hootsuite, Buffer, Canva\n"
                    "• Most common CRMs and project tools\n\n"
                    "Plus we're quick to learn new platforms!"
                ),
                category="technical",
                keywords=["tools", "software", "platform", "crm", "apps", "use"],
                priority=7
            ),
            FAQ(
                id="trial",
                question="Do you offer a trial period?",
                answer=(
                    "✅ *Trial & Onboarding:*\n"
                    "Yes! We offer:\n"
                    "1. Free 30-minute discovery call\n"
                    "2. Custom proposal and scope\n"
                    "3. 2-week trial period at reduced rate\n"
                    "4. No long-term commitment required\n\n"
                    "This helps ensure we're the right fit for your needs!"
                ),
                category="onboarding",
                keywords=["trial", "test", "try", "onboarding", "start", "begin"],
                priority=9
            ),
            FAQ(
                id="communication",
                question="How do we communicate?",
                answer=(
                    "💬 *Communication:*\n"
                    "We adapt to your preferred method:\n"
                    "• Slack (most common)\n"
                    "• Email\n"
                    "• WhatsApp\n"
                    "• Project management tools\n"
                    "• Weekly check-in calls available\n\n"
                    "We're responsive and keep you updated on all tasks!"
                ),
                category="general",
                keywords=["communicate", "contact", "reach", "talk", "message", "slack"],
                priority=6
            ),
            FAQ(
                id="security",
                question="How do you handle data security?",
                answer=(
                    "🔒 *Security & Confidentiality:*\n"
                    "Your data is safe with us:\n"
                    "• All team members sign NDAs\n"
                    "• We use secure password managers\n"
                    "• 2FA enabled on all accounts\n"
                    "• GDPR and data privacy compliant\n"
                    "• Regular security training\n\n"
                    "We take your privacy seriously!"
                ),
                category="security",
                keywords=["security", "safe", "privacy", "nda", "confidential", "secure"],
                priority=8
            ),
            FAQ(
                id="payment",
                question="What payment methods do you accept?",
                answer=(
                    "💳 *Payment:*\n"
                    "We accept:\n"
                    "• Credit/debit cards (Stripe)\n"
                    "• Bank transfer\n"
                    "• PayPal\n"
                    "• Monthly invoicing\n\n"
                    "Payment terms: Net 7 days. "
                    "Monthly retainers billed at the beginning of each month."
                ),
                category="payment",
                keywords=["payment", "pay", "invoice", "billing", "card", "paypal"],
                priority=7
            ),
            FAQ(
                id="cancellation",
                question="What's your cancellation policy?",
                answer=(
                    "📋 *Cancellation Policy:*\n"
                    "We believe in flexibility:\n"
                    "• 30-day notice for cancellation\n"
                    "• No long-term contracts required\n"
                    "• Monthly rolling agreements\n"
                    "• Scale up or down anytime\n\n"
                    "We want you to stay because you're happy, not because you're locked in!"
                ),
                category="policy",
                keywords=["cancel", "cancellation", "end", "stop", "terminate", "policy"],
                priority=6
            ),
        ]
        
        for faq in faqs:
            self._faqs[faq.id] = faq
    
    def search(self, query: str) -> List[FAQ]:
        """Search FAQs by query"""
        query_lower = query.lower()
        results = []
        
        for faq in self._faqs.values():
            # Check keywords
            if any(keyword in query_lower for keyword in faq.keywords):
                results.append(faq)
        
        # Sort by priority
        results.sort(key=lambda x: x.priority, reverse=True)
        return results
    
    def get_by_id(self, faq_id: str) -> Optional[FAQ]:
        """Get FAQ by ID"""
        return self._faqs.get(faq_id)
    
    def get_all(self, category: Optional[str] = None) -> List[FAQ]:
        """Get all FAQs, optionally filtered by category"""
        faqs = list(self._faqs.values())
        if category:
            faqs = [f for f in faqs if f.category == category]
        return sorted(faqs, key=lambda x: x.priority, reverse=True)


# ============================================================================
# RESPONSE FORMATTERS
# ============================================================================

class ServiceFormatter:
    """Formats service information for display"""
    
    WELCOME_MESSAGE = (
        "Hi 👋 Welcome!\n"
        "I'm Esther's virtual assistant.\n\n"
        "I'll help you find the perfect service for your needs. "
        "Let's get started! 🚀"
    )
    
    BOOKING_LINK = (
        "https://calendar.google.com/calendar/r/eventedit?"
        "text=Discovery+Call&details=Please+book+a+30-minute+discovery+call+with+Esther&sf=true"
    )
    
    @classmethod
    def format_services_menu(cls, catalog: ServiceCatalog) -> str:
        """Format complete services menu"""
        services = catalog.get_all_services()
        
        lines = [
            cls.WELCOME_MESSAGE,
            "\n📋 *Available Services:*\n"
        ]
        
        for service in services:
            lines.append(f"{service.id}. *{service.display_name}*")
            lines.append(f"   {service.description}\n")
        
        lines.append(
            "\n💡 Reply with the *number* or *service name* to learn more.\n"
            "Type *MENU* anytime to return here."
        )
        
        return "\n".join(lines)
    
    @classmethod
    def format_service_detail(
        cls, 
        service: ServicePackage,
        include_pricing: bool = True,
        include_tools: bool = True
    ) -> str:
        """Format detailed service information"""
        lines = [
            f"✨ *{service.display_name}*\n",
            f"{service.detailed_description}\n",
            "\n🎯 *What's Included:*"
        ]
        
        for deliverable in service.key_deliverables[:6]:  # Show max 6
            lines.append(f"• {deliverable}")
        
        if include_pricing:
            min_h, max_h = service.typical_hours_range
            lines.append(f"\n⏰ *Typical Hours:* {min_h}-{max_h} hours/week")
            lines.append(f"💰 *Pricing Tier:* {service.pricing_tier.value.title()}")
        
        if include_tools and service.required_tools:
            lines.append(f"\n🛠️ *Tools Used:* {', '.join(service.required_tools[:3])}")
        
        if service.requires_consultation:
            lines.append("\n⚠️ *Note:* This service requires a consultation call to customize.")
        
        lines.append("\n\nReply *YES* to proceed, or *NO* to see other options.")
        
        return "\n".join(lines)
    
    @classmethod
    def format_recommendations(
        cls,
        services: List[ServicePackage],
        business_type: Optional[str] = None
    ) -> str:
        """Format service recommendations"""
        if not services:
            return "Based on your needs, all our services could be a great fit! 🎯"
        
        lines = ["✨ *Recommended for you:*\n"]
        
        for i, service in enumerate(services[:3], 1):  # Top 3
            lines.append(f"{i}. *{service.display_name}*")
            lines.append(f"   {service.description}\n")
        
        if business_type:
            lines.append(f"\n💡 These services are popular with {business_type} businesses!")
        
        lines.append("\nReply with a number to learn more, or type *ALL* to see all services.")
        
        return "\n".join(lines)


# ============================================================================
# SINGLETON INSTANCES
# ============================================================================

# Global instances
_service_catalog = ServiceCatalog()
_faq_manager = FAQManager()
_formatter = ServiceFormatter()


# ============================================================================
# PUBLIC API
# ============================================================================

def get_service_catalog() -> ServiceCatalog:
    """Get the global service catalog instance"""
    return _service_catalog


def get_faq_manager() -> FAQManager:
    """Get the global FAQ manager instance"""
    return _faq_manager


def format_services_menu() -> str:
    """Format the services menu"""
    return _formatter.format_services_menu(_service_catalog)


def format_service_detail(service_name: str, **kwargs) -> str:
    """Format service details by name"""
    service = _service_catalog.get_service_by_name(service_name)
    if not service:
        return f"Service '{service_name}' not found."
    return _formatter.format_service_detail(service, **kwargs)


def format_service_detail_by_id(service_id: str, **kwargs) -> str:
    """Format service details by ID"""
    service = _service_catalog.get_service(service_id)
    if not service:
        return f"Service ID '{service_id}' not found."
    return _formatter.format_service_detail(service, **kwargs)


def search_services(query: str) -> List[ServicePackage]:
    """Search services"""
    return _service_catalog.search_services(query)


def get_recommendations(business_type: str = None, budget: str = None, hours: int = None) -> str:
    """Get service recommendations"""
    services = _service_catalog.get_recommendations(business_type, budget, hours)
    return _formatter.format_recommendations(services, business_type)


def search_faqs(query: str) -> Optional[str]:
    """Search FAQs and return first match"""
    results = _faq_manager.search(query)
    return results[0].answer if results else None


# Legacy compatibility
SERVICES = {s.id: s.display_name for s in _service_catalog.get_all_services()}
SERVICE_DETAILS = {s.display_name: s.description for s in _service_catalog.get_all_services()}
FAQS = {faq.id: faq.answer for faq in _faq_manager.get_all()}
BOOKING_LINK = ServiceFormatter.BOOKING_LINK
WELCOME_MESSAGE = ServiceFormatter.WELCOME_MESSAGE