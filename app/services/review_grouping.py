"""
services/review_grouping.py

담당: 개발자A
역할:
  1) 닉네임 마스킹 (PRD 4-4 데이터보안 - 개인정보 마스킹)
  2) 후기 원문 -> 고정 라벨(방음/청결/접근성) 분류 + 그룹별 요약 (LangChain + ChatGPT)
  3) AI 실패 시 폴백: 예외를 그대로 올려서 라우터가 원문 그대로 노출하도록 함 (PRD NFR 8.2)

[고정 라벨 관련]
LABELS는 임시값입니다. 팀에서 최종 라벨을 확정하면 이 리스트 하나만 바꾸면 되고,
나머지 로직(프롬프트 생성, 캐시 저장/로드)은 안 건드려도 됩니다.

[승인 절차 관련]
PRD FR-02: "AI 요약은 자동 노출(승인 절차 없음)"에 맞춰 생성된 그룹은 바로 status="approved"로
저장한다 (원래 있던 pending -> 관리자 승인 큐 방식은 뺌, 화면도 안 만들기로 팀 합의됨).
"""

import os
import json
from pathlib import Path

from dotenv import load_dotenv

from app.models.schemas import Review, ReviewGroup

load_dotenv()

# ---------------------------------------------------------------------------
# 고정 라벨 (분장서 "시간 촉박 시 컷 순서 2순위" 적용: 고정 라벨)
# 팀 확정: 호스트, 청결, 접근성, 비품, 기타 (2025-07 기준)
# "기타"는 나머지 4개 중 어디에도 안 맞는 후기를 담는 캐치올 카테고리.
# ---------------------------------------------------------------------------
LABELS: list[str] = ["호스트", "청결", "접근성", "비품", "기타"]

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"

# PRD NFR 8.3: 호출당 입력 ≤4K 토큰. 리뷰 1건당(내용+id+별점) 대략 60~80토큰, 여기에
# 라벨 설명/지시문 오버헤드(~800토큰)까지 감안해 리뷰 본문은 50건으로 제한한다.
# sp03처럼 리뷰가 367건인 공간은 전부 넣으면 15,000~20,000토큰까지 튀어 budget을 3~5배 초과함.
# [확인 필요] 50이라는 숫자와 "별점 골고루 샘플링" 방식은 임시 판단값 — A 확인 후 조정 가능.
MAX_REVIEWS_FOR_PROMPT = 50

# NFR 7.1: 그룹핑은 그룹 1건당 ≤10초. B의 recommendation.py(timeout=3, NFR 7.1 응답요구)와
# 같은 이유로, 여기도 timeout이 없으면 응답이 안 올 때 무한 대기해서 NFR 8.2 폴백이 작동 안 함.
GROUPING_TIMEOUT_SEC = 10


# ---------------------------------------------------------------------------
# 1) 닉네임 마스킹
# ---------------------------------------------------------------------------
def mask_nickname(name: str) -> str:
    """앞 3자리까지만 노출 대상으로 삼고, 첫 글자만 남기고 나머지는 '*'.
    3자리를 넘는 부분은 잘라내고 표시하지 않음.
    예: "세연"->"세*", "김선근"->"김**", "hodyun"->"h**"
    """
    name = (name or "").strip()
    if not name:
        return ""
    capped = name[:3]
    if len(capped) == 1:
        return capped
    return capped[0] + "*" * (len(capped) - 1)


# ---------------------------------------------------------------------------
# 2) LangChain + ChatGPT 그룹핑
# ---------------------------------------------------------------------------
def _sample_reviews_for_prompt(reviews: list[Review], max_count: int) -> list[Review]:
    """리뷰 수가 max_count를 넘으면 별점 버킷을 고르게 순회하며 샘플링한다.
    (최신순으로 자르면 별점 낮은 후기가 우연히 다 오래된 경우 누락될 수 있어서,
    "최근 N개" 대신 별점별로 최근 것부터 라운드로빈으로 채우는 방식을 택함.)
    """
    if len(reviews) <= max_count:
        return reviews

    buckets: dict[int, list[Review]] = {}
    for r in sorted(reviews, key=lambda r: r.created_at, reverse=True):
        buckets.setdefault(r.rating, []).append(r)

    sampled: list[Review] = []
    idx = 0
    while len(sampled) < max_count:
        added_this_round = False
        for rating in sorted(buckets):
            bucket = buckets[rating]
            if idx < len(bucket):
                sampled.append(bucket[idx])
                added_this_round = True
                if len(sampled) >= max_count:
                    break
        if not added_this_round:
            break
        idx += 1
    return sampled


