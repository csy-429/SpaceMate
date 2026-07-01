"""
개발자 B 담당 — 예약(시간 단위 / 올나잇 패키지) API.

[클론] GET /reservations/{space_id}/slots  — 요일별(평일/주말) 요금 + 패키지 여부 조회
[클론] POST /reservations                  — 즉시예약 확정 (공간만 예약 시 바로 결제완료 처리, 목업이므로 별도 결제 API 없이 confirmed 반환)

시연 공간(sp03, 스페이스T 참고 리스팅) 기준으로 단순화한 로직:
- 시간대(주간/야간) 구분 없음. 예약 날짜가 평일이면 평일요금, 토/일이면 주말요금 (공휴일 미반영).
- 기준인원(base_capacity) 초과 시 인당 extra_person_fee 추가. base_capacity 없는 공간은 초과요금 없음.

주의: 원래 기획서엔 슬롯 조회 경로가 `/spaces/{space_id}/slots`로 되어 있었으나,
그 라우터(spaces.py)는 개발자 A 담당 파일이라 임의로 건드리지 않기 위해
이 파일(reservations 라우터) 안에 `/reservations/{space_id}/slots`로 구현함.
프론트에서 호출 시 이 경로 기준으로 붙여야 함.
"""

from datetime import date as date_type

from fastapi import APIRouter, HTTPException

from app.data import repository
from app.models.schemas import ReservationRequest, ReservationResult

router = APIRouter()

MIN_HOURLY_HOURS = 2  # 시간 단위 예약 최소 시간 (참고 예시: 최소 2시간부터)


@router.get("/{space_id}/slots")
def get_slots(space_id: str, date: date_type):
    space = repository.get_space(space_id)
    if not space:
        raise HTTPException(status_code=404, detail="공간을 찾을 수 없습니다")

    is_weekend = date.weekday() >= 5  # 5=토, 6=일 (공휴일은 MVP 범위 밖)
    hourly_rate = space.price_per_hour_weekend if is_weekend else space.price_per_hour_weekday
    hourly_slots = [
        {"hour": hour, "price": hourly_rate, "available": True}  # MVP: 항상 예약 가능 처리
        for hour in range(24)
    ]

    package = None
    if space.price_package is not None:
        package = {
            "price": space.price_package,
            "time_range": space.package_hours,
            "available": True,
        }

    return {
        "space_id": space_id,
        "date": date,
        "is_weekend": is_weekend,
        "min_hours": MIN_HOURLY_HOURS,
        "capacity": space.capacity,
        "base_capacity": space.base_capacity,
        "extra_person_fee": space.extra_person_fee,
        "hourly_slots": hourly_slots,
        "package": package,
    }


@router.post("", response_model=ReservationResult)
def create_reservation(payload: ReservationRequest):
    if payload.reservation_type == "hourly":
        if payload.start_hour is None or payload.hours is None:
            raise HTTPException(
                status_code=400,
                detail="시간 단위 예약은 start_hour, hours가 필요합니다",
            )
        if not (0 <= payload.start_hour <= 23):
            raise HTTPException(status_code=400, detail="start_hour는 0~23 사이여야 합니다")
        if payload.hours < MIN_HOURLY_HOURS:
            raise HTTPException(
                status_code=400,
                detail=f"최소 예약 시간은 {MIN_HOURLY_HOURS}시간입니다",
            )

    # 최대 인원 초과는 에러로 막지 않고 조용히 상한선에서 clamp.
    # 프론트에서 인원 +버튼을 capacity에서 비활성화(회색 처리)하는 걸로 막는 게 기본이고,
    # 혹시 넘어온 값이 있어도 여기서 그냥 capacity로 잘라서 예약은 계속 진행되게 함.
    space = repository.get_space(payload.space_id)
    guest_count = payload.guest_count
    if space and guest_count > space.capacity:
        guest_count = space.capacity

    result = repository.create_reservation(
        space_id=payload.space_id,
        date_=payload.date,
        reservation_type=payload.reservation_type,
        start_hour=payload.start_hour,
        hours=payload.hours,
        guest_count=guest_count,
    )

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="예약할 수 없습니다 (공간 없음 또는 이 공간은 패키지 예약 미제공)",
        )

    # [클론] 공간만 예약하는 경우 장바구니를 거치지 않고 여기서 바로 결제 완료 처리.
    # 실제 결제 연동은 없는 목업이라 status="confirmed" 반환이 곧 "결제 완료"를 의미함.
    return result


@router.get("/{reservation_id}", response_model=ReservationResult)
def get_reservation(reservation_id: str):
    result = repository.get_reservation(reservation_id)
    if not result:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다")
    return result
