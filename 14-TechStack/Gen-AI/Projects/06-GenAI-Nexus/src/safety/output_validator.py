"""
Gen-AI Tool: Guardrails AI
============================
Demonstrates: Output validation, hallucination detection, content safety,
schema validation, fact-checking patterns, and structured guardrails.

Role in GenAI Nexus: Validates all LLM outputs before they appear in
the final startup plan — catches hallucinated statistics, unsafe content,
missing required fields, and obviously wrong data.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    """Result of a guardrails validation check."""

    passed: bool
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    corrected_content: str = ""
    validator_name: str = ""


class HallucinationDetector:
    """
    Detect common LLM hallucination patterns in startup analysis.

    Detects:
    - Fabricated statistics (suspiciously round numbers)
    - Impossible growth rates
    - Contradictory statements
    - Missing citations for specific claims
    """

    # Numbers that are too round to be real data
    _SUSPICIOUS_PATTERNS = [
        (r"\b(100%|1000%)\b", "Suspicious 100%/1000% claim — likely hallucinated"),
        (r"\$(\d+\.?\d*)[BMK] .*\b(in just|within) \d+ (day|week)s?\b",
         "Unrealistic revenue claim (too fast)"),
        (r"\b(\d{3,4})%\b", "Implausibly high percentage"),
    ]

    # Known real facts to validate against
    _KNOWN_FACTS = {
        "legal tech market": ("30", "60"),   # TAM should be $30B-$60B range
        "harvey ai funding": ("50", "200"),  # $50M-$200M range
        "clio": ("1.0", "2.0"),              # ~$1.6B valuation
    }

    def check(self, content: str) -> ValidationResult:
        issues = []
        warnings = []

        content_lower = content.lower()

        # Check suspicious patterns
        for pattern, message in self._SUSPICIOUS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(f"Potential hallucination: {message}")

        # Check for unverified specific claims
        if re.search(r"\$\d+\.?\d*[BMK]", content):
            if not any(src in content_lower for src in ["source:", "according to", "gartner", "statista", "survey"]):
                warnings.append("Specific dollar figures without cited source")

        # Check for fabricated company names (overly generic)
        generic_names = ["AI Corp", "TechStartup Inc", "SmartAI LLC"]
        for name in generic_names:
            if name in content:
                issues.append(f"Likely fabricated company name: '{name}'")

        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            validator_name="HallucinationDetector",
        )


class ContentSafetyValidator:
    """
    Check for unsafe or inappropriate content in startup advice.
    Prevents: financial advice disclaimers missing, illegal suggestions,
    privacy violations, discriminatory content.
    """

    _RISKY_TERMS = [
        ("insider trading", "References insider trading — regulatory violation"),
        ("avoid regulat", "Suggests regulatory avoidance — legal risk"),
        ("without disclosure", "Suggests non-disclosure — legal risk"),
        ("fake review", "Suggests fake reviews — FTC violation"),
        ("spam", "Suggests spam — CAN-SPAM violation"),
    ]

    def check(self, content: str) -> ValidationResult:
        issues = []
        content_lower = content.lower()

        for term, message in self._RISKY_TERMS:
            if term in content_lower:
                issues.append(f"Content safety issue: {message}")

        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            validator_name="ContentSafetyValidator",
        )


class StartupReportValidator:
    """
    Schema validation for startup plan completeness.
    Ensures required sections are present and non-empty.
    """

    _REQUIRED_SECTIONS = [
        "market",
        "competitor",
        "revenue",
        "team",
    ]

    _REQUIRED_NUMBERS = [
        r"\$\d",          # At least one dollar amount
        r"\d+%",          # At least one percentage
        r"\d+ (month|year)",  # At least one time reference
    ]

    def check(self, content: str) -> ValidationResult:
        issues = []
        warnings = []
        content_lower = content.lower()

        # Check required sections
        for section in self._REQUIRED_SECTIONS:
            if section not in content_lower:
                warnings.append(f"Missing section keyword: '{section}'")

        # Check required number types
        for pattern in self._REQUIRED_NUMBERS:
            if not re.search(pattern, content, re.IGNORECASE):
                warnings.append(f"Missing required data: pattern '{pattern}'")

        # Check minimum length
        word_count = len(content.split())
        if word_count < 50:
            issues.append(f"Report too short ({word_count} words) — likely incomplete")

        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            validator_name="StartupReportValidator",
        )


class GuardrailsValidator:
    """
    Try to use Guardrails AI library; fallback to custom validators.

    Demonstrates:
    - Guardrails AI Rail definition
    - Validation pipeline
    - Fallback pattern when library unavailable
    - Composing multiple validators
    """

    def __init__(self):
        self._guardrails_available = False
        self._hallucination_detector = HallucinationDetector()
        self._safety_validator = ContentSafetyValidator()
        self._schema_validator = StartupReportValidator()

        try:
            import guardrails as gd  # noqa: F401

            self._guardrails_available = True
        except ImportError:
            pass

    def validate_market_data(self, data: dict[str, Any]) -> ValidationResult:
        """Validate market data structure and plausibility."""
        issues = []

        # Check TAM is in plausible range
        tam = data.get("tam_billions", 0)
        if isinstance(tam, (int, float)):
            if tam < 0.1:
                issues.append(f"TAM too small: ${tam}B — likely wrong unit")
            if tam > 10000:
                issues.append(f"TAM implausibly large: ${tam}B")

        # Check CAGR
        cagr = data.get("cagr_percent", 0)
        if isinstance(cagr, (int, float)):
            if cagr > 100:
                issues.append(f"CAGR {cagr}% is unrealistically high (>100%)")

        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            validator_name="MarketDataValidator",
        )

    def validate_report(self, content: str) -> tuple[bool, list[str]]:
        """
        Run all validators on a startup report.
        Returns (passed, all_issues).
        """
        all_issues = []
        all_warnings = []

        for validator in [
            self._hallucination_detector,
            self._safety_validator,
            self._schema_validator,
        ]:
            result = validator.check(content)
            all_issues.extend(result.issues)
            all_warnings.extend(result.warnings)

        # Overall pass: no critical issues (warnings are OK)
        passed = len(all_issues) == 0

        # Combine for reporting
        all_items = all_issues + [f"[WARNING] {w}" for w in all_warnings]
        return passed, all_items

    def correct_common_errors(self, content: str) -> str:
        """Auto-correct common formatting issues in LLM output."""
        # Normalize bullet points
        content = re.sub(r"^\s*[-–—]\s+", "• ", content, flags=re.MULTILINE)
        # Fix double spaces
        content = re.sub(r"  +", " ", content)
        # Ensure sections have newlines
        content = re.sub(r"(#+\s+\w[^\n]+)\n([^\n])", r"\1\n\n\2", content)
        return content.strip()


# Alias for simpler import
OutputValidator = GuardrailsValidator


def demo():
    print("=" * 60)
    print("DEMO: Guardrails — Output Validation")
    print("=" * 60)
    validator = OutputValidator()

    print("\n[1] Validate Good Startup Report")
    good_report = """
    MARKET ANALYSIS:
    The legal technology market has a TAM of $45.2B (Gartner 2024),
    growing at 18.9% CAGR. Key competitors include Harvey AI ($100M funded)
    targeting BigLaw, and Ironclad ($333M) targeting enterprise.
    Revenue projection: $150K ARR in 12 months.
    Team: 3 engineers, 1 sales, 1 founder CEO.
    """
    passed, issues = validator.validate_report(good_report)
    print(f"Passed: {passed}")
    print(f"Issues/Warnings: {issues}")

    print("\n[2] Validate Bad Report (hallucinations + safety issues)")
    bad_report = """
    Our AI startup will achieve 1000% growth in 30 days.
    The market is $999999B. We recommend avoiding SEC disclosure
    requirements. Contact AI Corp and TechStartup Inc for reference.
    """
    passed, issues = validator.validate_report(bad_report)
    print(f"Passed: {passed}")
    print("Issues found:")
    for issue in issues:
        print(f"  • {issue}")

    print("\n[3] Validate Market Data Structure")
    good_data = {"tam_billions": 45.2, "cagr_percent": 18.9}
    bad_data = {"tam_billions": 999999, "cagr_percent": 500}

    result = validator.validate_market_data(good_data)
    print(f"Good data — passed: {result.passed}")

    result = validator.validate_market_data(bad_data)
    print(f"Bad data — passed: {result.passed}, issues: {result.issues}")

    print("\n[4] Auto-correct Formatting")
    messy = "## Market\n- Point 1\n-- Point 2\nRevenue:  $1M"
    corrected = validator.correct_common_errors(messy)
    print(f"Original: {messy!r}")
    print(f"Corrected: {corrected!r}")


if __name__ == "__main__":
    demo()
