from typing import List
from app.rules.base import Rule
from app.rules.disabled_management import DisabledManagementRule
from app.rules.schedule_rule import ScheduleRule
from app.rules.low_stock import LowStockRule
from app.rules.budget_exceeded import BudgetExceededRule


def get_all_rules() -> List[Rule]:
    """Возвращает все правила, отсортированные по приоритету"""
    rules = [
        DisabledManagementRule(),
        ScheduleRule(),
        LowStockRule(),
        BudgetExceededRule(),
    ]
    return sorted(rules, key=lambda r: r.priority)