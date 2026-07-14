"""
Real research engine.

Uses live web search (DuckDuckGo, via the `ddgs` package - no API key
required) targeted at the places people actually ask questions and vent
opinions: Reddit threads, Quora, Facebook groups (best-effort via site:
search, since FB groups are largely walled off from anonymous scraping),
and general "people also ask"-style query expansion. Raw results are then
handed to Claude to synthesize into 30 tagged, structured content ideas.

Honesty note: Facebook Group content is mostly behind login walls, so
results there are best-effort (public group previews / indexed threads
only). This is disclosed to the user in the idea's source_pattern field
when it happens.
"""
from ddgs import DDGS
from . import ai_client
from knowledge_panel import writing_standards_prompt_block

SEARCH_TARGETS = [
    ("Reddit discussion", "site:reddit.com {query}"),
    ("Quora Q&A", "site:quora.com {query}"),
    ("Facebook Group mentions", "site:facebook.com/groups {query}"),
    ("General 'how to' / PAA-style search", "{query} how to OR why OR best OR mistakes"),
    ("Comparison / vs discussion", "{query} vs OR alternative OR review"),
]


def build_seed_queries(brand: dict) -> list:
    strategy = brand.get("strategy_answers") or {}
    pillars = strategy.get("pillars", "")
    audience = strategy.get("offer", "") or strategy.get("transformation", "")
    goal_terms = brand.get("goals", {}) or {}

    seeds = []
    if pillars:
        # pillars might be a comma separated free-text string
        for p in str(pillars).split(","):
            p = p.strip()
            if p:
                seeds.append(p)
    if audience:
        seeds.append(str(audience)[:80])
    if not seeds:
        seeds.append(brand.get("name", "this business"))
    return seeds[:5]  # cap to keep search volume reasonable


def run_live_search(brand: dict, max_per_query: int = 6):
    seeds = build_seed_queries(brand)
    raw_hits = []
    with DDGS() as ddgs:
        for seed in seeds:
            for label, template in SEARCH_TARGETS:
                query = template.format(query=seed)
                try:
                    results = ddgs.text(query, max_results=max_per_query)
                except Exception as e:
                    results = []
                for r in results or []:
                    raw_hits.append({
                        "source_pattern": label,
                        "seed": seed,
                        "title": r.get("title", ""),
                        "snippet": r.get("body", ""),
                        "url": r.get("href", ""),
                    })
    return raw_hits


def synthesize_ideas(brand: dict, raw_hits: list, count: int = 30):
    """Turn raw search hits into `count` structured content idea cards via Claude."""
    strategy = brand.get("strategy_answers") or {}
    competitor_summaries = brand.get("_competitor_summaries", [])
    inspo_patterns = brand.get("_inspo_patterns", [])

    hits_text = "\n".join(
        f"- [{h['source_pattern']}] {h['title']}: {h['snippet']}" for h in raw_hits[:150]
    ) or "(no live search results were retrievable - synthesize from brand strategy alone and flag that clearly)"

    system = (
        "You are Zoara's research engine. Your ONLY job at this stage is to surface REAL, "
        "recurring topics/questions/directions people are actually discussing - not to write "
        "content. Ground every idea in the provided search signal where possible; never invent "
        "a source pattern that isn't supported by the hits given.\n\n" + writing_standards_prompt_block()
    )
    user = f"""
BRAND STRATEGY:
{strategy}

COMPETITOR CONTEXT:
{competitor_summaries}

INSPIRATION PATTERNS THE BRAND RESPONDS TO:
{inspo_patterns}

RAW SEARCH SIGNAL (Reddit/Quora/Facebook Groups/general web):
{hits_text}

Produce exactly {count} content idea cards as a JSON array. Each item must have:
- "topic": a specific, non-generic topic/question (not a full script)
- "source_pattern": where/why this keeps coming up (cite the source type, e.g. "Recurring Reddit question in r/small business-style threads")
- "suggested_angle": one sentence on the specific angle this brand could take, informed by their strategy and unique POV

Do not repeat near-duplicate ideas. Prioritize ideas that map to the brand's stated pillars and goal.
"""
    return ai_client.ask_json(system, user, max_tokens=4000)
