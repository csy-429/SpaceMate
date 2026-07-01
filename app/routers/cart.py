"""
개발자 B 담당 — 장바구니 API.

[신규] 보완상품(또는 이미 확정된 예약)을 담을 때만 진입하는 화면의 백엔드.
POST   /cart                       — 아이템 담기
GET    /cart/{session_id}          — 장바구니 조회
DELETE /cart/{session_id}/{item_id} — 아이템 제거
"""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.data import repository
from app.models.schemas import CartEntry

router = APIRouter()


class AddCartRequest(BaseModel):
    session_id: str
    item_type: Literal["space", "product"]
    ref_id: str
    quantity: int = 1


@router.post("", response_model=CartEntry)
def add_to_cart(payload: AddCartRequest):
    entry = CartEntry(
        item_type=payload.item_type,
        ref_id=payload.ref_id,
        quantity=payload.quantity,
    )
    repository.add_cart_item(payload.session_id, entry)
    return entry


@router.get("/{session_id}", response_model=list[CartEntry])
def get_cart(session_id: str):
    return repository.get_cart(session_id)


@router.delete("/{session_id}/{item_id}")
def delete_cart_item(session_id: str, item_id: str):
    repository.remove_cart_item(session_id, item_id)
    return {"status": "deleted", "item_id": item_id}
