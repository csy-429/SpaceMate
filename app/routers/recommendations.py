"""
개발자 B 담당 — 보완상품 추천 API.

[신규] POST /recommendations
body: {space_type, capacity, time_slot}
LLM(페르소나 분류) 연동은 TODO. 지금은 API 키/네트워크 의존성이 없는
폴백 매핑(services/recommendation.py)을 우선 사용하도록 try/except로 구조만 잡아둠 —
나중에 LLM 로직을 try 블록 안에 채워 넣으면 응답 계약(response contract)은 그대로 유지됨.
"""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.recommendation import get_fallback_products

router = APIRouter()


class RecommendationRequest(BaseModel):
    space_type: Literal["회의실", "파티룸", "공유주방"]
    capacity: int
    time_slot: str | None = None


@router.post("")
def recommend_products(payload: RecommendationRequest):
    try:
        # TODO: LangChain + ChatGPT로 페르소나 분류 후 맞춤 추천.
        # 지금은 미구현 상태이므로 항상 폴백으로 빠짐 (FR-07).
        raise NotImplementedError("LLM 추천 미구현 — 폴백 매핑 사용")
    except Exception:
        products = get_fallback_products(payload.space_type)
        return {"source": "fallback", "products": products}
