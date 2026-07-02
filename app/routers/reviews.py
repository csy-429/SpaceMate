"""
개발자 A 담당 — 후기 조회 + AI 그룹핑 API.

일반 사용자용 (router, main.py에서 prefix="/reviews"):
  GET /reviews/{space_id}          — 후기 원문 리스트 (그룹핑 전 폴백용, PRD NFR 8.2)
  GET /reviews/{space_id}/groups   — 승인(approved)된 그룹만 반환 (FR-01/FR-03)

관리자용 (admin_router, main.py에서 prefix="/admin"):
  POST /admin/generate-groups              — LLM 그룹핑 실행, 실패 시 원문 폴백 (FR-01, NFR 8.2)
  GET  /admin/review-groups                — pending 목록 (FR-02)
  POST /admin/review-groups/{id}/approve
  POST /admin/review-groups/{id}/reject
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.data import repository
from app.services.review_grouping import generate_review_groups

router = APIRouter()
admin_router = APIRouter()


@router.get("/{space_id}")
def list_reviews(space_id: str):
    return repository.get_reviews(space_id)


@router.get("/{space_id}/groups")
def list_review_groups(space_id: str):
    return repository.get_review_groups(space_id, status="approved")


class GenerateGroupsRequest(BaseModel):
    space_id: str


@admin_router.post("/generate-groups")
def generate_groups(payload: GenerateGroupsRequest):
    reviews = repository.get_reviews(payload.space_id)
    if not reviews:
        raise HTTPException(status_code=404, detail="해당 공간에 후기가 없습니다.")
    try:
        groups = generate_review_groups(payload.space_id, reviews)
        for group in groups:
            repository.add_review_group(group)
        return {"source": "llm", "groups": groups}
    except Exception:
        # NFR 8.2: AI 실패/타임아웃/파싱오류 시 원문 그대로 노출 (그룹핑 생략)
        return {"source": "fallback", "reviews": reviews}


@admin_router.get("/review-groups")
def pending_review_groups():
    return repository.list_pending_groups()


@admin_router.post("/review-groups/{group_id}/approve")
def approve_review_group(group_id: str):
    group = repository.update_review_group_status(group_id, "approved")
    if not group:
        raise HTTPException(status_code=404, detail="그룹을 찾을 수 없습니다.")
    return group


@admin_router.post("/review-groups/{group_id}/reject")
def reject_review_group(group_id: str):
    group = repository.update_review_group_status(group_id, "rejected")
    if not group:
        raise HTTPException(status_code=404, detail="그룹을 찾을 수 없습니다.")
    return group
