"""
Content generation. This is where Format Module + Platform Module +
Brand Brain + approved research idea + inspiration patterns all get
merged into one generation prompt. Nothing generic ever gets written -
every call is conditioned by the specific combination selected.
"""
from . import ai_client
from format_modules import get_format
from platform_modules import get_platform
from knowledge_panel import writing_standards_prompt_block

BASE_SYSTEM = """You are Zoara, an expert content strategist and copywriter.
You write results-oriented content, never filler or fluff. You always use
correct grammar and spelling regardless of how the user's own input is
written - you never mirror a user's typos or grammatical errors into
brand-facing content. You follow the exact structural skeleton given to
you for the active format, and you follow every platform-specific note
given to you. You write in the brand's actual voice, never a generic
'AI marketing' tone.
"""


def build_generation_prompt(brand: dict, format_id: str, platform_id: str,
                             idea: dict, build_spec: dict, inspo_notes: list,
                             creative_angle: str = ""):
    fmt = get_format(format_id)
    plat = get_platform(platform_id)
    if not fmt or not plat:
        raise ValueError("Unknown format or platform")

    skeleton = "\n".join(f"- {s['part']}: {s['guidance']}" for s in fmt["structure_skeleton"])
    platform_notes = "\n".join(f"- {n}" for n in plat["notes"])
    best_practices = "\n".join(f"- {b}" for b in fmt["best_practices"])
    inspo_block = "\n".join(f"- {n}" for n in inspo_notes) if inspo_notes else "(none provided)"

    strategy = brand.get("strategy_answers") or {}

    user_prompt = f"""
FORMAT: {fmt['name']}
PLATFORM: {plat['name']}

FORMAT STRUCTURE TO FOLLOW:
{skeleton}

FORMAT BEST PRACTICES:
{best_practices}

PLATFORM NOTES:
{platform_notes}

BUILD SPEC (length/structure the user chose):
{build_spec}

CREATIVE ANGLE / SERIES CONTEXT:
{creative_angle or "(standalone piece, no series/campaign)"}

BRAND STRATEGY:
{strategy}

RELEVANT INSPIRATION PATTERNS THE BRAND LIKES:
{inspo_block}

CONTENT IDEA TO WRITE FROM:
Topic: {idea.get('topic', '')}
Suggested angle: {idea.get('suggested_angle', '')}

Write the full piece now, broken out clearly by the structural parts above
(label each part). Then on a new line write "---METADATA---" followed by a
one-line rationale explaining which inspiration patterns and strategy
points you drew from.
"""
    return BASE_SYSTEM + "\n" + writing_standards_prompt_block(), user_prompt


def generate_content(brand: dict, format_id: str, platform_id: str, idea: dict,
                      build_spec: dict, inspo_notes: list, creative_angle: str = ""):
    system, user = build_generation_prompt(brand, format_id, platform_id, idea, build_spec, inspo_notes, creative_angle)
    text = ai_client.ask(system, user, max_tokens=2200, temperature=0.85)
    if "---METADATA---" in text:
        body, meta = text.split("---METADATA---", 1)
    else:
        body, meta = text, ""
    return {"raw_text": body.strip(), "rationale": meta.strip()}


def revise_content(brand: dict, format_id: str, platform_id: str, previous_text: str, edit_comment: str):
    fmt = get_format(format_id)
    plat = get_platform(platform_id)
    system = BASE_SYSTEM + "\n" + writing_standards_prompt_block()
    user = f"""
Here is the current draft ({fmt['name']} for {plat['name']}):

{previous_text}

The user's revision request: "{edit_comment}"

Rewrite the full piece incorporating this feedback, still following the
format's structural skeleton and the platform's best practices. Return
only the revised piece, labeled by structural part.
"""
    text = ai_client.ask(system, user, max_tokens=2200, temperature=0.75)
    return {"raw_text": text.strip()}


def repurpose_content(brand: dict, source_format_id: str, source_platform_id: str,
                       target_format_id: str, target_platform_id: str, source_text: str):
    target_fmt = get_format(target_format_id)
    target_plat = get_platform(target_platform_id)
    skeleton = "\n".join(f"- {s['part']}: {s['guidance']}" for s in target_fmt["structure_skeleton"])
    platform_notes = "\n".join(f"- {n}" for n in target_plat["notes"])

    system = BASE_SYSTEM + "\n" + writing_standards_prompt_block()
    user = f"""
SOURCE CONTENT (originally written as {source_format_id} for {source_platform_id}):
{source_text}

Re-derive this for a NEW target - do not just reformat the same text.
Rebuild the hook, pacing, and structure to genuinely fit the new format
and platform, while preserving the core message, offer, and CTA intent.

TARGET FORMAT: {target_fmt['name']}
TARGET STRUCTURE:
{skeleton}

TARGET PLATFORM: {target_plat['name']}
TARGET PLATFORM NOTES:
{platform_notes}

Write the full repurposed piece now, labeled by structural part.
"""
    text = ai_client.ask(system, user, max_tokens=2200, temperature=0.85)
    return {"raw_text": text.strip()}
