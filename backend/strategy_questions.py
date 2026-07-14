"""
The Strategy Interview.
Framed the way a senior brand strategist would actually run discovery -
drawing on positioning theory, Jobs-to-be-Done, and StoryBrand-style
customer-as-hero framing - rather than generic marketing-brief questions.
Asked one at a time in the flow engine.
"""

STRATEGY_QUESTIONS = [
    {
        "id": "offer",
        "question": "In one sentence: what do you sell, and to whom?",
        "why": "Forces offer clarity before anything else gets built on top of it.",
    },
    {
        "id": "transformation",
        "question": "What's the specific transformation you deliver - what does the customer's 'before' look like, and what does 'after' look like?",
        "why": "Content that shows a clear before/after outperforms content that just lists features.",
    },
    {
        "id": "anti_audience",
        "question": "Who is this brand explicitly NOT for?",
        "why": "Sharpening who you'll disappoint is often the fastest way to sharpen who you'll attract.",
    },
    {
        "id": "jobs_to_be_done",
        "question": "Beyond the literal product/service, what 'job' is the customer really hiring you to do? (e.g. not just 'a gym' but 'help me feel in control of my life again')",
        "why": "Jobs-to-be-Done thinking - the real motivation is rarely the surface-level product category.",
    },
    {
        "id": "objection",
        "question": "What's the #1 objection or hesitation that stops people from buying, even when they're interested?",
        "why": "Content that pre-handles the real objection converts; content that ignores it doesn't.",
    },
    {
        "id": "brand_personality",
        "question": "If your brand were a person at a party, how would they talk and act? Give 3 adjectives.",
        "why": "Sets the voice calibration Zoara writes in for every piece of content.",
    },
    {
        "id": "reputation_gap",
        "question": "What do you want to be known for that you're not fully known for yet?",
        "why": "Identifies the positioning gap content needs to close.",
    },
    {
        "id": "competitors",
        "question": "Name 2-3 competitors or brands you admire in this space, and what you think they do better or worse than you.",
        "why": "Used alongside the competitor links you add separately, to sharpen contrast and differentiation.",
    },
    {
        "id": "past_performance",
        "question": "What content (if any) has performed best for you so far, and why do you think it worked?",
        "why": "Real performance history is a stronger signal than any brief - never ignored if available.",
    },
    {
        "id": "pillars",
        "question": "What 3-5 topics or pillars do you want to be seen as an authority on?",
        "why": "Keeps the content calendar and research phase anchored instead of drifting topic to topic.",
    },
    {
        "id": "business_goal",
        "question": "What's the actual business goal behind content right now - revenue, leads, brand awareness, hiring, community, something else?",
        "why": "Every downstream generation and critique step is judged against this goal.",
    },
    {
        "id": "guardrails",
        "question": "Are there any words, phrases, claims, or topics Zoara should never use for this brand (legal, tone, past issues)?",
        "why": "A real strategist always asks what NOT to do, not just what to do.",
    },
    {
        "id": "unique_pov",
        "question": "What's a belief, story, or opinion that's uniquely yours - something a competitor couldn't say the same way?",
        "why": "This is usually the single highest-leverage content angle a brand has and is almost always under-used.",
    },
    {
        "id": "success_90_days",
        "question": "In one sentence, what does success look like 90 days from now?",
        "why": "Gives Zoara a concrete finish line to write toward, not just a vague 'more engagement'.",
    },
]


def get_questions():
    return STRATEGY_QUESTIONS
