"""
스페이스클라우드(spacecloud.kr) 후기 크롤러 - API 직접 호출 버전

브라우저 개발자도구 Network 탭에서 확인한 실제 후기 데이터 API를
직접 호출합니다. Selenium/브라우저 실행이 필요 없어 빠르고 안정적입니다.

[확인 완료]
- robots.txt: Claude-Web / anthropic-ai / User-agent:* 모두
  /space/25288 경로는 막혀있지 않음. robots.txt 기준 크롤링 가능.
- 후기 페이지네이션 엔드포인트 확인됨:
    GET https://api.spacecloud.kr/reviews
    쿼리 파라미터: page, only_image_review, space_id
  예: https://api.spacecloud.kr/reviews?page=2&only_image_review=false&space_id=25288
- 페이지당 3개씩, 총 367건 / 123페이지 (space_id=25288 기준, 값은 변할 수 있음)
- 리뷰 1건의 JSON 필드: id, created_at(날짜), content(후기 본문),
  rate(별점), writer.name(사용자명), images(사진 목록) 등
"""

import time
import random
import csv
import requests

SPACE_ID = 25288
BASE_URL = "https://api.spacecloud.kr/reviews"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    ),
    "Referer": f"https://www.spacecloud.kr/space/{SPACE_ID}",
    "Origin": "https://www.spacecloud.kr",
    "Accept": "application/json, text/plain, */*",
    # 403/빈값이 나오면 Network 탭 Headers의 다른 요청 헤더도 추가해보세요.
}

# 요청 사이 랜덤 대기 시간(초) - 서버 부하를 줄이고 정상 트래픽처럼 보이게 함
REQUEST_DELAY_RANGE = (2.0, 4.0)

# 연속 실패 시 재시도 관련 설정
MAX_RETRIES_PER_PAGE = 3
BACKOFF_BASE_SECONDS = 5  # 실패 시 5초, 10초, 20초... 로 대기시간 증가
MAX_CONSECUTIVE_FAILURES = 5  # 이 횟수만큼 페이지 자체가 계속 실패하면 전체 중단

# 요청마다 새 TCP 연결을 맺지 않고 재사용 -> 서버 부하 감소 + 더 자연스러운 트래픽
session = requests.Session()
session.headers.update(HEADERS)


def fetch_page(page: int) -> dict:
    """실패 시 지수 백오프로 재시도. 429(Too Many Requests)/5xx는 특히 더 오래 대기."""
    for attempt in range(1, MAX_RETRIES_PER_PAGE + 1):
        try:
            resp = session.get(
                BASE_URL,
                params={"page": page, "only_image_review": "false", "space_id": SPACE_ID},
                timeout=10,
            )
            if resp.status_code == 429:
                wait = BACKOFF_BASE_SECONDS * (2 ** attempt)
                print(f"  [429] 요청 과다 감지, {wait}초 대기 후 재시도 ({attempt}/{MAX_RETRIES_PER_PAGE})")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            wait = BACKOFF_BASE_SECONDS * attempt
            print(f"  요청 실패({e}), {wait}초 대기 후 재시도 ({attempt}/{MAX_RETRIES_PER_PAGE})")
            time.sleep(wait)
    raise RuntimeError(f"{page}페이지: {MAX_RETRIES_PER_PAGE}회 재시도 후에도 실패")


def extract_username(review: dict) -> str:
    """확인 완료: 사용자명은 writer.name 에 들어있음
    (예: {"writer": {"id": "...", "name": "호이이", "email": "hylove0***", ...}})"""
    writer = review.get("writer") or {}
    return writer.get("name", "")


def parse_review_block(data: dict):
    """응답이 {reviews: [...], page: {...}} 형태이든
    {reviews: {reviews: [...], page: {...}}} 형태이든 둘 다 처리."""
    reviews_field = data.get("reviews")
    if isinstance(reviews_field, dict):
        review_list = reviews_field.get("reviews", [])
        page_info = reviews_field.get("page", {})
    else:
        review_list = reviews_field or []
        page_info = data.get("page", {})
    return review_list, page_info


def crawl_all_reviews() -> list[dict]:
    all_reviews = []
    page = 1
    total_pages = 1
    consecutive_failures = 0

    while page <= total_pages:
        try:
            data = fetch_page(page)
            consecutive_failures = 0  # 성공하면 실패 카운트 초기화
        except RuntimeError as e:
            consecutive_failures += 1
            print(f"  {e}")
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                print(f"연속 {MAX_CONSECUTIVE_FAILURES}회 실패로 크롤링을 중단합니다. "
                      f"지금까지 모은 {len(all_reviews)}건은 저장됩니다.")
                break
            page += 1
            continue

        review_list, page_info = parse_review_block(data)
        total_pages = page_info.get("pages", 1)

        for r in review_list:
            all_reviews.append(
                {
                    "id": r.get("id"),
                    "username": extract_username(r),
                    "rating": r.get("rate"),
                    "date": r.get("created_at"),
                    "review": r.get("content"),
                }
            )

        print(f"{page}/{total_pages} 페이지 수집 완료 (누적 {len(all_reviews)}건)")
        page += 1
        time.sleep(random.uniform(*REQUEST_DELAY_RANGE))  # 요청 간격 두기

    return all_reviews


def save_csv(reviews: list[dict], filename: str = "spacecloud_reviews.csv"):
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "username", "rating", "date", "review"])
        writer.writeheader()
        writer.writerows(reviews)


if __name__ == "__main__":
    try:
        reviews = crawl_all_reviews()
        save_csv(reviews)
        print(f"총 {len(reviews)}건 저장 완료 -> spacecloud_reviews.csv")
    finally:
        session.close()  # 세션(연결) 명시적으로 정리 후 프로그램 종료
