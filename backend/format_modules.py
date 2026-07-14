"""
The Format Module library.
Each format defines: how it's structured, what length/build options exist,
what inspiration-dropdown menus should show for that format (hooks,
storytelling frameworks, CTAs, and format-specific extras), and the
best-practice rules Zoara must follow when writing in that format.
This is the core knowledge that gets injected into every generation prompt.
"""

HOOK_TYPES = [
    "Question hook", "Bold claim / statement", "Pattern interrupt",
    "POV / relatable scenario", "Shocking stat or number", "Story cold-open",
    "Contrarian take", "Direct callout to audience ('If you're a...')",
    "Before/After tease", "Listicle promise ('3 ways to...')",
    "Problem/pain naming", "Curiosity gap / open loop", "Let Zoara decide from my inspo",
]

STORYTELLING_FRAMEWORKS = [
    "PAS (Problem - Agitate - Solve)",
    "AIDA (Attention - Interest - Desire - Action)",
    "Before - After - Bridge",
    "StoryBrand / SB7 (customer as hero, brand as guide)",
    "Hero's Journey (mini/compressed)",
    "Listicle (numbered points)",
    "Myth-bust (common belief vs. truth)",
    "Case study / proof narrative",
    "FAQ format",
    "Day-in-the-life",
    "Let Zoara decide from my inspo",
]

CTA_TYPES = [
    "Soft engagement ('comment below', 'tag a friend')",
    "Save/share prompt",
    "Direct offer CTA ('shop now', 'book a call')",
    "Link-in-bio / DM keyword CTA",
    "Urgency/scarcity close",
    "Question-based CTA (invites conversation)",
    "Next-step tease (sets up next post in a series)",
    "Let Zoara decide",
]

