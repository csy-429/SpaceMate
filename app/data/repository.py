"""
데이터 접근 레이어 — 지금은 전부 인메모리(dict/list) 기반.
나중에 DB로 바꾸더라도 이 파일의 함수 시그니처만 유지하면
라우터/서비스 코드는 그대로 사용 가능하게 설계.

주의: 서버 재시작하면 _review_groups / _cart / _reservations / _orders는 초기화됨.
(하드코딩+메모리 방식으로 팀 합의된 사항, NFR 7.3)
"""

import uuid
from datetime import date

from app.models.schemas import (
    Space, Review, ReviewGroup, Product,
    CartEntry, ReservationResult, Order,
)
from app.data.seed import SPACES, PRODUCTS, REVIEWS

# ---- 런타임 상태 (메모리) ----
_review_groups: list[ReviewGroup] = []            # AI 생성 그룹, 최초엔 비어있음
_cart: dict[str, list[CartEntry]] = {}             # session_id -> items
_reservations: dict[str, ReservationResult] = {}   # reservation_id -> result
_orders: dict[str, Order] = {}                     # order_id -> order


# ---- Space [클론] ----
def list_spaces(filters: dict) -> list[Space]:
    result = SPACES
    if filters.get("type"):
        result = [s for s in result if s.type == filters["type"]]
    if filters.get("region"):
        result = [s for s in result if s.region == filters["region"]]
    if filters.get("capacity"):
        result = [s for s in result if s.capacity >= filters["capacity"]]

    sort_by = filters.get("sort")
    if sort_by == "price":
        result = sorted(result, key=lambda s: s.price_per_hour_weekday)
    elif sort_by == "popularity":
        result = sorted(result, key=lambda s: -s.popularity)
    return result


def get_space(space_id: str) -> Space | None:
    return next((s for s in SPACES if s.id == space_id), None)


# ---- Review / ReviewGroup [클론 + 신규] ----
def get_reviews(space_id: str) -> list[Review]:
    return [r for r in REVIEWS if r.space_id == space_id]


def get_review_groups(space_id: str, status: str = "approved") -> list[ReviewGroup]:
    return [g for g in _review_groups if g.space_id == space_id and g.status == status]


def add_review_group(group: ReviewGroup) -> None:
    _review_groups.append(group)


def update_review_group_status(group_id: str, status: str) -> ReviewGroup | None:
    for g in _review_groups:
        if g.id == group_id:
            g.status = status
            return g
    return None


def list_pending_groups() -> list[ReviewGroup]:
    return [g for g in _review_groups if g.status == "pending"]


# ---- Reservation [클론] ----
def calculate_hourly_price(space: Space, date_: date, hours: int) -> int:
    """예약 날짜가 평일이면 평일요금, 토/일이면 주말요금 (공휴일은 MVP 범위 밖, 단순화).
    시간대(주간/야간) 구분은 없음 — 해당 날짜 요금 x 시간수."""
    is_weekend = date_.weekday() >= 5  # 5=토, 6=일
    rate = space.price_per_hour_weekend if is_weekend else space.price_per_hour_weekday
    return rate * hours


def calculate_extra_guest_fee(space: Space, guest_count: int) -> int:
    """기준인원(base_capacity) 초과 시 인당 extra_person_fee 추가. base_capacity 없으면 0."""
    if space.base_capacity is None or guest_count <= space.base_capacity:
        return 0
    return (guest_count - space.base_capacity) * space.extra_person_fee


def create_reservation(
    space_id: str,
    date_: date,
    reservation_type: str,
    start_hour: int | None = None,
    hours: int | None = None,
    guest_count: int = 1,
) -> ReservationResult | None:
    space = get_space(space_id)
    if not space:
        return None

    if reservation_type == "package":
        if space.price_package is None:
            return None  # 이 공간은 패키지 예약 미제공
        price = space.price_package
    else:
        if start_hour is None or hours is None:
            return None
        price = calculate_hourly_price(space, date_, hours)

    price += calculate_extra_guest_fee(space, guest_count)

    result = ReservationResult(
        reservation_id=str(uuid.uuid4())[:8],
        space_id=space_id,
        date=date_,
        reservation_type=reservation_type,
        start_hour=start_hour,
        hours=hours,
        guest_count=guest_count,
        total_price=price,
    )
    _reservations[result.reservation_id] = result
    return result


def get_reservation(reservation_id: str) -> ReservationResult | None:
    return _reservations.get(reservation_id)


# ---- Cart [신규] ----
def get_cart(session_id: str) -> list[CartEntry]:
    return _cart.get(session_id, [])


def add_cart_item(session_id: str, item: CartEntry) -> None:
    _cart.setdefault(session_id, []).append(item)


def remove_cart_item(session_id: str, item_id: str) -> None:
    _cart[session_id] = [i for i in _cart.get(session_id, []) if i.id != item_id]


# ---- Checkout [신규] ----
def create_order(session_id: str) -> Order:
    items = get_cart(session_id)
    total = 0
    for item in items:
        if item.item_type == "product":
            product = next((p for p in PRODUCTS if p.id == item.ref_id), None)
            if product:
                total += product.price * item.quantity
        elif item.item_type == "space":
            reservation = _reservations.get(item.ref_id)
            if reservation:
                total += reservation.total_price

    order = Order(
        order_id=str(uuid.uuid4())[:8],
        session_id=session_id,
        items=items,
        total_price=total,
    )
    _orders[order.order_id] = order
    _cart[session_id] = []  # 결제 후 장바구니 비우기
    return order


# ---- Product [신규] ----
def list_products(space_type: str | None = None) -> list[Product]:
    if space_type:
        return [p for p in PRODUCTS if space_type in p.target_space_types]
    return PRODUCTS
