"""
A가 크롤링한 실제 후기 CSV(app/data/spacecloud_reviews.csv)를 로드한다.
CSV 컬럼: id, username, rating, date, review — space_id 컬럼은 없다.
CSV 전체가 시연용 공간 sp03("[합정역1분거리파티룸] 스페이스T" 실 리스팅) 후기이므로
모든 행을 sp03에 고정 매핑한다. 다른 공간을 크롤링하게 되면 이 로더를 공간별로 분리해야 함.
형식이 안 맞는 행(별점 범위 밖, 날짜 파싱 실패 등)은 건너뛰고 나머지는 그대로 로드한다 —
크롤링 데이터 특성상 소수의 결측/오염 행이 있을 수 있어 전체 로딩이 막히지 않게 방어적으로 처리.

[수정 이력]
- encoding="utf-8" -> "utf-8-sig" 로 변경.
  CSV가 BOM 포함으로 저장되어 있어서, "utf-8"로 열면 첫 컬럼명이 "id"가 아니라
  "\ufeffid"로 인식되어 row["id"]에서 KeyError가 나고 모든 행이 조용히 스킵되던 버그 수정.
  (except (KeyError, ValueError): continue 가 이 에러를 삼켜서 증상이 안 보였음 — 367건 전부
  로드 실패해도 함수는 그냥 빈 리스트를 반환할 뿐 에러가 안 남)
- author=row["username"].strip() 그대로 저장하던 부분을 mask_nickname()으로 마스킹.
  (PRD 4-4 개인정보 마스킹 원칙 — 첫 글자만 남기고 나머지 '*' 처리)
"""
import csv
from datetime import datetime
from pathlib import Path
from app.models.schemas import Review
from app.services.review_grouping import mask_nickname

_CSV_PATH = Path(__file__).parent / "spacecloud_reviews.csv"
_TARGET_SPACE_ID = "sp03"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def load_crawled_reviews() -> list[Review]:
    if not _CSV_PATH.exists():
        return []
    reviews: list[Review] = []
    with open(_CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rating = int(row["rating"])
                if not (1 <= rating <= 5):
                    continue
                created_at = datetime.strptime(row["date"], _DATE_FORMAT).date()
                content = row["review"].strip()
                if not content:
                    continue
                reviews.append(
                    Review(
                        id=f"cs{row['id']}",
                        space_id=_TARGET_SPACE_ID,
                        content=content,
                        author=mask_nickname(row["username"].strip()) or "익명",
                        rating=rating,
                        created_at=created_at,
                    )
                )
            except (KeyError, ValueError):
                continue
    return reviews
