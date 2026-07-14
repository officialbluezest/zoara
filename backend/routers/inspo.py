from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

import repo
from services.scraper import read_link
from services import ai_client

router = APIRouter(prefix="/api/brands/{brand_id}/inspo", tags=["inspo"])

ROOMS = ["hooks", "visual_style", "storytelling", "offers_ctas", "tone_personality"]


class AddInspo(BaseModel):
    room: str
    url: str
    user_note: str  # "what specifically do you like about this" - required, this is the highest-signal field


@router.post("")
def add_inspo(brand_id: str, payload: AddInspo):
    if payload.room not in ROOMS:
        raise HTTPException(400, f"room must be one of {ROOMS}")
    if not repo.get_brand(brand_id):
        raise HTTPException(404, "Brand not found")
    if not payload.user_note.strip():
        raise HTTPException(400, "Tell Zoara what you specifically like about this - that's the part that actually teaches her your taste.")

    item = repo.add_inspo(brand_id, payload.room, payload.url, payload.user_note)
    result = read_link(payload.url)

    if result.get("source") == "error":
        repo.update_inspo(item["id"], "", "", status="manual_needed")
        return {**item, "status": "manual_needed",
                "note": "Zoara couldn't auto-read this link (common for private/login-walled posts). "
                        "You can paste the caption/transcript manually via PATCH if you want her to learn from it."}

    text_blob = result.get("body_text") or result.get("title", "") or result.get("html_snippet", "")
    system = ("You are Zoara analyzing a piece of inspiration content the user submitted, in the "
               f"'{payload.room}' room, to learn their taste. They told you what they like about it: "
               f"\"{payload.user_note}\". Identify the concrete, reusable PATTERN behind what they like "
               "(a technique, structure, or style choice), not just a restatement of their note.")
    user = f"Content pulled from the link:\n{text_blob[:3000]}\n\nWhat specific, nameable pattern should Zoara extract and reuse for this brand? Answer in 1-2 sentences."
    try:
        pattern = ai_client.ask(system, user, max_tokens=200)
    except RuntimeError:
        pattern = ""

    summary = text_blob[:400]
    return repo.update_inspo(item["id"], summary, pattern.strip())


@router.get("")
def list_inspo(brand_id: str, room: Optional[str] = None):
    return repo.list_inspo(brand_id, room)
