"""
scorer.py — Compute weighted DQ scores and letter grades per dataset.

The DQScorer translates raw rule results into a business-readable scorecard.
This is the "reporting layer" that executives and data owners can act on.

Scoring methodology:
    Each DQ dimension has a weight (sums to 1.0):
        Completeness : 0.30  — highest weight, missing data is most common issue
        Validity     : 0.25  — format/range violations cause downstream failures
        Uniqueness   : 0.20  — duplicates are expensive to clean at scale
        Consistency  : 0.15  — referential/cross-column issues are hard to detect
        Freshness    : 0.10  — recency matters but is dataset-dependent

    Dimension score = average of all rule scores within that dimension (0.0–1.0)
    Overall score   = weighted sum of dimension scores × 100

    Grade:
        A  : >= 90   (production-ready)
        B  : >= 75   (minor issues, monitor closely)
        C  : >= 60   (significant issues, remediation needed)
        D  : >= 45   (serious DQ problems, investigate before using)
        F  : <  45   (data not fit for use)

Real-world context:
    - At FedEx: DQ score < 80 triggered automatic data quarantine
    - At PayPal: DQ score < 90 on payment data blocked batch processing
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List

from .validator import ValidationResult

logger = logging.getLogger(__name__)

DIMENSION_WEIGHTS: Dict[str, float] = {
    "completeness": 0.30,
    "validity":     0.25,
    "uniqueness":   0.20,
    "consistency":  0.15,
    "freshness":    0.10,
}

GRADE_THRESHOLDS = [
    (90, "A", "Excellent — data is production-ready"),
    (75, "B", "Good — minor issues, monitor closely"),
    (60, "C", "Fair — significant issues, remediation needed"),
    (45, "D", "Poor — serious DQ problems, investigate before use"),
    (0,  "F", "Failing — data is not fit for use"),
]


def _compute_grade(score: float) -> tuple:
    """Return (letter_grade, description) for a given 0–100 score."""
    for threshold, grade, description in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade, description
    return "F", "Failing — data is not fit for use"


@dataclass
class DimensionScore:
    """Score and statistics for a single DQ dimension."""
    dimension: str
    weight: float
    rule_count: int
    score_0_to_1: float          # Average of individual rule scores
    score_0_to_100: float        # score_0_to_1 * 100
    weighted_contribution: float # score_0_to_1 * weight (used in overall score)
    passed_rules: int
    failed_rules: int
    grade: str
    grade_description: str
    failing_rules: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "weight": self.weight,
            "rule_count": self.rule_count,
            "score": round(self.score_0_to_100, 2),
            "weighted_contribution": round(self.weighted_contribution * 100, 2),
            "passed_rules": self.passed_rules,
            "failed_rules": self.failed_rules,
            "grade": self.grade,
            "grade_description": self.grade_description,
            "failing_rules": self.failing_rules,
        }


@dataclass
class DQScoreCard:
    """
    Complete DQ scorecard for a dataset.

    Attributes:
        dataset_name        : Name of the validated dataset
        scored_at           : ISO timestamp
        overall_score       : Weighted overall DQ score (0–100)
        overall_grade       : Letter grade A–F
        grade_description   : Human-readable interpretation
        dimension_scores    : Per-dimension DimensionScore objects
        total_rules         : All rules evaluated
        passed_rules        : Rules that passed
        failed_rules        : Rules that failed
        row_count           : Rows in the dataset
        critical_issues     : Error-severity rules that failed
    """
    dataset_name: str
    scored_at: str
    overall_score: float
    overall_grade: str
    grade_description: str
    dimension_scores: Dict[str, DimensionScore]
    total_rules: int
    passed_rules: int
    failed_rules: int
    row_count: int
    critical_issues: List[str]

    def to_dict(self) -> dict:
        return {
            "dataset_name": self.dataset_name,
            "scored_at": self.scored_at,
            "overall_score": round(self.overall_score, 2),
            "overall_grade": self.overall_grade,
            "grade_description": self.grade_description,
            "total_rules": self.total_rules,
            "passed_rules": self.passed_rules,
            "failed_rules": self.failed_rules,
            "row_count": self.row_count,
            "critical_issues": self.critical_issues,
            "dimensions": {k: v.to_dict() for k, v in self.dimension_scores.items()},
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def print_scorecard(self) -> None:
        """Log a formatted scorecard."""
        grade = self.overall_grade
        score = self.overall_score
        lines = [
            f"\n{'='*70}",
            f"  DQ SCORECARD: {self.dataset_name}",
            f"{'='*70}",
            f"  Overall Score : {score:.1f} / 100   Grade: {grade}  ({self.grade_description})",
            f"  Rows          : {self.row_count:,}",
            f"  Rules         : {self.passed_rules} passed / {self.failed_rules} failed / {self.total_rules} total",
            f"{'='*70}",
            f"\n  {'Dimension':<16} {'Weight':>7} {'Score':>8} {'Grade':>6} {'Rules':>10}",
            f"  {'-'*55}",
        ]
        for dim, ds in self.dimension_scores.items():
            bar_filled = int(ds.score_0_to_100 / 5)  # 20 chars = 100 points
            bar = ("\u2588" * bar_filled).ljust(20)
            lines.append(
                f"  {ds.dimension:<16} {ds.weight*100:>6.0f}% "
                f"{ds.score_0_to_100:>7.1f} {ds.grade:>6}  "
                f"{ds.passed_rules}/{ds.rule_count} rules pass  |{bar}|"
            )
        if self.critical_issues:
            lines.append(f"\n  CRITICAL ISSUES ({len(self.critical_issues)}):")
            for issue in self.critical_issues:
                lines.append(f"    [ERROR] {issue}")
        logger.info("\n".join(lines))


class DQScorer:
    """
    Computes a weighted DQ scorecard from a ValidationResult.

    The scorer is stateless — call compute_scores() with any ValidationResult.

    Usage:
        scorer = DQScorer()
        scorecard = scorer.compute_scores(validation_result)
        scorecard.print_scorecard()
        print(scorecard.to_json())
    """

    DIMENSIONS = DIMENSION_WEIGHTS

    def compute_scores(self, validation_result: ValidationResult) -> DQScoreCard:
        """
        Compute per-dimension scores and overall weighted score.

        Args:
            validation_result: Output from DQValidator.validate()

        Returns:
            DQScoreCard with scores, grades, and breakdown per dimension.
        """
        from datetime import datetime, timezone
        scored_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        dimension_scores: Dict[str, DimensionScore] = {}
        overall_weighted_sum = 0.0
        active_weight_sum = 0.0

        for dim, weight in DIMENSION_WEIGHTS.items():
            dim_results = [r for r in validation_result.results if r.dimension == dim]

            if not dim_results:
                # No rules for this dimension — dimension contributes neutrally
                # (Don't penalise if user hasn't configured any freshness rules, etc.)
                ds = DimensionScore(
                    dimension=dim,
                    weight=weight,
                    rule_count=0,
                    score_0_to_1=1.0,
                    score_0_to_100=100.0,
                    weighted_contribution=weight * 1.0,
                    passed_rules=0,
                    failed_rules=0,
                    grade="A",
                    grade_description="No rules configured",
                    failing_rules=[],
                )
                dimension_scores[dim] = ds
                overall_weighted_sum += weight * 1.0
                active_weight_sum += weight
                continue

            # Average the scores of all rules in this dimension
            avg_score = sum(r.score for r in dim_results) / len(dim_results)
            avg_score_100 = avg_score * 100
            passed = sum(1 for r in dim_results if r.passed)
            failed = len(dim_results) - passed
            failing_rule_names = [r.rule_name for r in dim_results if not r.passed]

            grade, grade_desc = _compute_grade(avg_score_100)

            ds = DimensionScore(
                dimension=dim,
                weight=weight,
                rule_count=len(dim_results),
                score_0_to_1=avg_score,
                score_0_to_100=avg_score_100,
                weighted_contribution=weight * avg_score,
                passed_rules=passed,
                failed_rules=failed,
                grade=grade,
                grade_description=grade_desc,
                failing_rules=failing_rule_names,
            )
            dimension_scores[dim] = ds
            overall_weighted_sum += weight * avg_score
            active_weight_sum += weight

        # Overall score = weighted average (normalised to sum of active weights)
        if active_weight_sum > 0:
            overall_score = (overall_weighted_sum / active_weight_sum) * 100
        else:
            overall_score = 100.0

        overall_grade, overall_grade_desc = _compute_grade(overall_score)

        # Critical issues = error-severity rules that failed
        critical_issues = [
            f"{r.rule_name} ({r.column}): {r.details[:100]}"
            for r in validation_result.results
            if r.severity == "error" and not r.passed
        ]

        return DQScoreCard(
            dataset_name=validation_result.dataset_name,
            scored_at=scored_at,
            overall_score=overall_score,
            overall_grade=overall_grade,
            grade_description=overall_grade_desc,
            dimension_scores=dimension_scores,
            total_rules=validation_result.total_rules,
            passed_rules=validation_result.passed_rules,
            failed_rules=validation_result.failed_rules,
            row_count=validation_result.row_count,
            critical_issues=critical_issues,
        )
