"""
Critique engine. Zoara is meant to be an interactive collaborator, not a
vending machine - this is where she pushes back on her own output before
the user has to. Every piece is judged from two angles:
  1. Strategist perspective - does this actually serve the stated goal?
  2. Ideal customer perspective - would the target audience actually stop,
     feel something, and act?
Score out of 10 each; anything below the 7 cutoff must come with concrete,
actionable notes on what would push it over the line.
"""
from . import ai_client
from knowledge_panel import writing_standards_prompt_block

CUTOFF = 7

SYSTEM = """You are Zoara operating in critique mode. You switch between two
distinct, honest perspectives - never a generic "here's some feedback"
tone. You are not here to flatter the user; you are here to make the
content actually work. Be specific: point at exact lines/parts, not vague
impressions.
""" + "\n" + writing_standards_prompt_block()


def critique_content(brand: dict, format_id: str, platform_id: str, content_text: str, goal: str):
    strategy = brand.get("strategy_answers") or {}
    user = f"""
BRAND GOAL FOR THIS CONTENT: {goal}
BRAND STRATEGY CONTEXT: {strategy}
FORMAT: {format_id} | PLATFORM: {platform_id}

CONTENT TO CRITIQUE:
{content_text}

Evaluate this from TWO perspectives and return JSON with this exact shape:
{{
  "strategist_score": <int 1-10>,
  "strategist_feedback": "<2-4 sentences: does this actually serve the stated goal, structurally and strategically>",
  "customer_score": <int 1-10>,
  "customer_feedback": "<2-4 sentences, written AS the ideal target customer reacting honestly to this content - would they stop scrolling, feel something, act>",
  "overall_score": <float, average of the two, one decimal>,
  "improvement_notes": "<if overall_score < {CUTOFF}: specific, concrete changes that would push it above {CUTOFF}. If overall_score >= {CUTOFF}: brief note on what's working and one optional polish idea. Always actionable, never vague praise or vague criticism.>"
}}
"""
    result = ai_client.ask_json(SYSTEM, user, max_tokens=1200, temperature=0.4)
    result["passed_cutoff"] = result.get("overall_score", 0) >= CUTOFF
    return result
