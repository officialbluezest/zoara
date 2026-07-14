from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, Dict, List

import repo
from services.doc_parser import parse_strategy_doc
from services.scraper import read_link
from services import ai_client

router = APIRouter(prefix="/api/brands", tags=["brands"])


class CreateBrand(BaseModel):
    name: str


class UpdateBrand(BaseModel):
    name: Optional[str] = None
    strategy_answers: Optional[Dict[str, Any]] = None
    formats: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    goals: Optional[Dict[str, Any]] = None
    build_specs: Optional[Dict[str, Any]] = None
    creative_angles: Optional[Dict[str, Any]] = None


class AddCompetitor(BaseModel):
    url: str
    label: Optional[str] = ""


@router.post("")
def create_brand(payload: CreateBrand):
    return repo.create_brand(payload.name)


@router.get("")
def list_brands():
    return repo.list_brands()


@router.get("/{brand_id}")
def get_brand(brand_id: str):
    brand = repo.get_brand(brand_id)
    if not brand:
        raise HTTPException(404, "Brand not found")
    return brand


@router.patch("/{brand_id}")
def update_brand(brand_id: str, payload: UpdateBrand):
    fields = {k: v for k, v in payload.model_dump().items() if v is not None}
    brand = repo.update_brand(brand_id, fields)
    if not brand:
        raise HTTPException(404, "Brand not found")
    return brand


@router.delete("/{brand_id}")
def delete_brand(brand_id: str):
    repo.delete_brand(brand_id)
    return {"ok": True}


@router.post("/{brand_id}/strategy-doc")
async def upload_strategy_doc(brand_id: str, file: UploadFile = File(...)):
    brand = repo.get_brand(brand_id)
    if not brand:
        raise HTTPException(404, "Brand not found")
    content = await file.read()
    try:
        text = parse_strategy_doc(file.filename, content)
    except ValueError as e:
        raise HTTPException(400, str(e))

    if not text.strip():
        raise HTTPException(400, "Could not extract any text from that document.")

    # Read it like a strategist would: ask Claude to fill the strategy
    # question fields directly from the document instead of making the
    # user re-answer everything by hand.
    from strategy_questions import get_questions
    questions = get_questions()
    q_list = "\n".join(f"- {q['id']}: {q['question']}" for q in questions)
    system = ("You are a senior brand strategist reading a client's strategy document "
               "to extract the answers to a discovery questionnaire. Only use what is "
               "actually supported by the document - if something isn't covered, use an "
               "empty string for that field rather than inventing an answer.")
    user = f"""
STRATEGY DOCUMENT TEXT:
{text[:12000]}

QUESTIONNAIRE FIELDS TO FILL:
{q_list}

Return a JSON object keyed by each field id above, with your best extracted
answer (or "" if genuinely not covered in the document).
"""
    try:
        extracted = ai_client.ask_json(system, user, max_tokens=2000)
    except RuntimeError:
        extracted = {}

    brand = repo.update_brand(brand_id, {
        "strategy_doc_text": text,
        "strategy_doc_filename": file.filename,
        "strategy_answers": {**(brand.get("strategy_answers") or {}), **{k: v for k, v in extracted.items() if v}},
    })
    return brand


@router.post("/{brand_id}/competitors")
def add_competitor(brand_id: str, payload: AddCompetitor):
    if not repo.get_brand(brand_id):
        raise HTTPException(404, "Brand not found")
    comp = repo.add_competitor(brand_id, payload.url, payload.label)
    result = read_link(payload.url)
    if result.get("source") == "error":
        repo.update_competitor(comp["id"], "", status="failed")
        return {**comp, "extracted_summary": "", "status": "failed", "error": result["error"]}

    text_blob = result.get("body_text") or result.get("meta_description") or result.get("title", "")
    try:
        system = "You are a brand strategist summarizing a competitor's positioning from their website/social content for competitive-context purposes."
        user = f"Competitor URL: {payload.url}\nRaw page content:\n{text_blob[:5000]}\n\nSummarize in 3-4 sentences: their apparent positioning, tone, and what they emphasize."
        summary = ai_client.ask(system, user, max_tokens=300)
    except RuntimeError:
        summary = text_blob[:400]

    return repo.update_competitor(comp["id"], summary)


@router.get("/{brand_id}/competitors")
def list_competitors(brand_id: str):
    return repo.list_competitors(brand_id)


@router.get("/{brand_id}/completeness")
def check_completeness(brand_id: str):
    """
    Powers the 'free tab navigation, but final submit needs the
    compulsory fields' requirement. Frontend calls this before allowing
    the user past the final submit step.
    """
    brand = repo.get_brand(brand_id)
    if not brand:
        raise HTTPException(404, "Brand not found")

    missing = []
    if not brand.get("name"):
        missing.append("Brand name")
    if not brand.get("formats"):
        missing.append("At least one content format")
    if not brand.get("platforms"):
        missing.append("At least one platform")

    strategy = brand.get("strategy_answers") or {}
    has_doc = bool(brand.get("strategy_doc_text"))
    required_strategy_fields = ["offer", "transformation", "anti_audience", "business_goal"]
    if not has_doc:
        for f in required_strategy_fields:
            if not strategy.get(f):
                missing.append(f"Strategy answer: {f}")
    else:
        for f in required_strategy_fields:
            if not strategy.get(f):
                missing.append(f"Strategy field not found in doc, needs manual answer: {f}")

    goals = brand.get("goals") or {}
    if not goals.get("primary_goal"):
        missing.append("Primary content goal")

    build_specs = brand.get("build_specs") or {}
    if not build_specs:
        missing.append("Build/length specs for at least one format")

    return {"complete": len(missing) == 0, "missing": missing}
