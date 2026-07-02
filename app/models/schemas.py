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
    capacity: int               # 최대 수용 인원
    price_per_hour_weekday: int  # 평일 시간당 요금
    price_per_hour_weekend: int  # 주말/공휴일 시간당 요금
    facilities: list[str]
    popularity: int            # 베스트순 정렬용
    image_url: str
    price_package: int | None = None      # 올나잇 패키지 고정가 (미제공 공간은 None)
    package_hours: str | None = None      # 패키지 시간대 표시용, 예: "18:00~익일 08:00"
    base_capacity: int | None = None      # 기준 인원 (초과 시 인당 추가요금 발생, 없으면 초과요금 미적용)
    extra_person_fee: int = 0             # 기준 인원 초과 시 인당 추가요금


class Review(BaseModel):
    id: str
    space_id: str
    content: str
    author: str = "익명"
    rating: int
    created_at: date


class ReviewGroup(BaseModel):
    id: str
    space_id: str
    label: str                 # 예: "방음", "청결", "접근성"
    summary: str
    status: Literal["pending", "approved", "rejected"] = "pending"
    review_ids: list[str] = Field(default_factory=list)  # 요약 근거 원본 리뷰 id (관리자 승인 화면 원문 대조용)


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
    reservation_type: Literal["hourly", "package"] = "hourly"
    start_hour: int | None = None   # hourly 전용, 0~23
    hours: int | None = None        # hourly 전용, 최소 예약시간 이상
    guest_count: int = 1            # 예약 인원


class ReservationResult(BaseModel):
    reservation_id: str
    space_id: str
    date: date
    reservation_type: Literal["hourly", "package"]
    start_hour: int | None = None
    hours: int | None = None
    guest_count: int = 1
    total_price: int
    status: Literal["confirmed"] = "confirmed"


class Order(BaseModel):
    order_id: str
    session_id: str
    items: list[CartEntry]
    total_price: int
    status: Literal["completed"] = "completed"
