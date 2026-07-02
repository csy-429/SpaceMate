"""
개발자B 담당: 보완상품 추천 API.
[갱신] POST /recommendations
body: {space_type, capacity, time_slot, force}

캐싱 체인 (A의 review_grouping 캐시 패턴과 동일, 2026-07-02):
1) force가 아니고 메모리에 이미 성공한 결과 있으면 재호출 없이 그대로 반환 -> source: "existing"
2) 없으면 LLM 호출 시도 -> 성공하면 메모리+파일에 저장 -> source: "llm"
3) LLM 실패(키 없음/타임아웃/파싱오류) 시 파일 캐시 확인(서버 재시작으로 메모리 비어있을 때 대비)
   -> 있으면 source: "cache"
4) 파일 캐시도 없으면 하드코딩 폴백 -> source: "fallback" (FR-07, NFR 8.2)
"""
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.recommendation import (
    get_cached_products,
    get_fallback_products,
    get_llm_recommended_products,
    load_recommendation_cache,
    save_recommendation_cache,
    set_cached_products,
)

router = APIRouter()


class RecommendationRequest(BaseModel):
    space_type: Literal["회의실", "파티룸", "공유주방"]
    capacity: int
    time_slot: str | None = None
    force: bool = False  # true면 캐시 무시하고 LLM 재호출


@router.post("")
def recommend_products(payload: RecommendationRequest):
    if not payload.force:
        cached = get_cached_products(payload.space_type)
        if cached:
            return {"source": "existing", "products": cached}

    try:
        products = get_llm_recommended_products(
            payload.space_type, payload.capacity, payload.time_slot
        )
        set_cached_products(payload.space_type, products)
        save_recommendation_cache(payload.space_type, products)
        return {"source": "llm", "products": products}
    except Exception:
        file_cached = load_recommendation_cache(payload.space_type)
        if file_cached:
            set_cached_products(payload.space_type, file_cached)
            return {"source": "cache", "products": file_cached}
        products = get_fallback_products(payload.space_type)
        return {"source": "fallback", "products": products}
