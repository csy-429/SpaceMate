"""
공간 검색·목록·상세 API (FR-08).
[참고] 원래 Developer A 담당 파일이나, 일정상 Developer B가 대신 구현.
       A가 나중에 FR-01/02(후기 그룹핑/승인)를 완성하면 이 파일은 수정 없이도
       자동으로 그룹 요약을 노출한다 — 지금은 승인된 그룹이 없으므로 원문 후기로
       폴백한다 (PRD US-01 AC-4: "AI 미작동 시 후기 원문이 그대로 표시된다").

GET /spaces          - 목록 (type/region/capacity/sort 쿼리 필터)
GET /spaces/{id}     - 상세 (공간 정보 + 후기(그룹 or 원문))
"""
from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from app.data import repository

router = APIRouter()


@router.get("")
def list_spaces(
    type: Literal["회의실", "파티룸", "공유주방"] | None = Query(
        None, description="공간 유형 필터"
    ),
    region: str | None = Query(None, description="지역 필터 (예: 강남구)"),
    capacity: int | None = Query(
        None, ge=1, description="최소 수용 인원 (이 값 이상인 공간만)"
    ),
    sort: Literal["price", "popularity"] | None = Query(
        None, description="정렬 기준: price(평일요금 오름차순) | popularity(인기 내림차순)"
    ),
):
    filters = {"type": type, "region": region, "capacity": capacity, "sort": sort}
    spaces = repository.list_spaces(filters)
    # 프론트 카드에 별점/리뷰수 표시용 — Space 스키마는 안 건드리고 응답에서만 덧붙임.
    enriched = [
        {**s.model_dump(), **repository.get_rating_summary(s.id)} for s in spaces
    ]
    return {"count": len(spaces), "spaces": enriched}


@router.get("/{space_id}")
def get_space_detail(space_id: str):
    space = repository.get_space(space_id)
    if space is None:
        raise HTTPException(status_code=404, detail="space not found")

    space_data = {**space.model_dump(), **repository.get_rating_summary(space_id)}

    # FR-02: 승인된(approved) 그룹만 노출. A가 아직 그룹을 안 만들었으면 빈 리스트.
    groups = repository.get_review_groups(space_id, status="approved")
    if groups:
        return {"space": space_data, "review_mode": "grouped", "review_groups": groups}

    # 폴백: 그룹이 없으면 원문 후기 그대로 (US-01 AC-4)
    reviews = repository.get_reviews(space_id)
    return {"space": space_data, "review_mode": "raw", "reviews": reviews}
