# Rules package — exports all rule classes for easy import

from .base_rule import BaseRule, RuleResult
from .completeness import CompletenessRatioRule, NotNullRule
from .consistency import CrossColumnRule, ReferentialIntegrityRule
from .freshness import DataFreshnessRule
from .uniqueness import UniquenessRatioRule, UniqueRule
from .validity import AllowedValuesRule, RegexRule, TypeRule, ValueRangeRule

__all__ = [
    "BaseRule",
    "RuleResult",
    "NotNullRule",
    "CompletenessRatioRule",
    "RegexRule",
    "ValueRangeRule",
    "AllowedValuesRule",
    "TypeRule",
    "UniqueRule",
    "UniquenessRatioRule",
    "ReferentialIntegrityRule",
    "CrossColumnRule",
    "DataFreshnessRule",
]
