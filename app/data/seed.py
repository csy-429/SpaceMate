"""
SpaceMate 시드 데이터.
DB 없이 하드코딩 + 메모리 상태로 운영하기로 팀 합의된 사항 (NFR 7.3 참고).
서버 재시작 시 이 데이터로 초기화된다.

[갱신] Review에 rating/created_at 필수 필드가 추가됨에 따라:
- sp03(시연용 공간, "[합정역1분거리파티룸] 스페이스T" 실 리스팅과 동일)은 하드코딩 대신
  A가 크롤링한 실제 후기 CSV(app/data/spacecloud_reviews.csv)에서 로드한다.
- 나머지 공간(sp01/02/04/05/06)은 기존 하드코딩 placeholder 후기를 유지하되
  rating/created_at 값을 채웠다 (임의값, 실제 크롤링 대상 아님).
"""

from datetime import date

from app.data.reviews_loader import load_crawled_reviews
from app.models.schemas import Space, Review, Product

SPACES: list[Space] = [
    Space(
        id="sp01", name="강남 스퀘어 회의실 A", type="회의실", region="강남구",
        capacity=8, price_per_hour_weekday=15000, price_per_hour_weekend=20000,
        facilities=["화이트보드", "빔프로젝터", "와이파이"], popularity=92,
        image_url="https://placehold.co/400x300?text=Space+A",
    ),
    Space(
        id="sp02", name="서초 컨퍼런스룸", type="회의실", region="서초구",
        capacity=12, price_per_hour_weekday=20000, price_per_hour_weekend=25000,
        facilities=["화상회의 장비", "화이트보드", "커피머신"], popularity=78,
        image_url="https://placehold.co/400x300?text=Space+B",
    ),
    # sp03 = 시연용 기준 공간. 실제 리스팅 "[합정역1분거리파티룸] 스페이스T"
    # (https://www.spacecloud.kr/space/25288) 값 그대로 맞춤 — 가격/인원은 기존 값 유지,
    # 이름/지역/대표이미지를 실제 리스팅 메타데이터로 교체 (2026-07-01).
    Space(
        id="sp03", name="[합정역1분거리파티룸] 스페이스T", type="파티룸", region="합정",
        capacity=10, price_per_hour_weekday=13000, price_per_hour_weekend=18000,
        facilities=["빔프로젝터", "블루투스 스피커", "미러볼"], popularity=95,
        image_url="https://formeqly4682.edge.naverncp.com/service/168164444_919f3ecb8d32bb46a2bd5a96c07a9098.jpeg?type=m&w=900&h=900&autorotate=true&quality=90",
        price_package=100000, package_hours="18:00~익일 08:00",
        base_capacity=6, extra_person_fee=10000,
    ),
    Space(
        id="sp04", name="성수동 루프탑 파티룸", type="파티룸", region="성수동",
        capacity=20, price_per_hour_weekday=35000, price_per_hour_weekend=50000,
        facilities=["루프탑", "블루투스 스피커", "테이블세팅"], popularity=88,
        image_url="https://placehold.co/400x300?text=Space+D",
        price_package=110000, package_hours="18:00~익일 08:00",
    ),
    Space(
        id="sp05", name="마포 공유주방 키친랩", type="공유주방", region="마포구",
        capacity=6, price_per_hour_weekday=18000, price_per_hour_weekend=22000,
        facilities=["4구 인덕션", "오븐", "식기세트"], popularity=70,
        image_url="https://placehold.co/400x300?text=Space+E",
    ),
    Space(
        id="sp06", name="잠실 베이킹 스튜디오", type="공유주방", region="잠실",
        capacity=8, price_per_hour_weekday=22000, price_per_hour_weekend=28000,
        facilities=["오븐 2대", "냉장고", "식기세트", "앞치마 대여"], popularity=81,
        image_url="https://placehold.co/400x300?text=Space+F",
    ),
]

PRODUCTS: list[Product] = [
    Product(id="pd01", name="생일 케이크", price=35000, target_space_types=["파티룸"]),
    Product(id="pd02", name="풍선 데코 세트", price=15000, target_space_types=["파티룸"]),
    Product(id="pd03", name="다과 세트", price=20000, target_space_types=["회의실", "파티룸"]),
    Product(id="pd04", name="음향기기 대여", price=25000, target_space_types=["회의실", "파티룸"]),
    Product(id="pd05", name="베이킹 재료 키트", price=18000, target_space_types=["공유주방"]),
]

