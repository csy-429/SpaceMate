"""
SpaceMate 시드 데이터.
DB 없이 하드코딩 + 메모리 상태로 운영하기로 팀 합의된 사항 (NFR 7.3 참고).
서버 재시작 시 이 데이터로 초기화된다.
"""

from app.models.schemas import Space, Review, Product

SPACES: list[Space] = [
    Space(
        id="sp01", name="강남 스퀘어 회의실 A", type="회의실", region="강남구",
        capacity=8, price_per_hour_day=15000, price_per_hour_night=20000,
        facilities=["화이트보드", "빔프로젝터", "와이파이"], popularity=92,
        image_url="https://placehold.co/400x300?text=Space+A",
    ),
    Space(
        id="sp02", name="서초 컨퍼런스룸", type="회의실", region="서초구",
        capacity=12, price_per_hour_day=20000, price_per_hour_night=25000,
        facilities=["화상회의 장비", "화이트보드", "커피머신"], popularity=78,
        image_url="https://placehold.co/400x300?text=Space+B",
    ),
    Space(
        id="sp03", name="홍대 파티룸 문라이트", type="파티룸", region="홍대",
        capacity=15, price_per_hour_day=30000, price_per_hour_night=45000,
        facilities=["빔프로젝터", "블루투스 스피커", "미러볼"], popularity=95,
        image_url="https://placehold.co/400x300?text=Space+C",
    ),
    Space(
        id="sp04", name="성수동 루프탑 파티룸", type="파티룸", region="성수동",
        capacity=20, price_per_hour_day=35000, price_per_hour_night=50000,
        facilities=["루프탑", "블루투스 스피커", "테이블세팅"], popularity=88,
        image_url="https://placehold.co/400x300?text=Space+D",
    ),
    Space(
        id="sp05", name="마포 공유주방 키친랩", type="공유주방", region="마포구",
        capacity=6, price_per_hour_day=18000, price_per_hour_night=22000,
        facilities=["4구 인덕션", "오븐", "식기세트"], popularity=70,
        image_url="https://placehold.co/400x300?text=Space+E",
    ),
    Space(
        id="sp06", name="잠실 베이킹 스튜디오", type="공유주방", region="잠실",
        capacity=8, price_per_hour_day=22000, price_per_hour_night=28000,
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

REVIEWS: list[Review] = [
    # sp01
    Review(id="rv01", space_id="sp01", content="회의실이 방음이 잘 되어서 화상회의 하기 좋았어요."),
    Review(id="rv02", space_id="sp01", content="지하철역에서 가까워서 접근성이 정말 좋습니다."),
    Review(id="rv03", space_id="sp01", content="화이트보드랑 빔프로젝터 상태가 깨끗하고 잘 작동했어요."),
    Review(id="rv04", space_id="sp01", content="청결 상태가 매우 좋았고 정리정돈이 잘 되어 있었어요."),
    Review(id="rv05", space_id="sp01", content="주차 공간이 협소해서 조금 불편했습니다."),
    # sp02
    Review(id="rv06", space_id="sp02", content="화상회의 장비가 최신이라 원격 미팅하기 편했어요."),
    Review(id="rv07", space_id="sp02", content="방음이 잘 안 돼서 옆방 소리가 조금 들렸어요."),
    Review(id="rv08", space_id="sp02", content="역에서 도보 3분이라 접근성이 최고예요."),
    Review(id="rv09", space_id="sp02", content="커피머신이 있어서 좋았고 청결하게 관리되고 있었어요."),
    Review(id="rv10", space_id="sp02", content="테이블 배치가 넓어서 여유롭게 회의할 수 있었습니다."),
    # sp03
    Review(id="rv11", space_id="sp03", content="미러볼이랑 조명이 파티 분위기 내기 딱 좋았어요."),
    Review(id="rv12", space_id="sp03", content="스피커 음질이 좋아서 노래 틀기 좋았습니다."),
    Review(id="rv13", space_id="sp03", content="위치가 홍대 중심이라 접근성이 뛰어나요."),
    Review(id="rv14", space_id="sp03", content="청소 상태가 깔끔해서 기분 좋게 이용했어요."),
    Review(id="rv15", space_id="sp03", content="화장실이 좁아서 인원 많을 땐 조금 불편했어요."),
    # sp04
    Review(id="rv16", space_id="sp04", content="루프탑 뷰가 정말 예뻐서 사진 찍기 좋았어요."),
    Review(id="rv17", space_id="sp04", content="스피커 음향 시설이 훌륭했습니다."),
    Review(id="rv18", space_id="sp04", content="성수동이라 접근성은 괜찮은 편이에요."),
    Review(id="rv19", space_id="sp04", content="청결 상태 최상, 테이블 세팅도 깔끔했어요."),
    Review(id="rv20", space_id="sp04", content="여름엔 야외라 더울 수 있으니 참고하세요."),
    # sp05
    Review(id="rv21", space_id="sp05", content="인덕션 화구가 4개라 여럿이 요리하기 편했어요."),
    Review(id="rv22", space_id="sp05", content="주방이 매우 청결하게 관리되고 있었습니다."),
    Review(id="rv23", space_id="sp05", content="마포 쪽이라 접근성이 준수한 편이에요."),
    Review(id="rv24", space_id="sp05", content="오븐 예열이 오래 걸려서 시간 계획이 필요해요."),
    Review(id="rv25", space_id="sp05", content="식기 세트가 잘 구비되어 있어 편리했어요."),
    # sp06
    Review(id="rv26", space_id="sp06", content="오븐이 2대라 베이킹 클래스 하기 좋았습니다."),
    Review(id="rv27", space_id="sp06", content="잠실역에서 가까워 접근성이 좋아요."),
    Review(id="rv28", space_id="sp06", content="청결하고 앞치마까지 대여해줘서 편했어요."),
    Review(id="rv29", space_id="sp06", content="냉장고 용량이 넉넉해서 재료 보관하기 좋았어요."),
    Review(id="rv30", space_id="sp06", content="주말엔 예약이 꽉 차서 미리 예약해야 해요."),
]
