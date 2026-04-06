"""Minimal external tool agent placeholders.

This file provides simple, safe stub functions so imports succeed and the
project can be run or extended. Replace with real implementations later.
"""

def online_search(query):
    """Perform a dummy online search and return a placeholder result."""
    return f"[dummy search result] No real search implemented for: {query}"


def call_tool(name, *args, **kwargs):
    """Generic tool caller stub."""
    return {
        "tool": name,
        "status": "not_implemented",
        "args": args,
        "kwargs": kwargs,
    }


__all__ = ["online_search", "call_tool"]
