from fastapi import APIRouter, HTTPException

from format_modules import list_formats, get_format, FORMAT_MODULES
from platform_modules import list_platforms, get_platform
from knowledge_panel import get_knowledge_panel
from strategy_questions import get_questions

router = APIRouter(prefix="/api/meta", tags=["meta"])


@router.get("/formats")
def formats():
    return list_formats()


@router.get("/formats/{format_id}")
def format_detail(format_id: str):
    fmt = get_format(format_id)
    if not fmt:
        raise HTTPException(404, "Format not found")
    return fmt


@router.get("/platforms")
def platforms():
    return list_platforms()


@router.get("/platforms/{platform_id}")
def platform_detail(platform_id: str):
    plat = get_platform(platform_id)
    if not plat:
        raise HTTPException(404, "Platform not found")
    return plat


@router.get("/knowledge-panel")
def knowledge_panel():
    return get_knowledge_panel()


@router.get("/strategy-questions")
def strategy_questions():
    return get_questions()
