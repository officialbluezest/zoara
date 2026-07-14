"""
Zoara's Knowledge Panel.
A curated library of real, well-regarded resources on copywriting and
content strategy. This is what "grounds" Zoara's writing instincts beyond
the format/platform modules - it's shown to users as a learning tab, and
selected principles from it are also injected into the generation and
critique prompts as writing standards Zoara must hold itself to.
"""

KNOWLEDGE_PANEL = {
    "core_writing_principles": [
        "Clarity beats cleverness. If a reader has to work to understand a line, cut it.",
        "Specificity is persuasive; vagueness is forgettable. Numbers, names, and details build belief.",
        "Write to one person, not a crowd. 'You' language outperforms 'people' or 'everyone'.",
        "Every sentence has one job: earn the next sentence's read. Cut anything that doesn't.",
        "Lead with the reader's interest (their problem/desire), not the brand's announcement.",
        "Show, don't just claim - a demonstrated result beats an asserted superlative every time.",
        "Good copy is edited copy - the first draft's job is to exist so the second draft can be good.",
        "Grammar and correctness are non-negotiable: correct writing is a trust signal, even in casual formats.",
    ],
    "books": [
        {"title": "Ogilvy on Advertising", "author": "David Ogilvy", "why": "The foundational text on research-driven, benefit-led advertising copy."},
        {"title": "The Copywriter's Handbook", "author": "Robert Bly", "why": "A practical, structural guide to headlines, body copy, and offers."},
        {"title": "Breakthrough Advertising", "author": "Eugene Schwartz", "why": "The deepest treatment of market awareness levels and how they should change your hook."},
        {"title": "Cashvertising", "author": "Drew Eric Whitman", "why": "Direct-response psychology - the 'Life-Force 8' desires that drive buying decisions."},
        {"title": "Building a StoryBrand", "author": "Donald Miller", "why": "The customer-as-hero framework used throughout Zoara's storytelling options."},
        {"title": "Everybody Writes", "author": "Ann Handley", "why": "Content-marketing-specific writing craft and editing discipline."},
        {"title": "Made to Stick", "author": "Chip & Dan Heath", "why": "Why some ideas are inherently more memorable and shareable than others."},
        {"title": "Influence", "author": "Robert Cialdini", "why": "The psychology behind persuasion principles (reciprocity, social proof, scarcity) used ethically in CTAs and offers."},
    ],
    "youtube_and_creators": [
        {"name": "Alex Cattoni (Copy Posse)", "why": "Modern direct-response copywriting for creators and online businesses."},
        {"name": "Copyhackers (YouTube + blog)", "why": "Conversion-focused copywriting breakdowns with real before/after examples."},
        {"name": "Think Media / Sunny Lenarduzzi", "why": "YouTube script structure and retention-focused storytelling for creators."},
        {"name": "Vanessa Lau / Later's social channels", "why": "Platform-specific short-form content strategy breakdowns."},
    ],
    "sites_and_communities": [
        {"name": "Copyhackers.com", "why": "Deep-dive articles on conversion copywriting frameworks."},
        {"name": "Swiped.co", "why": "Swipe file of real high-performing ad and sales copy for pattern study."},
        {"name": "AnswerThePublic-style query research", "why": "Used inside Zoara's own research engine to find what people are actually asking."},
        {"name": "r/copywriting, r/marketing (Reddit)", "why": "Real practitioner discussion and critique - also a live source for Zoara's research phase."},
    ],
}


def get_knowledge_panel():
    return KNOWLEDGE_PANEL


def writing_standards_prompt_block():
    """A compact block of the core principles for injection into every generation/critique prompt."""
    lines = "\n".join(f"- {p}" for p in KNOWLEDGE_PANEL["core_writing_principles"])
    return f"WRITING STANDARDS ZOARA MUST FOLLOW AT ALL TIMES:\n{lines}"
