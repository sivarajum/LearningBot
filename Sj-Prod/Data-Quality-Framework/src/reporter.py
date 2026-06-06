"""
reporter.py — Generate structured DQ reports in JSON and text formats.

The DQReporter combines profiling, validation, and scoring results into
a single comprehensive report object suitable for:
    - Storing in a data catalog
    - Sending to a monitoring dashboard
    - Emailing to data owners
    - Writing to S3 / ADLS / GCS as a DQ report artifact

Report structure:
    {
        "metadata": { generated_at, framework_version },
        "profile":  DatasetProfile.to_dict(),
        "validation": ValidationResult.to_dict(),
        "scorecard": DQScoreCard.to_dict(),
        "alerts": [ ...critical issues formatted as alerts ],
        "recommendations": [ ...auto-generated fix suggestions ]
    }
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

from .profiler import DatasetProfile
from .scorer import DQScoreCard
from .validator import ValidationResult

logger = logging.getLogger(__name__)

FRAMEWORK_VERSION = "1.0.0"


@dataclass
class DQAlert:
    """
    A single DQ alert — a human-readable notification of a data quality issue.

    Severity: error | warning | info
    """
    alert_id: str
    severity: str
    dimension: str
    rule_name: str
    column: str
    message: str
    failing_count: int
    total_count: int

    def to_dict(self) -> dict:
        return {
            "alert_id": self.alert_id,
            "severity": self.severity,
            "dimension": self.dimension,
            "rule_name": self.rule_name,
            "column": self.column,
            "message": self.message,
            "failing_count": self.failing_count,
            "total_count": self.total_count,
        }


def _generate_recommendations(scorecard: DQScoreCard, validation_result: ValidationResult) -> List[str]:
    """
    Auto-generate remediation recommendations based on failing rules.
    """
    recommendations = []

    for result in validation_result.results:
        if result.passed:
            continue

        dim = result.dimension
        col = result.column
        rule = result.rule_name
        pct = result.pass_rate * 100

        if dim == "completeness":
            if pct < 50:
                recommendations.append(
                    f"CRITICAL: Column '{col}' is {100-pct:.1f}% null. "
                    f"Investigate upstream pipeline — check ETL job for silent failures."
                )
            else:
                recommendations.append(
                    f"Column '{col}' has {100-pct:.1f}% null values. "
                    f"Consider: (1) add NOT NULL constraint at source, "
                    f"(2) impute with domain-appropriate default, "
                    f"(3) review if field is truly required."
                )
        elif dim == "validity":
            if "regex" in rule.lower() or "format" in rule.lower():
                recommendations.append(
                    f"Column '{col}' has {result.failing_count} format violations. "
                    f"Add input validation at ingestion layer. "
                    f"Sample bad values: {result.failing_values[:3]}"
                )
            elif "range" in rule.lower():
                recommendations.append(
                    f"Column '{col}' has {result.failing_count} out-of-range values. "
                    f"Implement range checks in source system or ETL transformation."
                )
            elif "allowed" in rule.lower():
                recommendations.append(
                    f"Column '{col}' has {result.failing_count} invalid category values. "
                    f"Standardise at ingestion: map variants to canonical values."
                )
        elif dim == "uniqueness":
            recommendations.append(
                f"Column '{col}' has {result.failing_count} duplicate values. "
                f"Add DISTINCT or dedup step in ETL. "
                f"Investigate upstream system for duplicate record generation."
            )
        elif dim == "consistency":
            if "referential" in rule.lower() or "integrity" in rule.lower():
                recommendations.append(
                    f"Column '{col}' has {result.failing_count} orphaned references. "
                    f"Ensure parent table is loaded before child table. "
                    f"Add FK constraint or referential check in orchestration."
                )
            else:
                recommendations.append(
                    f"Cross-column rule '{rule}' failed on {result.failing_count} rows. "
                    f"Review business logic in source system and transformation code."
                )
        elif dim == "freshness":
            recommendations.append(
                f"Column '{col}' freshness check failed. "
                f"Investigate pipeline schedule and upstream data delivery SLAs."
            )

    if not recommendations:
        recommendations.append("No issues detected. Data quality is within acceptable thresholds.")

    return recommendations


class DQReporter:
    """
    Assembles and persists comprehensive DQ reports.

    Usage:
        reporter = DQReporter(output_dir="./reports")
        report = reporter.generate_report(
            profile=profile,
            validation_result=validation_result,
            scorecard=scorecard,
        )
        reporter.save_report(report, "customers")
        print(reporter.format_text_summary(report))
    """

    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_report(
        self,
        profile: DatasetProfile,
        validation_result: ValidationResult,
        scorecard: DQScoreCard,
    ) -> Dict[str, Any]:
        """
        Build a complete DQ report as a nested dictionary.

        Returns:
            Full report dict with metadata, profile, validation, scorecard, alerts, recommendations.
        """
        generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        alerts = self._generate_alerts(validation_result)
        recommendations = _generate_recommendations(scorecard, validation_result)

        report = {
            "metadata": {
                "generated_at": generated_at,
                "framework_version": FRAMEWORK_VERSION,
                "dataset_name": validation_result.dataset_name,
                "framework": "Enterprise Data Quality Framework — POC-09",
            },
            "scorecard": scorecard.to_dict(),
            "profile": profile.to_dict(),
            "validation": validation_result.to_dict(),
            "alerts": [a.to_dict() for a in alerts],
            "recommendations": recommendations,
        }

        return report

    def save_report(self, report: Dict[str, Any], dataset_name: str) -> str:
        """
        Save the report as a JSON file in the output directory.

        Returns:
            Path to the saved file.
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"dq_report_{dataset_name}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2, default=str)

        return filepath

    def format_text_summary(self, report: Dict[str, Any]) -> str:
        """
        Generate a concise text summary of the report for logging/email.
        """
        sc = report["scorecard"]
        alerts = report["alerts"]
        recs = report["recommendations"]

        error_alerts = [a for a in alerts if a["severity"] == "error"]
        warning_alerts = [a for a in alerts if a["severity"] == "warning"]

        lines = [
            "=" * 70,
            f"  DATA QUALITY REPORT: {sc['dataset_name']}",
            f"  Generated: {report['metadata']['generated_at']}",
            "=" * 70,
            f"  Overall Score  : {sc['overall_score']:.1f}/100  Grade: {sc['overall_grade']}",
            f"  ({sc['grade_description']})",
            "",
            f"  Rules: {sc['passed_rules']} passed / {sc['failed_rules']} failed / {sc['total_rules']} total",
            f"  Alerts: {len(error_alerts)} errors, {len(warning_alerts)} warnings",
            "",
            "  DQ Dimensions:",
        ]

        for dim, dim_data in sc.get("dimensions", {}).items():
            score = dim_data.get("score", 0)
            grade = dim_data.get("grade", "?")
            passed = dim_data.get("passed_rules", 0)
            total = dim_data.get("rule_count", 0)
            lines.append(f"    {dim:<16}: {score:>6.1f}/100  [{grade}]  {passed}/{total} rules pass")

        if error_alerts:
            lines.append("")
            lines.append(f"  CRITICAL ALERTS ({len(error_alerts)}):")
            for a in error_alerts[:5]:
                lines.append(f"    [ERROR] {a['rule_name']} on '{a['column']}': {a['message']}")

        if recs:
            lines.append("")
            lines.append(f"  RECOMMENDATIONS ({min(3, len(recs))} of {len(recs)}):")
            for rec in recs[:3]:
                lines.append(f"    - {rec[:120]}")

        lines.append("=" * 70)
        return "\n".join(lines)

    @staticmethod
    def _generate_alerts(validation_result: ValidationResult) -> List[DQAlert]:
        """Convert failing RuleResults into DQAlert objects."""
        alerts = []
        for i, result in enumerate(validation_result.results):
            if result.passed:
                continue

            alert = DQAlert(
                alert_id=f"ALERT-{i+1:04d}",
                severity=result.severity,
                dimension=result.dimension,
                rule_name=result.rule_name,
                column=result.column,
                message=(
                    f"{result.failing_count} of {result.total_count} rows fail rule '{result.rule_name}' "
                    f"(pass rate: {result.pass_rate * 100:.1f}%)"
                ),
                failing_count=result.failing_count,
                total_count=result.total_count,
            )
            alerts.append(alert)

        return alerts