def _build_prompt(reviews: list[Review], labels: list[str]) -> str:
    review_lines = "\n".join(f"- (id={r.id}, 별점={r.rating}) {r.content}" for r in reviews)
    label_list = ", ".join(labels)
    return f"""아래는 한 공간에 대한 실제 이용 후기 목록입니다.
각 후기를 다음 고정 카테고리 중 가장 관련 있는 것 하나 이상에 매핑하고, 카테고리별로
후기 내용을 2~3문장으로 요약해주세요.

카테고리: {label_list}
- "호스트": 호스트(사장님/담당자)와의 연락 응답률, 친절도, 응대 태도 등
- "청결": 시설 청결 상태, 화장실 위생, 냄새 등
- "접근성": 역과의 거리, 도보/자차 이용 편의성, 주차 등
- "비품": 식기류, 난방/냉방, 빔프로젝터 등 홈페이지에 기재된 비품이 실제로
  구비되어 있는지·상태는 어떤지에 대한 언급
- "기타": 위 4개 분류에 뚜렷하게 해당하지 않는 후기 중, 언급 빈도가 높은 주제
  (예: 분위기·인테리어·가격 만족도 등). 이 카테고리는 가장 자주 등장하는
  주제 위주로 요약하고, 산발적인 단일 언급은 생략해도 됨.
모든 후기는 반드시 위 5개 카테고리 중 최소 하나에는 포함되어야 합니다.
관련 후기가 하나도 없는 카테고리는 결과 자체에서 제외하세요.
label 값은 반드시 위 5개 카테고리 문자열 중 하나와 정확히 일치해야 합니다 (새 카테고리 생성 금지).
review_ids는 반드시 아래 "후기 목록"에 실제로 나열된 id 값만 사용하세요 (목록에 없는 id를 지어내지 마세요).

후기 목록:
{review_lines}

아래 JSON 형식으로만 답하세요 (다른 텍스트 금지, id는 예시가 아니라 위 후기 목록에서 그대로 가져올 것):
[
  {{"label": "카테고리명", "summary": "2~3문장 요약", "review_ids": ["<위 목록에 있는 실제 id>", "..."]}}
]
"""


def generate_review_groups(space_id: str, reviews: list[Review]) -> list[ReviewGroup]:
    """LangChain + ChatGPT로 고정 라벨 기준 그룹 생성.
    실패(타임아웃/API 에러/JSON 파싱 실패) 시 예외를 그대로 올림.
    -> 호출한 라우터(POST /admin/generate-groups)가 이 예외를 잡아서
       "원문 그대로 노출" 폴백으로 넘어가야 함 (PRD NFR 8.2, 분장서 7번 항목).
    """
    from langchain_openai import ChatOpenAI  # 지연 import: API 키 없어도 모듈 로드는 되게

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=api_key,
        timeout=GROUPING_TIMEOUT_SEC,
        max_tokens=1000,  # NFR 8.3: 출력 ≤1K 토큰
    )
    sampled = _sample_reviews_for_prompt(reviews, MAX_REVIEWS_FOR_PROMPT)
    prompt = _build_prompt(sampled, LABELS)

    response = llm.invoke(prompt)
    raw = response.content.strip()
    # 혹시 모델이 ```json ... ``` 코드블록으로 감싸서 응답하는 경우 대비
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw[4:] if raw.lower().startswith("json") else raw

    parsed = json.loads(raw)  # 형식이 어긋나면 여기서 JSONDecodeError -> 상위에서 폴백 처리

    valid_labels = set(LABELS)
    valid_review_ids = {r.id for r in sampled}  # 실제로 프롬프트에 넣어준 리뷰 id만 인정 (NFR 8.1)

    groups: list[ReviewGroup] = []
    for i, item in enumerate(parsed, start=1):
        label = item.get("label")
        summary = item.get("summary")
        if label not in valid_labels or not summary:
            # 고정 라벨을 안 지켰거나 요약이 비어있는 항목은 신뢰하지 않고 건너뜀 (NFR 8.1)
            continue
        review_ids = [rid for rid in item.get("review_ids", []) if rid in valid_review_ids]
        groups.append(
            ReviewGroup(
                id=f"rg_{space_id}_{i}",
                space_id=space_id,
                label=label,
                summary=summary,
                status="approved",  # FR-02: 승인 절차 없이 자동 노출
                review_ids=review_ids,
            )
        )
    return groups


# ---------------------------------------------------------------------------
# 3) 캐시 저장/로드 (발표 당일 라이브 API 호출 실패 리스크 줄이기 위함)
# ---------------------------------------------------------------------------
def save_groups_cache(space_id: str, groups: list[ReviewGroup]) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"review_groups_{space_id}.json"
    data = [g.model_dump() for g in groups]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_groups_cache(space_id: str) -> list[ReviewGroup] | None:
    path = CACHE_DIR / f"review_groups_{space_id}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return [ReviewGroup(**item) for item in data]
