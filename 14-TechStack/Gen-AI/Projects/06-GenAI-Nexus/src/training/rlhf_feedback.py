"""
Gen-AI Tool: RLHF (Reinforcement Learning from Human Feedback)
================================================================
Demonstrates: Reward model training, preference data collection,
PPO training loop concept, DPO (Direct Preference Optimization),
and human feedback collection pipeline.

Role in GenAI Nexus: Learn from user ratings of startup advice quality —
preferred advice gets reinforced, poor advice gets penalized.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class PreferenceExample:
    """A human preference: chosen (better) vs rejected (worse) response."""

    prompt: str
    chosen: str          # Better response (human preferred)
    rejected: str        # Worse response (human rejected)
    timestamp: str = ""
    feedback_note: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class RewardScore:
    prompt: str
    response: str
    score: float    # Higher = better quality advice
    reasons: list[str] = field(default_factory=list)


@dataclass
class FeedbackSession:
    """User rating session for collecting preference data."""

    session_id: str
    startup_idea: str
    ratings: list[dict] = field(default_factory=list)
    preferences: list[PreferenceExample] = field(default_factory=list)


# Sample preference data showing good vs bad startup advice
SAMPLE_PREFERENCES = [
    PreferenceExample(
        prompt="How do I find my first 10 customers for a legal tech startup?",
        chosen=(
            "Target specific: solo practitioners using Clio who review NDAs regularly. "
            "Join Clio Community forum, answer questions about contract review for 2 weeks before pitching. "
            "Then DM your top 10 engagers. Offer 6 months free for feedback. "
            "Goal: 10 design partners, not 10 random customers."
        ),
        rejected=(
            "You should market your product on social media and attend networking events. "
            "LinkedIn is great for B2B. Make sure your website has good SEO. "
            "Cold outreach can work if you personalize it."
        ),
        feedback_note="Chosen is specific, actionable, leverages insider knowledge. Rejected is generic MBA advice.",
    ),
    PreferenceExample(
        prompt="What should my burn rate be in year 1?",
        chosen=(
            "Target $30-50K/month for a technical founding team of 2. "
            "Breakdown: 2 founders (0 salary or market - 50%), $5K cloud infra (pre-scale), "
            "$3K tools (GitHub, Figma, Notion, Hubspot), $2K legal (incorporation, TOS). "
            "Key: stay lean until you have $10K MRR — proof of demand before hiring."
        ),
        rejected=(
            "Burn rate depends on many factors like team size, location, and growth goals. "
            "You should create a detailed financial model to understand your specific needs. "
            "Generally, startups should aim to have 12-18 months of runway."
        ),
        feedback_note="Chosen gives real numbers. Rejected is vague and adds no value.",
    ),
]


class HumanFeedbackCollector:
    """
    Collects and stores human preference data for RLHF.

    In production: integrates with a web UI where users rate advice.
    Here: demonstrates the data structure and collection pipeline.
    """

    def __init__(self, storage_path: str = "./data/rlhf_feedback"):
        self._storage = Path(storage_path)
        self._storage.mkdir(parents=True, exist_ok=True)
        self._preferences: list[PreferenceExample] = list(SAMPLE_PREFERENCES)

    def collect_rating(
        self,
        prompt: str,
        response_a: str,
        response_b: str,
        preferred: str,  # "A" or "B"
        feedback: str = "",
    ) -> PreferenceExample:
        """Record a human preference between two responses."""
        chosen = response_a if preferred == "A" else response_b
        rejected = response_b if preferred == "A" else response_a

        pref = PreferenceExample(
            prompt=prompt,
            chosen=chosen,
            rejected=rejected,
            feedback_note=feedback,
        )
        self._preferences.append(pref)
        return pref

    def simulate_feedback_session(self, startup_idea: str, responses: list[str]) -> FeedbackSession:
        """
        Simulate a user feedback session.
        In production: real users rate these via UI.
        """
        session = FeedbackSession(
            session_id=f"session_{random.randint(1000, 9999)}",
            startup_idea=startup_idea,
        )

        ratings = [
            {"response": r[:100], "rating": random.choice([3, 4, 4, 5]), "helpful": True}
            for r in responses
        ]
        session.ratings = ratings

        # Create preference pairs
        for i in range(len(responses) - 1):
            pref = PreferenceExample(
                prompt=f"Advise on: {startup_idea}",
                chosen=responses[i] if ratings[i]["rating"] >= ratings[i + 1]["rating"] else responses[i + 1],
                rejected=responses[i + 1] if ratings[i]["rating"] >= ratings[i + 1]["rating"] else responses[i],
            )
            session.preferences.append(pref)
            self._preferences.append(pref)

        return session

    def save(self) -> Path:
        """Persist preference data to disk."""
        filepath = self._storage / "preferences.jsonl"
        with open(filepath, "w") as f:
            for pref in self._preferences:
                f.write(json.dumps({
                    "prompt": pref.prompt,
                    "chosen": pref.chosen,
                    "rejected": pref.rejected,
                    "timestamp": pref.timestamp,
                    "feedback_note": pref.feedback_note,
                }) + "\n")
        return filepath

    def get_dataset(self) -> list[PreferenceExample]:
        return self._preferences


class RewardModel:
    """
    Reward model that scores response quality.

    Full RLHF: Train this on preference data, then use PPO to update the LLM.
    DPO alternative: skip reward model, use preference data directly.

    Demonstrates:
    - Rule-based reward scoring (heuristic, no model needed)
    - DPO data format preparation
    - Reward signal computation
    """

    # Markers of high-quality startup advice
    _POSITIVE_SIGNALS = [
        "specific", "exact", "$", "%", "month", "week",
        "because", "example", "data", "benchmark", "metric",
    ]
    _NEGATIVE_SIGNALS = [
        "it depends", "various factors", "consider", "generally",
        "typically", "maybe", "might", "could potentially",
    ]

    def score(self, prompt: str, response: str) -> RewardScore:
        """Score response quality using heuristic reward model."""
        response_lower = response.lower()
        reasons = []
        score = 0.5  # baseline

        # Positive signals
        for sig in self._POSITIVE_SIGNALS:
            if sig in response_lower:
                score += 0.05
                reasons.append(f"+0.05: contains '{sig}'")

        # Negative signals
        for sig in self._NEGATIVE_SIGNALS:
            if sig in response_lower:
                score -= 0.05
                reasons.append(f"-0.05: vague phrase '{sig}'")

        # Length bonus (too short = bad advice)
        word_count = len(response.split())
        if word_count > 100:
            score += 0.1
            reasons.append("+0.1: detailed response (>100 words)")
        elif word_count < 30:
            score -= 0.2
            reasons.append("-0.2: too short (<30 words)")

        # Contains numbers (specificity bonus)
        import re
        if re.search(r"\d+", response):
            score += 0.1
            reasons.append("+0.1: contains specific numbers")

        score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
        return RewardScore(
            prompt=prompt,
            response=response,
            score=round(score, 3),
            reasons=reasons[:5],  # Top 5 reasons
        )

    def prepare_dpo_dataset(
        self, preferences: list[PreferenceExample]
    ) -> list[dict]:
        """
        Prepare preference data for DPO training.
        DPO trains directly on (chosen, rejected) pairs — no reward model needed.
        """
        return [
            {
                "prompt": pref.prompt,
                "chosen": pref.chosen,
                "rejected": pref.rejected,
            }
            for pref in preferences
        ]


class RLHFPipeline:
    """
    Complete RLHF pipeline demonstration.
    Combines feedback collection → reward scoring → DPO dataset preparation.
    """

    def __init__(self):
        self._collector = HumanFeedbackCollector()
        self._reward_model = RewardModel()

    def run(self, startup_idea: str, candidate_responses: list[str]) -> dict:
        """
        Full RLHF pipeline for one startup advisory session.
        """
        # 1. Collect (simulated) human feedback
        session = self._collector.simulate_feedback_session(startup_idea, candidate_responses)

        # 2. Score each response with reward model
        reward_scores = [
            self._reward_model.score(startup_idea, r)
            for r in candidate_responses
        ]

        # 3. Rank responses by reward
        ranked = sorted(
            zip(candidate_responses, reward_scores),
            key=lambda x: x[1].score,
            reverse=True,
        )

        # 4. Prepare DPO dataset
        prefs = self._collector.get_dataset()
        dpo_data = self._reward_model.prepare_dpo_dataset(prefs[-len(session.preferences):])

        return {
            "session_id": session.session_id,
            "ratings": session.ratings,
            "reward_scores": [
                {"response_preview": r[:80], "score": s.score}
                for r, s in ranked
            ],
            "best_response": ranked[0][0] if ranked else "",
            "dpo_pairs": len(dpo_data),
            "total_preferences": len(prefs),
        }


def demo():
    print("=" * 60)
    print("DEMO: RLHF — Human Feedback Pipeline")
    print("=" * 60)

    pipeline = RLHFPipeline()
    reward_model = RewardModel()
    collector = HumanFeedbackCollector()

    print("\n[1] Score Response Quality (Reward Model)")
    good = (
        "For mid-market law firms, target $499/month flat-rate. "
        "Benchmark: Clio charges $49/user, we charge per firm. "
        "A 5-person firm pays $100/attorney/month — justified by saving 2 hours/week at $350/hr."
    )
    bad = "It depends on various factors. You should consider your target market and pricing strategy."

    score_good = reward_model.score("How to price legal tech SaaS?", good)
    score_bad = reward_model.score("How to price legal tech SaaS?", bad)
    print(f"Good response score: {score_good.score}")
    print(f"Bad response score: {score_bad.score}")
    print(f"Reasons for good: {score_good.reasons[:3]}")

    print("\n[2] Preference Data Collection")
    pref = collector.collect_rating(
        prompt="How do I acquire first customers?",
        response_a=good,
        response_b=bad,
        preferred="A",
        feedback="Response A is specific with real numbers",
    )
    print(f"Preference recorded: chosen='{pref.chosen[:60]}...'")

    print("\n[3] RLHF Pipeline — Full Session")
    responses = [good, bad, "Target lawyers who review 10+ contracts per week — start there."]
    result = pipeline.run("AI legal document analyzer", responses)
    print(f"Session: {result['session_id']}")
    print(f"Best response: {result['best_response'][:80]}...")
    print(f"Reward scores: {[r['score'] for r in result['reward_scores']]}")
    print(f"DPO training pairs ready: {result['dpo_pairs']}")

    print("\n[4] DPO Dataset Preview")
    dpo = reward_model.prepare_dpo_dataset(SAMPLE_PREFERENCES[:1])
    print(f"Prompt: {dpo[0]['prompt'][:80]}")
    print(f"Chosen: {dpo[0]['chosen'][:80]}...")
    print(f"Rejected: {dpo[0]['rejected'][:80]}...")


if __name__ == "__main__":
    demo()
