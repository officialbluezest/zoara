from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

import repo
from services import research as research_service

router = APIRouter(prefix="/api/brands/{brand_id}/research", tags=["research"])


class StartResearch(BaseModel):
    count: Optional[int] = 30


class IdeaStatusUpdate(BaseModel):
    status: str  # approved | rejected | tweaked
    tweak_comment: Optional[str] = ""


def _run_research_job(brand_id: str, job_id: str, count: int):
    try:
        brand = repo.get_brand(brand_id)
        competitors = repo.list_competitors(brand_id)
        inspo = repo.list_inspo(brand_id)
        brand["_competitor_summaries"] = [c["extracted_summary"] for c in competitors if c.get("extracted_summary")]
        brand["_inspo_patterns"] = [i["extracted_pattern"] for i in inspo if i.get("extracted_pattern")]

        raw_hits = research_service.run_live_search(brand)
        ideas = research_service.synthesize_ideas(brand, raw_hits, count=count)
        if isinstance(ideas, dict) and "ideas" in ideas:
            ideas = ideas["ideas"]
        repo.add_research_ideas(brand_id, job_id, ideas)
        repo.complete_research_job(job_id)
    except Exception as e:
        repo.complete_research_job(job_id, error=str(e))


@router.post("/start")
def start_research(brand_id: str, payload: StartResearch, background_tasks: BackgroundTasks):
    if not repo.get_brand(brand_id):
        raise HTTPException(404, "Brand not found")
    job_id = repo.create_research_job(brand_id, payload.count)
    background_tasks.add_task(_run_research_job, brand_id, job_id, payload.count)
    return {"job_id": job_id, "status": "running",
            "message": "Research is running in the background - feel free to switch tabs, this will keep going."}


@router.get("/status/{job_id}")
def research_status(brand_id: str, job_id: str):
    job = repo.get_research_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@router.get("/ideas")
def list_ideas(brand_id: str, status: Optional[str] = None):
    return repo.list_research_ideas(brand_id, status)


@router.patch("/ideas/{idea_id}")
def update_idea(brand_id: str, idea_id: str, payload: IdeaStatusUpdate):
    if payload.status not in ("approved", "rejected", "tweaked", "pending"):
        raise HTTPException(400, "invalid status")
    idea = repo.update_research_idea_status(idea_id, payload.status, payload.tweak_comment or "")
    if not idea:
        raise HTTPException(404, "Idea not found")
    return idea
