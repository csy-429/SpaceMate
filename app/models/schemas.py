"""
SpaceMate 공용 스키마 확정본.
이 파일은 공통 작업 단계에서 커밋된 이후 개발자 A/B가 임의로 수정하지 않는다.
필드 추가/변경이 필요하면 반드시 상대방과 먼저 상의할 것.
"""

from pydantic import BaseModel, Field
from typing import Literal
from datetime import date
import uuid


class Space(BaseModel):
    id: str
    name: str
    type: Literal["회의실", "파티룸", "공유주방"]
    region: str
    capacity: int
    price_per_hour_day: int    # 주간(09-18) 시간당 요금
    price_per_hour_night: int  # 야간(18-24) 시간당 요금
    facilities: list[str]
    popularity: int            # 베스트순 정렬용
    image_url: str


class Review(BaseModel):
    id: str
    space_id: str
    content: str
    author: str = "익명"


class ReviewGroup(BaseModel):
    id: str
    space_id: str
    label: str                 # 예: "방음", "청결", "접근성"
    summary: str
    status: Literal["pending", "approved", "rejected"] = "pending"


class Product(BaseModel):
    id: str
    name: str
    price: int
    target_space_types: list[str]  # 어떤 공간 유형에 추천할지


class CartItem(BaseModel):
    item_type: Literal["space", "product"]
    ref_id: str
    quantity: int = 1


class CartEntry(CartItem):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])


class ReservationRequest(BaseModel):
    space_id: str
    date: date
    time_slots: list[Literal["오전", "오후", "저녁"]]


class ReservationResult(BaseModel):
    reservation_id: str
    space_id: str
    date: date
    time_slots: list[str]
    total_price: int
    status: Literal["confirmed"] = "confirmed"


class Order(BaseModel):
    order_id: str
    session_id: str
    items: list[CartEntry]
    total_price: int
    status: Literal["completed"] = "completed"
