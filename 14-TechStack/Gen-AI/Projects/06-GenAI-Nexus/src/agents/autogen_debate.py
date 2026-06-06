"""
Gen-AI Tool: Microsoft AutoGen
================================
Demonstrates: Multi-agent conversation, optimist vs skeptic debate,
AssistantAgent + UserProxyAgent, group chat, conversation termination.

Role in GenAI Nexus: Devil's advocate debate to stress-test the startup
plan. Optimist agent promotes, Skeptic agent tears apart, Mediator synthesizes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

DEMO_DEBATE = """
STARTUP PLAN STRESS TEST — AutoGen Multi-Agent Debate
======================================================

TOPIC: "AI legal document analyzer for mid-market law firms"

OPTIMIST: This is a massive opportunity. $45.2B market, Harvey proves
the demand at BigLaw, Clio proves PLG works in legal tech. We're filling
the exact gap between them. The numbers make sense: 80% of law firms are
small/mid, spending $18K/yr on software. AI at $299/mo = $3.6K/yr.
That's LESS than current spend with 10x the value. This sells itself.

SKEPTIC: Hold on. Attorney-client privilege is a landmine. If our AI
"sees" confidential communications, we have an ethics problem with 50
different state bars. Harvey got away with this because they target
BigLaw firms with in-house counsel. Small firms are MORE ethically exposed,
not less. Also, $299/mo is actually HIGH for solo practitioners who
already complain about Clio at $49/user/month. This needs deep legal
domain expertise we probably don't have.

OPTIMIST: Fair point on ethics. But Microsoft, Google, Thomson Reuters all
have opinions from ethics committees. We get ABA ethics opinion pre-launch.
On pricing: $299 is for the FIRM, not per user. A 5-person firm paying
$59/attorney/month for 90% time savings on contracts? That's a no-brainer.
Break-even is ONE contract reviewed per month.

SKEPTIC: What about data security? A law firm's documents are their most
sensitive assets. We're asking them to upload client contracts to a SaaS
platform. One breach = malpractice exposure for them. We need to be
self-hosted or have a flawless security story.

MEDIATOR SYNTHESIS:
Both sides raise valid points. Critical pre-conditions before launch:
1. ABA ethics opinion (1-2 months, ~$15K legal cost)
2. SOC2 Type I certification (3 months, AWS makes this feasible)
3. On-prem option for security-conscious firms (Month 9+)
4. Pricing: $199 solo / $499 small team / $999 firm — not one-size

VERDICT: The opportunity is real. The execution risks are manageable but
MUST be addressed before launch. Don't skip the ethics + security work.
"""


@dataclass
class DebateConfig:
    max_turns: int = 6
    openai_key: str = ""
    verbose: bool = False


@dataclass
class DebateTurn:
    agent: str
    message: str
    turn_number: int


@dataclass
class DebateResult:
    """Full debate transcript + synthesis."""

    topic: str
    turns: list[DebateTurn] = field(default_factory=list)
    synthesis: str = ""
    verdict: str = ""
    risks_identified: list[str] = field(default_factory=list)


class StartupDebate:
    """
    AutoGen multi-agent debate for startup stress testing.

    Demonstrates:
    - AssistantAgent with distinct personas
    - Multi-agent group chat
    - Conversation flow control
    - Termination conditions
    - Synthesis from structured debate
    """

    OPTIMIST_SYSTEM = """You are an OPTIMIST startup analyst.
Your job: find the strongest reasons this startup WILL succeed.
Focus on: market timing, competitor weaknesses, founder advantages.
Be specific with numbers. Avoid cheerleading without evidence.
Speak in 2-3 sentences max per turn."""

    SKEPTIC_SYSTEM = """You are a SKEPTIC venture investor.
Your job: find the FATAL flaws in this startup plan.
Focus on: regulatory risk, competitive threats, assumptions that must hold true.
If you can't kill the idea, say so honestly.
Be specific. No generic "competition is fierce" — name companies and exact threats."""

    MEDIATOR_SYSTEM = """You are a MEDIATOR startup advisor.
After hearing both sides, synthesize:
1. Top 3 risks that MUST be addressed (with specific mitigations)
2. Top 3 genuine opportunities
3. Clear go/no-go recommendation with conditions

