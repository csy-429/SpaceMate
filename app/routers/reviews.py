"""
개발자 A 담당 — 후기 조회 + AI 그룹핑 API.

일반 사용자용 (router, main.py에서 prefix="/reviews"):
  GET /reviews/{space_id}          — 후기 원문 리스트 (그룹핑 전 폴백용, PRD NFR 8.2)
  GET /reviews/{space_id}/groups   — 승인(approved)된 그룹만 반환 (FR-01/FR-03)

관리자용 (admin_router, main.py에서 prefix="/admin"):
  POST /admin/generate-groups — 그룹핑 실행 (관리자 트리거, NFR 7.1). PRD FR-02에 맞춰
  승인 절차 없이 생성 즉시 approved로 저장한다(화면도 안 만들기로 팀 합의).
  실패/타임아웃/파싱오류 시: 캐시(cache/review_groups_{space_id}.json)가 있으면 캐시 사용,
  없으면 원문 그대로 노출 (NFR 8.2 폴백 체인).
  이미 승인된 그룹이 있으면 LLM을 다시 호출하지 않고 기존 결과를 그대로 반환한다
  (토큰 비용 절감, NFR 8.3 "관리자 배치성으로 제한"). 리뷰가 늘었거나 라벨을 바꿔서
  다시 돌려야 하면 body에 force=true를 넣어서 명시적으로 재생성한다.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.data import repository
from app.services.review_grouping import generate_review_groups, save_groups_cache, load_groups_cache

router = APIRouter()
admin_router = APIRouter()


@router.get("/{space_id}")
def list_reviews(space_id: str):
    # spaces.py의 get_space_detail과 동일 패턴: 존재하지 않는 공간은 404,
    # 존재하지만 후기가 0건인 공간은 빈 리스트(둘을 구분해야 프론트가 에러/빈상태를 다르게 처리 가능)
    if repository.get_space(space_id) is None:
        raise HTTPException(status_code=404, detail="space not found")
    return repository.get_reviews(space_id)


@router.get("/{space_id}/groups")
def list_review_groups(space_id: str):
    if repository.get_space(space_id) is None:
        raise HTTPException(status_code=404, detail="space not found")
    return repository.get_review_groups(space_id, status="approved")


class GenerateGroupsRequest(BaseModel):
    space_id: str
    force: bool = False  # true면 기존 승인된 그룹이 있어도 LLM을 다시 호출해 재생성


@admin_router.post("/generate-groups")
def generate_groups(payload: GenerateGroupsRequest):
    space_id = payload.space_id
    reviews = repository.get_reviews(space_id)
    if not reviews:
        raise HTTPException(status_code=404, detail="해당 공간에 후기가 없습니다.")

    if not payload.force:
        existing = repository.get_review_groups(space_id, status="approved")
        if existing:
            # 이미 그룹이 있으면 재호출 없이 그대로 반환 (토큰 비용 절감)
            return {"source": "existing", "groups": existing}

    try:
        groups = generate_review_groups(space_id, reviews)
        if not groups:
            raise RuntimeError("LLM이 유효한 그룹을 하나도 반환하지 않음")
        repository.replace_review_groups(space_id, groups)
        save_groups_cache(space_id, groups)  # 발표 당일 라이브 호출 실패 대비 스냅샷
        return {"source": "llm", "groups": groups}
    except Exception:
        # NFR 8.2: 1차 폴백 = 캐시된 이전 결과, 캐시도 없으면 2차 폴백 = 원문 그대로 노출
        cached = load_groups_cache(space_id)
        if cached:
            repository.replace_review_groups(space_id, cached)
            return {"source": "cache", "groups": cached}
        return {"source": "fallback", "reviews": reviews}
