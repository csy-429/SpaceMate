"""
개발자B 담당: 보완상품 추천 API.
[갱신] POST /recommendations
body: {space_type, capacity, time_slot}
LLM(LangChain + OpenAI GPT-4o-mini) 연동 완료. services/recommendation.py의
get_llm_recommended_products()를 우선 시도하고, 예외(키 없음/타임아웃/파싱 실패 등)
발생 시 get_fallback_products()로 즉시 대체한다 (FR-07, NFR 8.2 서비스 무중단).
"""
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.recommendation import get_fallback_products, get_llm_recommended_products

router = APIRouter()


class RecommendationRequest(BaseModel):
    space_type: Literal["회의실", "파티룸", "공유주방"]
    capacity: int
    time_slot: str | None = None


@router.post("")
def recommend_products(payload: RecommendationRequest):
    try:
        products = get_llm_recommended_products(
            payload.space_type, payload.capacity, payload.time_slot
        )
        return {"source": "llm", "products": products}
    except Exception:
        products = get_fallback_products(payload.space_type)
        return {"source": "fallback", "products": products}
