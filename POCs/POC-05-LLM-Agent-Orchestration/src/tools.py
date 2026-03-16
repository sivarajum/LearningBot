"""Tools available to agents: web search and calculator."""

from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """Search the web using DuckDuckGo and return the top 3 results.

    Args:
        query: The search query string.

    Returns:
        Formatted string with top 3 search results.
    """
    try:
        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddgs:
            for i, r in enumerate(ddgs.text(query, max_results=3)):
                results.append(
                    f"[{i + 1}] {r['title']}\n"
                    f"    {r['body']}\n"
                    f"    Source: {r['href']}"
                )
        if results:
            return "\n\n".join(results)
        return f"No results found for: {query}"
    except Exception as e:
        return f"Search failed ({type(e).__name__}): {e}"


@tool
def calculate(expression: str) -> str:
    """Safely evaluate a math expression.

    Args:
        expression: A mathematical expression like '2 + 3 * 4'.

    Returns:
        The result as a string, or an error message.
    """
    allowed_chars = set("0123456789+-*/.() ")
    if not all(c in allowed_chars for c in expression):
        return f"Invalid characters in expression: {expression}"
    try:
        result = eval(expression, {"__builtins__": {}}, {})  # noqa: S307
        return str(result)
    except Exception as e:
        return f"Calculation error: {e}"
