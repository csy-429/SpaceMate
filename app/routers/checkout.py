"""
개발자 B 담당 — 통합결제 API.

[신규] 장바구니에 상품이 담긴 경우에만 진입하는 통합결제.
실제 결제 연동 없는 목업 — order_id 발급 + "결제 완료" 응답만 반환.
분리정산(호스트 수수료 10%) 안내는 프론트에서 텍스트로만 표시 (백엔드는 total_price만 내려줌).
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.data import repository
from app.models.schemas import Order

router = APIRouter()


class CheckoutRequest(BaseModel):
    session_id: str


@router.post("", response_model=Order)
def checkout(payload: CheckoutRequest):
    order = repository.create_order(payload.session_id)
    return order