Speak only when called. Be decisive."""

    def __init__(self, config: DebateConfig | None = None, use_local: bool = False):
        self._config = config or DebateConfig()
        self._use_local = use_local
        self._demo = not self._config.openai_key and not use_local

    def run(self, startup_idea: str, plan_summary: str = "") -> str:
        """
        Run a multi-turn debate about the startup plan.

        Args:
            startup_idea: The startup to debate
            plan_summary: Executive summary from CEO agent

        Returns:
            Full debate transcript with synthesis
        """
        if self._demo:
            return DEMO_DEBATE

        try:
            import autogen

            if self._use_local:
                from config.settings import settings

                llm_config = {
                    "config_list": [
                        {
                            "model": settings.ollama_model,
                            "base_url": f"{settings.ollama_base_url}/v1",
                            "api_key": "ollama",
                        }
                    ]
                }
            else:
                llm_config = {
                    "config_list": [
                        {"model": "gpt-4o-mini", "api_key": self._config.openai_key}
                    ]
                }

            optimist = autogen.AssistantAgent(
                name="Optimist",
                system_message=self.OPTIMIST_SYSTEM,
                llm_config=llm_config,
            )

            skeptic = autogen.AssistantAgent(
                name="Skeptic",
                system_message=self.SKEPTIC_SYSTEM,
                llm_config=llm_config,
            )

            mediator = autogen.AssistantAgent(
                name="Mediator",
                system_message=self.MEDIATOR_SYSTEM,
                llm_config=llm_config,
            )

            # UserProxy manages the conversation
            user_proxy = autogen.UserProxyAgent(
                name="Moderator",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=0,
                code_execution_config=False,
            )

            group_chat = autogen.GroupChat(
                agents=[optimist, skeptic, mediator, user_proxy],
                messages=[],
                max_round=self._config.max_turns,
                speaker_selection_method="round_robin",
            )

            manager = autogen.GroupChatManager(
                groupchat=group_chat, llm_config=llm_config
            )

            topic = (
                f"Debate this startup plan:\n\n"
                f"Startup: {startup_idea}\n"
                f"Plan: {plan_summary[:500] if plan_summary else 'See startup idea'}\n\n"
                f"Optimist: argue why this will succeed.\n"
                f"Skeptic: argue why this will fail.\n"
                f"Mediator: synthesize after 2 rounds each."
            )

            user_proxy.initiate_chat(manager, message=topic)

            # Extract transcript
            transcript = []
            for msg in group_chat.messages:
                transcript.append(f"{msg['name'].upper()}: {msg['content']}")

            return "\n\n".join(transcript)

        except (ImportError, Exception) as e:
            return DEMO_DEBATE + f"\n[Note: AutoGen not available — {e}]"

    def extract_risks(self, debate_output: str) -> list[str]:
        """Extract key risks identified in the debate."""
        risks = []
        lines = debate_output.split("\n")
        in_risks_section = False

        for line in lines:
            if "risk" in line.lower() and ":" in line:
                in_risks_section = True
            if in_risks_section and line.strip().startswith(("1.", "2.", "3.", "•", "-")):
                risk = line.strip().lstrip("123.-•").strip()
                if risk:
                    risks.append(risk)

        # Fallback: extract sentences containing "risk" keyword
        if not risks:
            for line in lines:
                if "risk" in line.lower() and len(line) > 20:
                    risks.append(line.strip()[:150])

        return risks[:5]


def demo():
    print("=" * 60)
    print("DEMO: AutoGen — Multi-Agent Startup Debate")
    print("=" * 60)
    debate = StartupDebate()

    print("\n[1] Run Optimist vs Skeptic Debate")
    result = debate.run(
        "AI legal document analyzer",
        "Build AI tools for mid-market law firms at $299-999/month",
    )
    print(result)

    print("\n[2] Extract Key Risks from Debate")
    risks = debate.extract_risks(result)
    print("\nKey Risks Identified:")
    for i, risk in enumerate(risks, 1):
        print(f"  {i}. {risk}")


if __name__ == "__main__":
    demo()
