"""Shared LLM factory used by all agents."""

import os


def get_llm(temperature: float = 0):
    """Try to create an LLM instance. Returns None if no API key.

    Args:
        temperature: Sampling temperature (0 = deterministic, higher = creative).
    """
    if os.getenv("OPENAI_API_KEY"):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
    if os.getenv("ANTHROPIC_API_KEY"):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model="claude-sonnet-4-20250514", temperature=temperature)
    return None
