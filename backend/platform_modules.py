"""
Platform playbooks. Injected into generation/critique prompts whenever
that platform is selected. Keep these editable - platform norms shift over
time, and this file is the single place that should change when they do.
"""

PLATFORM_MODULES = {
    "instagram": {
        "name": "Instagram",
        "notes": [
            "Reels are favored for reach; carousels are favored for saves and shares (dwell time signal).",
            "Hook must land in the first 1-2 seconds, visually or via on-screen text - many watch muted.",
            "Captions: front-load the value in the first line, since the rest gets cut off in feed.",
            "Specific CTAs ('Save this for later', 'Comment GUIDE and I'll send it') outperform 'link in bio'.",
            "Hashtags matter less than they used to; 3-5 relevant ones is plenty.",
        ],
        "ideal_specs": {"reel_length": "7-90 sec (15-30 sec sweet spot for reach)", "carousel_slides": "up to 10", "caption_length": "125 chars before fold"},
    },
    "tiktok": {
        "name": "TikTok",
        "notes": [
            "Native, slightly unpolished content consistently outperforms overly produced ads.",
            "Hook = first spoken line AND first line of caption; open loops and pattern interrupts work well.",
            "Text-on-screen should reinforce a different detail than the voiceover, not just repeat it.",
            "Watch time and re-watches matter more than raw likes - loopable endings help retention.",
            "Trending sounds should serve the message, never override it.",
        ],
        "ideal_specs": {"video_length": "9-60 sec (15-34 sec sweet spot)", "caption_length": "short, punchy, 1-2 lines"},
    },
    "facebook": {
        "name": "Facebook",
        "notes": [
            "Older, more link-tolerant audience - native video and point-of-view text posts still perform well.",
            "Groups and comment threads are an underrated distribution channel.",
            "Longer captions are tolerated if the first 2 lines earn the 'See more' click.",
        ],
        "ideal_specs": {"video_length": "15 sec - 3 min for feed, longer tolerated in groups", "caption_length": "first 2 lines critical"},
    },
    "x": {
        "name": "X (Twitter)",
        "notes": [
            "Threads reward a strong, standalone first tweet; every following tweet needs its own mini-hook.",
            "Text-first, opinion/POV-driven content outperforms polished marketing tone.",
            "Replies and self-quote-tweets extend a thread's life.",
            "CTAs work better as a soft closing line than a hard sell.",
        ],
        "ideal_specs": {"tweet_length": "under 280 chars per tweet ideally, thread 4-15+ tweets", "media": "images/video boost engagement"},
    },
    "linkedin": {
        "name": "LinkedIn",
        "notes": [
            "Personal, story-led posts consistently outperform corporate-toned ones.",
            "First 2-3 lines before the 'see more' fold are everything - treat it like a headline.",
            "Short-line, whitespace-heavy formatting increases readability and dwell time.",
            "Document/carousel posts perform very well for how-to and educational content.",
            "CTAs that invite conversation ('What's your take?') outperform hard pitches.",
        ],
        "ideal_specs": {"post_length": "150-300 words sweet spot, hook in first 2 lines", "carousel_slides": "6-12 slides"},
    },
    "youtube_shorts": {
        "name": "YouTube Shorts",
        "notes": [
            "Same short-form logic as TikTok/Reels but with slightly higher tolerance for informational density.",
            "Titles and thumbnails still matter even for Shorts - treat the first frame as a thumbnail.",
            "Loop-friendly endings increase replay rate, a strong ranking signal.",
        ],
        "ideal_specs": {"video_length": "under 60 sec"},
    },
    "youtube_longform": {
        "name": "YouTube (Long-form)",
        "notes": [
            "Retention in the first 30 seconds is the single biggest ranking factor - hook before branding.",
            "Chaptered structure with clear mid-video re-hooks keeps retention from decaying.",
            "Thumbnail + title do the discovery work; the script's job is to deliver on that promise fast.",
        ],
        "ideal_specs": {"video_length": "8-20 min sweet spot for most niches"},
    },
}


def list_platforms():
    return [{"id": k, "name": v["name"]} for k, v in PLATFORM_MODULES.items()]


def get_platform(platform_id):
    return PLATFORM_MODULES.get(platform_id)
