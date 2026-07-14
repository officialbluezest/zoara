"""
Thin wrapper around the real Anthropic API. Requires ANTHROPIC_API_KEY to
be set in the environment (see .env.example). This is a genuine API
integration, not a mock - without a valid key, calls will raise a clear
error that the frontend surfaces to the user.
"""
import os
import json
import anthropic

MODEL = os.environ.get("ZOARA_MODEL", "claude-sonnet-4-5")


def _client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to your .env file "
            "(see .env.example) to enable Zoara's AI generation, research "
            "synthesis, and critique features."
        )
    return anthropic.Anthropic(api_key=api_key)


def ask(system_prompt: str, user_prompt: str, max_tokens: int = 2000, temperature: float = 0.8) -> str:
    client = _client()
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return "".join(block.text for block in resp.content if block.type == "text")


def ask_json(system_prompt: str, user_prompt: str, max_tokens: int = 3000, temperature: float = 0.7):
    """Ask for a strict JSON response and parse it, with a defensive fallback."""
    full_system = system_prompt + "\n\nRespond with ONLY valid JSON. No markdown fences, no preamble, no commentary."
    raw = ask(full_system, user_prompt, max_tokens=max_tokens, temperature=temperature)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # try to salvage the largest {...} or [...] block
        start = min([i for i in [cleaned.find("{"), cleaned.find("[")] if i != -1], default=-1)
        end = max(cleaned.rfind("}"), cleaned.rfind("]"))
        if start != -1 and end != -1:
            try:
                return json.loads(cleaned[start:end + 1])
            except json.JSONDecodeError:
                pass
        raise RuntimeError(f"Zoara's AI returned non-JSON output that couldn't be parsed: {raw[:300]}")