# sp01/02/04/05/06 하드코딩 placeholder 후기 (rating/created_at은 임의 채움값, 실제 크롤링 아님).
# sp03은 아래에서 CSV 실데이터로 대체하므로 여기 없음.
_PLACEHOLDER_REVIEWS: list[Review] = [
    # sp01
    Review(id="rv01", space_id="sp01", content="회의실이 방음이 잘 되어서 화상회의 하기 좋았어요.", rating=5, created_at=date(2026, 5, 1)),
    Review(id="rv02", space_id="sp01", content="지하철역에서 가까워서 접근성이 정말 좋습니다.", rating=5, created_at=date(2026, 5, 2)),
    Review(id="rv03", space_id="sp01", content="화이트보드랑 빔프로젝터 상태가 깨끗하고 잘 작동했어요.", rating=5, created_at=date(2026, 5, 3)),
    Review(id="rv04", space_id="sp01", content="청결 상태가 매우 좋았고 정리정돈이 잘 되어 있었어요.", rating=5, created_at=date(2026, 5, 4)),
    Review(id="rv05", space_id="sp01", content="주차 공간이 협소해서 조금 불편했습니다.", rating=3, created_at=date(2026, 5, 5)),
    # sp02
    Review(id="rv06", space_id="sp02", content="화상회의 장비가 최신이라 원격 미팅하기 편했어요.", rating=5, created_at=date(2026, 5, 6)),
    Review(id="rv07", space_id="sp02", content="방음이 잘 안 돼서 옆방 소리가 조금 들렸어요.", rating=3, created_at=date(2026, 5, 7)),
    Review(id="rv08", space_id="sp02", content="역에서 도보 3분이라 접근성이 최고예요.", rating=5, created_at=date(2026, 5, 8)),
    Review(id="rv09", space_id="sp02", content="커피머신이 있어서 좋았고 청결하게 관리되고 있었어요.", rating=5, created_at=date(2026, 5, 9)),
    Review(id="rv10", space_id="sp02", content="테이블 배치가 넓어서 여유롭게 회의할 수 있었습니다.", rating=4, created_at=date(2026, 5, 10)),
    # sp04
    Review(id="rv16", space_id="sp04", content="루프탑 뷰가 정말 예뻐서 사진 찍기 좋았어요.", rating=5, created_at=date(2026, 5, 11)),
    Review(id="rv17", space_id="sp04", content="스피커 음향 시설이 훌륭했습니다.", rating=5, created_at=date(2026, 5, 12)),
    Review(id="rv18", space_id="sp04", content="성수동이라 접근성은 괜찮은 편이에요.", rating=4, created_at=date(2026, 5, 13)),
    Review(id="rv19", space_id="sp04", content="청결 상태 최상, 테이블 세팅도 깔끔했어요.", rating=5, created_at=date(2026, 5, 14)),
    Review(id="rv20", space_id="sp04", content="여름엔 야외라 더울 수 있으니 참고하세요.", rating=3, created_at=date(2026, 5, 15)),
    # sp05
    Review(id="rv21", space_id="sp05", content="인덕션 화구가 4개라 여럿이 요리하기 편했어요.", rating=5, created_at=date(2026, 5, 16)),
    Review(id="rv22", space_id="sp05", content="주방이 매우 청결하게 관리되고 있었습니다.", rating=5, created_at=date(2026, 5, 17)),
    Review(id="rv23", space_id="sp05", content="마포 쪽이라 접근성이 준수한 편이에요.", rating=4, created_at=date(2026, 5, 18)),
    Review(id="rv24", space_id="sp05", content="오븐 예열이 오래 걸려서 시간 계획이 필요해요.", rating=3, created_at=date(2026, 5, 19)),
    Review(id="rv25", space_id="sp05", content="식기 세트가 잘 구비되어 있어 편리했어요.", rating=5, created_at=date(2026, 5, 20)),
    # sp06
    Review(id="rv26", space_id="sp06", content="오븐이 2대라 베이킹 클래스 하기 좋았습니다.", rating=5, created_at=date(2026, 5, 21)),
    Review(id="rv27", space_id="sp06", content="잠실역에서 가까워 접근성이 좋아요.", rating=5, created_at=date(2026, 5, 22)),
    Review(id="rv28", space_id="sp06", content="청결하고 앞치마까지 대여해줘서 편했어요.", rating=5, created_at=date(2026, 5, 23)),
    Review(id="rv29", space_id="sp06", content="냉장고 용량이 넉넉해서 재료 보관하기 좋았어요.", rating=4, created_at=date(2026, 5, 24)),
    Review(id="rv30", space_id="sp06", content="주말엔 예약이 꽉 차서 미리 예약해야 해요.", rating=4, created_at=date(2026, 5, 25)),
]

# sp03(시연용)은 A가 크롤링한 실제 후기 367건을 그대로 사용 (spacecloud_reviews.csv)
REVIEWS: list[Review] = _PLACEHOLDER_REVIEWS + load_crawled_reviews()
