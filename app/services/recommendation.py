"""
개발자 B 담당 — 보완상품 추천 서비스.

[신규] FR-07 폴백: LLM 호출 실패/미구현 시 space_type -> 기본 상품 매핑으로 즉시 대체.
LLM(페르소나 분류) 로직은 추후 이 파일에 추가하되, get_fallback_products()의
시그니처/반환 타입은 유지해서 라우터 쪽 코드가 안 바뀌게 한다.
"""

from app.data.seed import PRODUCTS
from app.models.schemas import Product

# space_type -> 추천 상품 id 목록 (하드코딩 폴백, FR-07)
FALLBACK_MAP: dict[str, list[str]] = {
    "회의실": ["pd03", "pd04"],
    "파티룸": ["pd01", "pd02", "pd04"],
    "공유주방": ["pd05", "pd03"],
}


def get_fallback_products(space_type: str) -> list[Product]:
    ids = FALLBACK_MAP.get(space_type, [])
    return [p for p in PRODUCTS if p.id in ids]
