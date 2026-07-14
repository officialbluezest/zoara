from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, Dict

import repo
from services import generator, critique as critique_service

router = APIRouter(prefix="/api/content", tags=["content"])


class GenerateRequest(BaseModel):
    brand_id: str
    format_id: str
    platform_id: str
    research_idea_id: Optional[str] = None
    manual_topic: Optional[str] = None
    build_spec: Dict[str, Any] = {}
    creative_angle: Optional[str] = ""


class ReviseRequest(BaseModel):
    edit_comment: str


class RepurposeRequest(BaseModel):
    target_format_id: str
    target_platform_id: str


class CritiqueRequest(BaseModel):
    goal: Optional[str] = ""


class CommentRequest(BaseModel):
    comment: str


def _resolve_idea(payload: GenerateRequest):
    if payload.research_idea_id:
        idea = repo.get_research_idea(payload.research_idea_id)
        if not idea:
            raise HTTPException(404, "Research idea not found")
        return idea
    if payload.manual_topic:
        return {"topic": payload.manual_topic, "suggested_angle": ""}
    raise HTTPException(400, "Provide either research_idea_id or manual_topic")


def _inspo_notes(brand_id):
    items = repo.list_inspo(brand_id)
    return [f"[{i['room']}] {i['extracted_pattern']}" for i in items if i.get("extracted_pattern")]


@router.post("/generate")
def generate(payload: GenerateRequest):
    brand = repo.get_brand(payload.brand_id)
    if not brand:
        raise HTTPException(404, "Brand not found")
    idea = _resolve_idea(payload)
    inspo_notes = _inspo_notes(payload.brand_id)

    try:
        result = generator.generate_content(
            brand, payload.format_id, payload.platform_id, idea,
            payload.build_spec, inspo_notes, payload.creative_angle or "",
        )
    except RuntimeError as e:
        raise HTTPException(400, str(e))

    idea_id = payload.research_idea_id if payload.research_idea_id else None
    return repo.create_content(
        payload.brand_id, payload.format_id, payload.platform_id, idea_id,
        {"rationale": result["rationale"]}, result["raw_text"],
        title=idea.get("topic", "")[:80],
    )


@router.get("")
def list_content(brand_id: str):
    return repo.list_content(brand_id)


@router.get("/{content_id}")
def get_content(content_id: str):
    item = repo.get_content(content_id)
    if not item:
        raise HTTPException(404, "Content not found")
    return item


@router.post("/{content_id}/revise")
def revise(content_id: str, payload: ReviseRequest):
    item = repo.get_content(content_id)
    if not item:
        raise HTTPException(404, "Content not found")
    brand = repo.get_brand(item["brand_id"])
    try:
        result = generator.revise_content(brand, item["format"], item["platform"], item["raw_text"], payload.edit_comment)
    except RuntimeError as e:
        raise HTTPException(400, str(e))
    return repo.update_content(content_id, result["raw_text"], status="revised")


@router.post("/{content_id}/repurpose")
def repurpose(content_id: str, payload: RepurposeRequest):
    item = repo.get_content(content_id)
    if not item:
        raise HTTPException(404, "Content not found")
    brand = repo.get_brand(item["brand_id"])
    try:
        result = generator.repurpose_content(
            brand, item["format"], item["platform"],
            payload.target_format_id, payload.target_platform_id, item["raw_text"],
        )
    except RuntimeError as e:
        raise HTTPException(400, str(e))
    return repo.create_content(
        item["brand_id"], payload.target_format_id, payload.target_platform_id,
        item.get("research_idea_id"), {}, result["raw_text"],
        parent_id=content_id, title=f"[Repurposed] {item.get('title','')}"[:80],
    )


@router.post("/{content_id}/critique")
def run_critique(content_id: str, payload: CritiqueRequest):
    item = repo.get_content(content_id)
    if not item:
        raise HTTPException(404, "Content not found")
    brand = repo.get_brand(item["brand_id"])
    goal = payload.goal or (brand.get("goals") or {}).get("primary_goal", "")
    try:
        result = critique_service.critique_content(brand, item["format"], item["platform"], item["raw_text"], goal)
    except RuntimeError as e:
        raise HTTPException(400, str(e))
    return repo.add_critique(content_id, result)


@router.get("/{content_id}/critiques")
def list_critiques(content_id: str):
    return repo.list_critiques(content_id)


@router.post("/critiques/{critique_id}/comment")
def comment_on_critique(critique_id: str, payload: CommentRequest):
    result = repo.add_critique_comment(critique_id, payload.comment)
    if not result:
        raise HTTPException(404, "Critique not found")
    return result
