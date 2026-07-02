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
        facilities=["화이트보드", "빔프로젝터", "와이파이"],
        popularity=92,
        image_url="images/회의실1.jpg",
        description="강남역 인근에 위치한 실용적인 회의 공간입니다. 화이트보드와 빔프로젝터를 갖추고 있어 "
                    "소규모 미팅이나 스터디 모임에 적합합니다.",
    ),
    Space(
        id="sp02", name="서초 컨퍼런스룸", type="회의실", region="서초구",
        capacity=12, price_per_hour_weekday=20000, price_per_hour_weekend=25000,
        facilities=["화상회의 장비", "화이트보드", "커피머신"],
        popularity=78,
        image_url="images/회의실2.jpg",
        description="서초동 오피스 밀집 지역에 자리한 컨퍼런스룸입니다. 화상회의 장비가 구비되어 있어 "
                    "원격 미팅이나 세미나 진행에 편리합니다.",
    ),
    # sp03 = 시연용 기준 공간. 실제 리스팅 "[합정역1분거리파티룸] 스페이스T"
    # (https://www.spacecloud.kr/space/25288) 값 그대로 맞춤 — 가격/인원은 기존 값 유지,
    # 이름/지역/대표이미지를 실제 리스팅 메타데이터로 교체 (2026-07-01).
    Space(
        id="sp03", name="[합정역1분거리파티룸] 스페이스T", type="파티룸", region="합정",
        capacity=10, price_per_hour_weekday=13000, price_per_hour_weekend=18000,
        facilities=["빔프로젝터", "블루투스 스피커", "미러볼"],
        popularity=95,
        image_url="https://formeqly4682.edge.naverncp.com/service/168164444_919f3ecb8d32bb46a2bd5a96c07a9098.jpeg?type=m&w=900&h=900&autorotate=true&quality=90",
        price_package=100000, package_hours="18:00~익일 08:00",
        base_capacity=6, extra_person_fee=10000,
        # 실제 리스팅 "공간소개" 탭 원문 그대로 (2026-07-02, 사용자 제공 스크린샷 기준)
        description=(
            "스페이스T는 합정역 3번 출구 1분 거리에 위치해 있습니다.\n"
            "낮에는 햇살가득한 분위기에 밤에는 옥탑야경의 분위기로 매력이 있는 공간입니다.\n"
            "브라이덜 샤워, 영상 촬영, 스터디 모임 장소, 이벤트룸, 파티룸 등 다양한 용도로 이용하실 수있어요.\n"
            "낮에는 시간 단위로 필요한 만큼만 시간 선택해서 이용하고 밤에는 패키지로 알차게 놀기!\n"
            "\n"
            "심야 시간 예약 가능합니다 !\n"
            "올나잇 상품 예약 가능합니다 !\n"
            "\n"
            "※ 분실물은 책임지지 않습니다.\n"
            "\n"
            "※당일예약은 불가합니다!\n"
            "\n"
            "※퇴실시간은 예약 완료 10분전 입니다 예) 14시~17시 예약시 16시 50분 퇴실\n"
            "- 퇴실시간 (50분) 지연시 청소보증금 환급이 불가합니다! 입,퇴실 시간을 꼭 지켜주세요 !!\n"
            "\n"
            "※스페이스클라우드 결제완료 및 공간이용동의서 작성, 청소보증금 5만원 입금후 예약이 확정 처리됩니다.\n"
            "- 청소보증금 환급 조건은 별도로 안내해 드리며, 공간이용동의서를 꼼꼼히 읽어주세요!!\n"
            "\n"
            "영업시간 0~24시 | 휴무일 없음\n"
            "지상 7층 · 주차 1대 가능 · 엘리베이터 있음"
        ),
        # 실제 리스팅 "시설안내"/"예약시 주의사항"/"환불규정 안내" 탭 원문 그대로
        # (2026-07-02, 사용자 제공 스크린샷 기준)
        facility_notes=[
            "합정역 3번 출구 도보 1분거리에 있어 모임하기 좋은 곳에 있어요:) 인근에 맛집과 카페, 편의점이 많아 먹고 놀기 최고에요!",
            "냉장고, 에어프라이기, 인덕션, 전자레인지, 전기포트, 냄비, 후라이팬, 8인 기준의 머그잔과 와인잔, 그리고 각종 식기류가 준비되어 있어요:) 그 외엔 준비해드릴 수 없어요 ㅠㅠ",
            "소독액, 손소독제, 물티슈, 휴지, 일반 및 음식물, 재활용 봉투도 현장에 구비되어 있어요! 쾌적한 공간에서 즐거운 시간 보내시고, 입실 전 상태로 뒷정리 부탁드립니다:)",
            "숙박 목적 및 숙박 시설 공간이 아니므로 일체 숙박용품(세면도구 및 이불, 수건 등)은 제공하지 않아요:)",
            "냉난방기, 바닥난방, 크고 두꺼운 극세사 담요가 있어 쾌적하게 이용하실 수 있어요:)",
            "주차는 본건물에 공간 이용시간에 한해서만 최대 1대까지 가능해요:)",
            "5G WIFI, 보드게임, 100인치 빔프로젝터(HDMI선으로 연결), 휴대폰 삼각대가 구비되어 있어요! **빔프로젝터 연결 노트북은 직접 들고와 주세요!",
            "간단한 취사는 가능해요. 단, 고기류나 생선류, 튀김류와 같이 냄새 배는 요리는 불가해요. 배달음식 및 음식물, 주류 반입도 가능해요:)",
            "스페이스T의 출입문은 잠금이 되지 않지만, 파티룸이 건물 꼭대기층에 있고, 해당 건물에는 공유오피스와 일반 회사만 있어 외부인 출입이 없으니 보안에 안심하셔도 돼요:)",
            "범죄 예방 및 화재 예방, 고객 안전 및 시설 보호, 인원 수 확인용으로 24시간 CCTV 가동 중이에요. 그 외 용도로는 일체 열람 및 저장하지 않아요:)",
        ],
        notice_items=[
            "입실 및 퇴실시간을 어기실 경우, 시간 당 금액의 2배가 청구돼요. 입실은 정시에, 퇴실은 마지막 이용시간 10분전이에요. **예) 14시~18시 예약시 17시 50분 퇴실",
            "이용시간 보다 늦게 입실하시거나, 일찍 퇴실하신다고 해서 남은 이용시간을 환불해 드리지 않습니다:)",
            "기준인원은 6명이며 최대 방문 10명입니다. 인원 초과시 1인당 10,000원 추가돼요. **잠시 방문도 인원 수에 포함되고, 인원 교체는 불가합니다!",
            "이용 인원 수의 변동이 있으실 경우에는 입실 전(이용시간 전)에 말씀해 주세요. **이용 시간 이후에 말씀하시면 추가 인원에 대한 환불은 불가합니다:)",
            "건물 전체가 금연 구역이에요! 실내 흡연은 절대 불가해요!! 생일초는 가능하지만, 버너 및 이벤트초 등의 화재 위험 물품은 반입이 절대 불가해요!!",
            "미성년자는 저녁10시 이후부터 이용이 불가해요. **미성년자의 경우, 예약 전에 먼저 말씀해 주세요! 말씀 안 해주셔서 발생한 문제는 일체 책임지지 않아요!",
            "스페이스클라우드 결제완료 후, 공간이용동의서 작성 및 보증금 입금이 완료되어야 예약 확정 처리돼요. **안내 이후 2시간 이내로 동의서 작성 및 보증금 입금이 되지 않으면 예약 취소 처리돼요",
            "보증금 환급은 보증금 환급 조건에 충족하면, 이용일 기준 차주 화요일에 일괄 환급해 드려요. **보증금 환급 조건은 예약 시, 별도로 안내해 드려요!",
            "예약 변경은 이용일 기준 8일 전까지만 가능하며, 예약 취소의 경우 취소 일자별 환불 금액이 상이해요. **코로나, 독감 등의 경우도 개인사정으로 취급합니다!",
            "다양한 채널을 통해 예약을 받고 있어 관리자의 예약 확인 후, 예약 취소처리 될 수 있으니 이점 양해 부탁드려요:) 최대한 빨리 확인할게요!",
        ],
    ),
    Space(
        id="sp04", name="성수동 루프탑 파티룸", type="파티룸", region="성수동",
        capacity=20, price_per_hour_weekday=35000, price_per_hour_weekend=50000,
        facilities=["루프탑", "블루투스 스피커", "테이블세팅"],
        popularity=88,
        image_url="images/party_room1.jpg",
        price_package=110000, package_hours="18:00~익일 08:00",
        description="성수동 감성 가득한 루프탑 파티룸입니다. 탁 트인 야외 공간에서 생일파티, 소모임 등 "
                    "다양한 행사를 즐길 수 있습니다.",
    ),
    # sp07/sp08 = 목록 화면 시각적 풍성함을 위해 추가한 파티룸 2개 (실사진 없어서 임시 플레이스홀더,
    # 나중에 실제 사진 받으면 sp01/02/04/05/06 처럼 교체 예정).
    Space(
        id="sp07", name="이태원 루프탑 파티룸", type="파티룸", region="이태원",
        capacity=15, price_per_hour_weekday=28000, price_per_hour_weekend=40000,
        facilities=["루프탑", "빔프로젝터", "블루투스 스피커"], popularity=84,
        image_url="https://placehold.co/400x300?text=Space+G",
        price_package=90000, package_hours="19:00~익일 09:00",
        description="이태원 중심가에 위치한 루프탑 파티룸입니다. 다양한 문화가 어우러진 동네 분위기와 함께 "
                    "활기찬 파티를 즐기실 수 있어요.",
    ),
    Space(
        id="sp08", name="건대 스타일리시 파티룸", type="파티룸", region="건대입구",
        capacity=12, price_per_hour_weekday=16000, price_per_hour_weekend=22000,
        facilities=["미러볼", "노래방 기기", "블루투스 스피커"], popularity=90,
        image_url="https://placehold.co/400x300?text=Space+H",
        description="건대입구역 인근의 트렌디한 파티룸입니다. 미러볼과 노래방 기기로 신나는 분위기를 "
                    "연출할 수 있습니다.",
    ),
    Space(
        id="sp05", name="마포 공유주방 키친랩", type="공유주방", region="마포구",
        capacity=6, price_per_hour_weekday=18000, price_per_hour_weekend=22000,
        facilities=["4구 인덕션", "오븐", "식기세트"],
        popularity=70,
        image_url="images/공유주방1.jpg",
        description="마포구에 위치한 공유주방입니다. 다양한 조리기구가 구비되어 있어 소규모 쿠킹 클래스나 "
                    "모임 요리에 적합합니다.",
    ),
    Space(
        id="sp06", name="잠실 베이킹 스튜디오", type="공유주방", region="잠실",
        capacity=8, price_per_hour_weekday=22000, price_per_hour_weekend=28000,
        facilities=["오븐 2대", "냉장고", "식기세트", "앞치마 대여"],
        popularity=81,
        image_url="images/공유주방2.jpg",
        description="잠실 인근의 베이킹 전문 공유주방입니다. 오븐 2대와 넉넉한 조리 공간으로 베이킹 클래스나 "
                    "소모임에 활용하기 좋습니다.",
    ),
]