FORMAT_MODULES = {

    "sales_script": {
        "name": "Sales Script",
        "description": "Direct-response copy written to be spoken or read with the explicit job of moving someone toward a purchase decision.",
        "best_for_platforms": ["instagram", "facebook", "tiktok", "youtube_longform"],
        "structure_skeleton": [
            {"part": "Hook", "guidance": "Name the pain or desire in the first line. No throat-clearing."},
            {"part": "Agitate", "guidance": "Make the cost of inaction concrete and specific, not generic fear."},
            {"part": "Mechanism", "guidance": "Introduce the unique way your offer solves this differently than alternatives."},
            {"part": "Proof", "guidance": "Result, testimonial, number, or demonstration that makes the claim credible."},
            {"part": "Offer", "guidance": "State exactly what they get, in plain terms."},
            {"part": "CTA", "guidance": "One clear next action. Never two competing CTAs."},
            {"part": "Urgency/Close", "guidance": "Real reason to act now (deadline, capacity, cost of waiting) - never fabricated scarcity."},
        ],
        "length_options": [
            {"label": "Short (30-45 sec spoken / ~90-130 words)", "value": "short"},
            {"label": "Medium (60-90 sec spoken / ~150-230 words)", "value": "medium"},
            {"label": "Long (2-3 min spoken / ~300-450 words)", "value": "long"},
            {"label": "Custom word count", "value": "custom"},
        ],
        "inspiration_dropdowns": {
            "hooks": HOOK_TYPES,
            "storytelling_frameworks": STORYTELLING_FRAMEWORKS,
            "ctas": CTA_TYPES,
            "extra": {"label": "Proof style", "options": [
                "Customer testimonial (verbatim style)", "Before/after numbers",
                "Founder credibility story", "Third-party stat/press", "Live demonstration narration",
            ]},
        },
        "best_practices": [
            "Every claim needs to be provable or softened - never write a claim you can't back up.",
            "Specificity beats superlatives: '312 businesses' beats 'hundreds of businesses'.",
            "One offer, one CTA. Multiple asks kill conversion.",
            "Write for the ear if it's meant to be spoken: short sentences, contractions, natural pauses.",
        ],
    },

    "talking_head_video": {
        "name": "Talking-Head Video",
        "description": "A script for a person speaking directly to camera - Reels, TikToks, YouTube Shorts, or longer vlogs.",
        "best_for_platforms": ["tiktok", "instagram", "youtube_shorts"],
        "structure_skeleton": [
            {"part": "Hook", "guidance": "Spoken in the first 1-2 seconds. Must work with sound off too if text-on-screen is used."},
            {"part": "Setup", "guidance": "One sentence of context - why should they keep watching."},
            {"part": "Core point(s)", "guidance": "Max 3 points for short-form. Each point needs its own micro-payoff."},
            {"part": "Payoff/Insight", "guidance": "The 'aha' - what they didn't know before this video."},
            {"part": "CTA", "guidance": "Single, natural next action - said, not just captioned."},
        ],
        "length_options": [
            {"label": "10-15 sec", "value": "10-15s"},
            {"label": "15-30 sec", "value": "15-30s"},
            {"label": "30-45 sec", "value": "30-45s"},
            {"label": "45 sec - 1:20", "value": "45s-80s"},
            {"label": "2-3 min (short-form long)", "value": "2-3min"},
            {"label": "Custom", "value": "custom"},
        ],
        "inspiration_dropdowns": {
            "hooks": HOOK_TYPES,
            "storytelling_frameworks": STORYTELLING_FRAMEWORKS,
            "ctas": CTA_TYPES,
            "extra": {"label": "Delivery energy", "options": [
                "High-energy/fast-cut", "Calm/authoritative", "Conversational/casual",
                "Documentary/explainer", "Comedic/playful",
            ]},
        },
        "best_practices": [
            "The first line must survive without visuals - write it to work as pure audio.",
            "Cut every sentence that doesn't earn the next second of watch time.",
            "Text-on-screen should reinforce a different detail than the voiceover says verbatim, not just caption it.",
            "End on the payoff or CTA, never trail off.",
        ],
    },

    "flyer_static_post": {
        "name": "Flyer / Static Post",
        "description": "A single-image piece of copy - event flyers, promo graphics, single-slide announcements.",
        "best_for_platforms": ["instagram", "facebook", "linkedin"],
        "structure_skeleton": [
            {"part": "Headline", "guidance": "Carries the most visual and message weight. Should work as a 2-second read."},
            {"part": "Subheadline", "guidance": "Expands the headline with the specific benefit or detail."},
            {"part": "Body", "guidance": "Optional. Choose list or short-paragraph form depending on the build spec."},
            {"part": "CTA + Detail", "guidance": "Action + the practical info needed to take it (date, link, price)."},
        ],
        "length_options": [
            {"label": "Headline + CTA only (minimal)", "value": "minimal"},
            {"label": "Headline + subheadline + CTA", "value": "standard"},
            {"label": "Full build: headline + subheadline + body (list) + CTA", "value": "full_list"},
            {"label": "Full build: headline + subheadline + body (paragraph) + CTA", "value": "full_paragraph"},
        ],
        "inspiration_dropdowns": {
            "hooks": ["Benefit-led headline", "Curiosity headline", "Urgency headline", "Number/stat headline", "Question headline"],
            "ctas": CTA_TYPES,
            "extra": {"label": "Body style", "options": [
                "3-4 bullet value points", "Short single paragraph", "Numbered steps", "None - visual only",
            ]},
        },
        "best_practices": [
            "The headline must stand alone - assume the viewer reads nothing else.",
            "Never bury the date/price/link inside a paragraph - keep practical details scannable.",
            "One primary CTA. A flyer with three asks converts none of them.",
        ],
    },

    "carousel": {
        "name": "Carousel",
        "description": "A multi-slide post where each slide carries one idea, built to maximize saves and swipe-through.",
        "best_for_platforms": ["instagram", "linkedin", "facebook"],
        "structure_skeleton": [
            {"part": "Slide 1 (Cover/Hook)", "guidance": "Must work as a standalone thumbnail - this is what gets the swipe."},
            {"part": "Slides 2-N (Body)", "guidance": "One idea per slide. Never cram two points on one slide."},
            {"part": "Final slide (Summary + CTA)", "guidance": "Recap the value in one line, then a clear next action."},
        ],
        "length_options": [
            {"label": "Short (5 slides)", "value": "5"},
            {"label": "Standard (7-8 slides)", "value": "7-8"},
            {"label": "Long (10 slides)", "value": "10"},
            {"label": "Custom slide count", "value": "custom"},
        ],
        "inspiration_dropdowns": {
            "hooks": HOOK_TYPES,
            "storytelling_frameworks": STORYTELLING_FRAMEWORKS,
            "ctas": CTA_TYPES,
            "extra": {"label": "Content build per slide", "options": [
                "Headline only per slide", "Headline + 1-2 line explanation per slide",
                "Headline + bullet list per slide", "Question + answer per slide",
            ]},
        },
        "best_practices": [
            "Slide 1 has to work with zero context - most people see it in-feed before they ever swipe.",
            "Keep text per slide under ~25-30 words - carousels are skimmed, not read.",
            "Design a clear visual thread so slide-to-slide feels like one idea unfolding, not disconnected tips.",
        ],
    },

    "text_on_broll": {
        "name": "Text-on-B-roll",
        "description": "Short text beats timed over background footage, often with no or minimal voiceover.",
        "best_for_platforms": ["tiktok", "instagram", "youtube_shorts"],
        "structure_skeleton": [
            {"part": "Opening beat", "guidance": "The hook, as a punchy on-screen line, not a full sentence."},
            {"part": "Beats 2-N", "guidance": "Each beat = one small idea, timed to a visual cut."},
            {"part": "Final beat", "guidance": "Payoff line or CTA - the line people screenshot."},
        ],
        "length_options": [
            {"label": "6-8 beats (~15-20 sec)", "value": "6-8"},
            {"label": "10-14 beats (~30-45 sec)", "value": "10-14"},
            {"label": "16-20 beats (~1 min)", "value": "16-20"},
            {"label": "Custom beat count", "value": "custom"},
        ],
        "inspiration_dropdowns": {
            "hooks": HOOK_TYPES,
            "storytelling_frameworks": STORYTELLING_FRAMEWORKS,
            "extra": {"label": "Pacing style", "options": [
                "Fast cut (1 beat per 1-2 sec)", "Medium (1 beat per 2-4 sec)", "Slow/cinematic (1 beat per 4-6 sec)",
            ]},
        },
        "best_practices": [
            "No more than ~8-10 words per beat - it has to be read in one glance.",
            "Each beat should be able to stand alone as a screenshot-worthy line.",
            "Build toward a single punchline or payoff, not a flat list of facts.",
        ],
    },

    "meme": {
        "name": "Meme",
        "description": "Relatable, humor-driven content built on a setup/punchline structure, with a light or absent brand tie-in.",
        "best_for_platforms": ["instagram", "tiktok", "x", "facebook"],
        "structure_skeleton": [
            {"part": "Setup", "guidance": "A relatable premise the audience instantly recognizes - usually the top text or first frame."},
            {"part": "Punchline", "guidance": "The twist, exaggeration, or relatable payoff - bottom text or caption."},
            {"part": "Brand tie-in (optional)", "guidance": "Only if it lands naturally - forced branding kills memes."},
        ],
        "length_options": [
            {"label": "Classic 2-line (setup/punchline)", "value": "classic"},
            {"label": "Caption-driven (image + longer caption)", "value": "caption_driven"},
        ],
        "inspiration_dropdowns": {
            "extra": {"label": "Humor style", "options": [
                "Self-deprecating", "Observational/relatable", "Exaggeration", "Absurdist",
                "Industry-insider joke", "Trend/format remix",
            ]},
        },
        "best_practices": [
            "The relatability has to be real - if the brand's audience doesn't actually feel this, skip it.",
            "Never force the product into the punchline; let the brand show up in tone, not the joke's mechanics.",
            "Simplicity wins - the best memes are readable in under 2 seconds.",
        ],
    },

    "story_sequence": {
        "name": "Story Sequence",
        "description": "A multi-frame Story (IG/FB) sequence designed for tap-through, using polls, questions, or countdowns as native interaction.",
        "best_for_platforms": ["instagram", "facebook"],
        "structure_skeleton": [
            {"part": "Frame 1 (Hook/Tease)", "guidance": "Open a loop that only resolves by tapping through."},
            {"part": "Frames 2-N", "guidance": "Build the idea/offer one small reveal at a time; use interactive stickers where natural."},
            {"part": "Final frame (CTA)", "guidance": "Swipe-up/link sticker or DM keyword CTA."},
        ],
        "length_options": [
            {"label": "3-4 frames", "value": "3-4"},
            {"label": "5-7 frames", "value": "5-7"},
            {"label": "8-10 frames", "value": "8-10"},
        ],
        "inspiration_dropdowns": {
            "hooks": HOOK_TYPES,
            "ctas": CTA_TYPES,
            "extra": {"label": "Interactive elements", "options": [
                "Poll sticker", "Quiz sticker", "Question box", "Countdown sticker", "Slider sticker", "None",
            ]},
        },
        "best_practices": [
            "Each frame should require almost no read time - Stories are consumed in under a second per frame.",
            "Use interaction stickers to boost algorithmic reach, not just for decoration.",
            "Keep a consistent visual thread so viewers know they're mid-sequence, not on a new post.",
        ],
    },

    "thread": {
        "name": "Thread (X)",
        "description": "A multi-post sequence on X where each tweet needs its own hook while building one continuous argument or story.",
        "best_for_platforms": ["x"],
        "structure_skeleton": [
            {"part": "Tweet 1 (Hook)", "guidance": "Must work as a standalone tweet - this is what gets the click to expand."},
            {"part": "Tweets 2-N", "guidance": "One idea per tweet; each needs a mini hook of its own since people drop off."},
            {"part": "Final tweet (Close)", "guidance": "Summary + soft CTA (follow, reply, or link)."},
        ],
        "length_options": [
            {"label": "Short thread (4-6 tweets)", "value": "4-6"},
            {"label": "Standard (8-12 tweets)", "value": "8-12"},
            {"label": "Long-form thread (15+ tweets)", "value": "15+"},
        ],
        "inspiration_dropdowns": {
            "hooks": HOOK_TYPES,
            "storytelling_frameworks": STORYTELLING_FRAMEWORKS,
            "extra": {"label": "Tone", "options": [
                "Opinion/POV-driven", "Educational/how-to", "Story/narrative", "Data-driven breakdown",
            ]},
        },
        "best_practices": [
            "Tweet 1 has to earn the expand-click entirely on its own - no context from later tweets counts.",
            "Avoid corporate/marketing tone - X rewards a clear personal point of view.",
            "Each tweet should be readable and complete alone, even out of order.",
        ],
    },

    "youtube_longform": {
        "name": "Long-form YouTube Script",
        "description": "A full-length video script (typically 5-20+ minutes) with chaptered structure for retention.",
        "best_for_platforms": ["youtube_longform"],
        "structure_skeleton": [
            {"part": "Cold open hook (10-15 sec)", "guidance": "Show the payoff or stakes before any intro/branding."},
            {"part": "Promise/preview", "guidance": "Tell them exactly what they'll get and why it's worth the watch time."},
            {"part": "Body (chaptered sections)", "guidance": "Each chapter = one clear sub-topic with its own mini-arc."},
            {"part": "Recap", "guidance": "Reinforce the core takeaway before the close."},
            {"part": "CTA", "guidance": "Subscribe/next-video/offer - stated clearly, not assumed."},
        ],
        "length_options": [
            {"label": "Short-long (5-8 min)", "value": "5-8min"},
            {"label": "Standard (8-15 min)", "value": "8-15min"},
            {"label": "Deep-dive (15-25 min)", "value": "15-25min"},
            {"label": "Custom", "value": "custom"},
        ],
        "inspiration_dropdowns": {
            "hooks": HOOK_TYPES,
            "storytelling_frameworks": STORYTELLING_FRAMEWORKS,
            "ctas": CTA_TYPES,
            "extra": {"label": "Chapter style", "options": [
                "Numbered list format", "Chronological/story format", "Problem-by-problem breakdown", "Q&A format",
            ]},
        },
        "best_practices": [
            "Retention lives or dies in the first 30 seconds - never open with channel branding before the hook.",
            "Every chapter transition should tease forward ('but here's where it gets interesting...').",
            "Write spoken, not written, English - contractions, shorter clauses, natural rhythm.",
        ],
    },

    "ugc_ad_script": {
        "name": "UGC / Ad Script",
        "description": "A script written to sound like authentic user-generated content, for use as a paid ad or organic seed post.",
        "best_for_platforms": ["tiktok", "instagram", "facebook"],
        "structure_skeleton": [
            {"part": "Hook", "guidance": "Must sound like a real person talking, not a brand - avoid ad-speak entirely."},
            {"part": "Relatable problem", "guidance": "Name the exact situation the target customer is in right now."},
            {"part": "Discovery/Turning point", "guidance": "How they found the product - kept casual and specific."},
            {"part": "Result", "guidance": "Concrete, specific outcome - numbers or before/after beat vague praise."},
            {"part": "CTA", "guidance": "Casual, first-person recommendation tone, not a corporate command."},
        ],
        "length_options": [
            {"label": "15-30 sec", "value": "15-30s"},
            {"label": "30-45 sec", "value": "30-45s"},
            {"label": "45-60 sec", "value": "45-60s"},
            {"label": "Custom", "value": "custom"},
        ],
        "inspiration_dropdowns": {
            "hooks": HOOK_TYPES,
            "storytelling_frameworks": STORYTELLING_FRAMEWORKS,
            "extra": {"label": "Creator persona", "options": [
                "Skeptic-turned-believer", "Excited discovery", "Comparison ('I tried X vs Y')",
                "Routine/day-in-the-life integration", "Problem-solved testimonial",
            ]},
        },
        "best_practices": [
            "If it reads like ad copy, rewrite it - UGC only works when it sounds unscripted.",
            "Specific, slightly imperfect phrasing outperforms polished marketing language here.",
            "The result claimed must be realistic and honest - exaggerated UGC destroys trust fast when caught.",
        ],
    },

    "testimonial_case_study": {
        "name": "Testimonial / Case Study",
        "description": "Proof-driven content built around a real (or realistic composite) customer result.",
        "best_for_platforms": ["instagram", "linkedin", "facebook", "youtube_longform"],
        "structure_skeleton": [
            {"part": "Before state", "guidance": "The specific problem/pain the customer had - concrete, not generic."},
            {"part": "Turning point", "guidance": "Why they chose this brand/product over alternatives."},
            {"part": "Process", "guidance": "Brief - what actually happened, kept credible and specific."},
            {"part": "Result", "guidance": "The measurable or clearly observable after state."},
            {"part": "CTA", "guidance": "Invite the viewer to see themselves in this outcome."},
        ],
        "length_options": [
            {"label": "Short quote-style (under 100 words)", "value": "short"},
            {"label": "Standard narrative (150-300 words)", "value": "standard"},
            {"label": "Full case study (400-700 words)", "value": "full"},
        ],
        "inspiration_dropdowns": {
            "storytelling_frameworks": ["Before-After-Bridge", "Case study / proof narrative", "Problem-Agitate-Solve", "Let Zoara decide"],
            "extra": {"label": "Proof format", "options": [
                "Written quote + result stat", "Interview-style Q&A", "Narrated case study (no direct quote)", "Screenshot/data-led",
            ]},
        },
        "best_practices": [
            "Specific numbers and timeframes make a testimonial believable; vague praise doesn't.",
            "Keep the customer's authentic voice - don't over-polish quotes into marketing-speak.",
            "Always show the before state clearly - the result only means something in contrast.",
        ],
    },
}


def list_formats():
    return [{"id": k, "name": v["name"], "description": v["description"]} for k, v in FORMAT_MODULES.items()]


def get_format(format_id):
    return FORMAT_MODULES.get(format_id)
