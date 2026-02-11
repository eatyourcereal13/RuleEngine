from enum import Enum


class CampaignStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"


class TriggeredRule(str, Enum):
    DISABLED_MANAGEMENT = "disabled_management"
    SCHEDULE = "schedule"
    LOW_STOCK = "low_stock"
    BUDGET_EXCEEDED = "budget_exceeded"
    NO_RESTRICTIONS = "no_restrictions"