PRODUCTS: list[Product] = [
    Product(id="pd01", name="생일 케이크", price=35000, target_space_types=["파티룸"], image_url="images/케이크.jpg"),
    Product(id="pd02", name="풍선 데코 세트", price=15000, target_space_types=["파티룸"], image_url="images/풍선파.jpg"),
    Product(id="pd03", name="다과 세트", price=20000, target_space_types=["회의실", "파티룸"], image_url="images/다과세트.jpg"),
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
    # sp07
    Review(id="rv31", space_id="sp07", content="루프탑에서 보는 야경이 정말 예뻤어요.", rating=5, created_at=date(2026, 5, 26)),
    Review(id="rv32", space_id="sp07", content="이태원이라 접근성이 좋고 근처에 먹거리도 많아요.", rating=5, created_at=date(2026, 5, 27)),
    Review(id="rv33", space_id="sp07", content="빔프로젝터 화질이 선명해서 영화 감상하기 좋았어요.", rating=4, created_at=date(2026, 5, 28)),
    Review(id="rv34", space_id="sp07", content="루프탑이라 날씨 영향을 좀 받는 편이에요.", rating=3, created_at=date(2026, 5, 29)),
    Review(id="rv35", space_id="sp07", content="공간이 넓어서 인원 많은 모임에 딱이었습니다.", rating=5, created_at=date(2026, 5, 30)),
    # sp08
    Review(id="rv36", space_id="sp08", content="미러볼이랑 노래방 기기 덕분에 분위기가 확 살았어요.", rating=5, created_at=date(2026, 5, 31)),
    Review(id="rv37", space_id="sp08", content="건대입구역에서 가까워서 이동이 편했습니다.", rating=5, created_at=date(2026, 6, 1)),
    Review(id="rv38", space_id="sp08", content="가격 대비 시설이 알차서 만족스러웠어요.", rating=5, created_at=date(2026, 6, 2)),
    Review(id="rv39", space_id="sp08", content="방음이 살짝 아쉬웠지만 전체적으로 괜찮았어요.", rating=4, created_at=date(2026, 6, 3)),
    Review(id="rv40", space_id="sp08", content="노래방 기기 음질이 좋아서 다들 만족했어요.", rating=5, created_at=date(2026, 6, 4)),
]

# sp03(시연용)은 A가 크롤링한 실제 후기 367건을 그대로 사용 (spacecloud_reviews.csv)
REVIEWS: list[Review] = _PLACEHOLDER_REVIEWS + load_crawled_reviews()
