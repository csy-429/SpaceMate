"""
개발자B 담당: 보완상품 추천 서비스.
[갱신] FR-04/FR-07 LLM 연동: LangChain + OpenAI(GPT-4o-mini)로 예약 맥락 -> 보완상품 추천.
       실패/타임아웃/키없음 시 예외를 던지고, 라우터(recommendations.py)의 except에서
       get_fallback_products()로 즉시 대체한다 (NFR 8.2 Fallback 전략, PRD FR-07).

할루시네이션 방지 (NFR 8.1): 프롬프트에 space_type과 매칭되는 후보 상품 id 목록만 주입하고,
LLM 응답에서 그 후보 id 목록에 없는 값은 전부 걸러낸다. 카탈로그 밖 상품은 절대 반환되지 않는다.

비용/속도 예산 (NFR 8.3): 모델은 gpt-4o-mini, 응답 max_tokens=1000, 클라이언트 레벨
timeout=3초로 NFR 7.1(보완상품 추천 응답 3초 초과 시 폴백)을 강제한다.

[갱신] 캐싱 추가 — A의 review_grouping.py 캐시 패턴과 동일한 구조 (2026-07-02).
매 요청마다 LLM을 새로 부르면 화면 들어갈 때마다 1~3초씩 걸려서(발표 때 어색한 딜레이),
space_type별로 한 번 성공한 결과를 메모리에 저장해두고 재사용한다. 재호출 여부/우선순위
판단은 라우터(recommendations.py)가 하고, 이 파일은 캐시 저장소(메모리+파일)만 제공한다.
"""

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.data.seed import PRODUCTS
from app.models.schemas import Product

load_dotenv()

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"

# space_type -> 마지막으로 성공한 LLM 추천 결과 (서버 켜있는 동안만 유지)
_recommendation_cache: dict[str, list[Product]] = {}


def get_cached_products(space_type: str) -> list[Product] | None:
    return _recommendation_cache.get(space_type)


def set_cached_products(space_type: str, products: list[Product]) -> None:
    _recommendation_cache[space_type] = products


def _cache_path(space_type: str) -> Path:
    return CACHE_DIR / f"recommendations_{space_type}.json"


def save_recommendation_cache(space_type: str, products: list[Product]) -> Path:
    """발표 당일 라이브 API 실패 리스크를 줄이기 위한 파일 스냅샷 (서버 재시작해도 남음)."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(space_type)
    data = [p.model_dump() for p in products]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_recommendation_cache(space_type: str) -> list[Product] | None:
    path = _cache_path(space_type)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Product(**item) for item in data]

# space_type -> 추천 상품 id 목록 (하드코딩 폴백, FR-07)
FALLBACK_MAP: dict[str, list[str]] = {
    "회의실": ["pd03", "pd04"],
    "파티룸": ["pd01", "pd02", "pd04"],
    "공유주방": ["pd05", "pd03"],
}

RECOMMEND_TIMEOUT_SEC = 3  # NFR 7.1
RECOMMEND_MODEL = "gpt-4o-mini"  # NFR 8.3

_llm: ChatOpenAI | None = None


def get_fallback_products(space_type: str) -> list[Product]:
    """AI 미작동/실패 시 즉시 반환되는 하드코딩 폴백 (FR-07, NFR 8.2)."""
    ids = FALLBACK_MAP.get(space_type, [])
    return [p for p in PRODUCTS if p.id in ids]


def _get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model=RECOMMEND_MODEL,
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=RECOMMEND_TIMEOUT_SEC,
            max_tokens=1000,
        )
    return _llm


def _candidate_products(space_type: str) -> list[Product]:
    """후보 풀은 seed의 target_space_types 기준 (FALLBACK_MAP보다 넓을 수 있음)."""
    return [p for p in PRODUCTS if space_type in p.target_space_types]


def _parse_ids(raw: str, valid_ids: set[str]) -> list[str]:
    """LLM 응답에서 JSON 배열만 뽑아내고, 후보 id 목록에 없는 값은 버린다 (NFR 8.1)."""
    text = raw.strip()
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        text = match.group(0)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [pid for pid in parsed if isinstance(pid, str) and pid in valid_ids]


def get_llm_recommended_products(
    space_type: str, capacity: int, time_slot: str | None
) -> list[Product]:
    """
    FR-04: 예약 맥락(공간유형/인원/시간대) -> 페르소나(쌍윤씨) 참고 -> 보완상품 추천.
    실패 시 예외를 그대로 올려서 호출부(라우터)가 폴백으로 떨어지게 한다.
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set")

    candidates = _candidate_products(space_type)
    if not candidates:
        raise RuntimeError(f"no candidate products for space_type={space_type}")

    catalog_text = "\n".join(
        f"- id={p.id}, name={p.name}, price={p.price}원" for p in candidates
    )

    system = SystemMessage(
        content=(
            "너는 공간 예약 서비스 SpaceMate의 보완상품 추천 어시스턴트다. "
            "아래 후보 목록에 있는 상품 id만 사용해서 추천해야 하며, "
            "후보에 없는 상품을 지어내면 안 된다. "
            "페르소나(24세 대학생 '쌍윤씨', 동아리/조모임/생일파티로 공간을 자주 예약하고 "
            "준비물을 한 번에 사고 싶어함)를 참고해서 예약 맥락에 맞는 상품을 1~3개 골라라. "
            '반드시 JSON 배열 형식으로만 응답한다. 예: ["pd01", "pd02"]'
        )
    )
    human = HumanMessage(
        content=(
            f"공간유형: {space_type}\n"
            f"인원: {capacity}명\n"
            f"시간대: {time_slot or '미지정'}\n"
            f"후보 상품 목록:\n{catalog_text}\n\n"
            "위 후보 중에서만 골라 상품 id 배열(JSON)로만 답하라."
        )
    )

    llm = _get_llm()
    response = llm.invoke([system, human])  # timeout=3초가 NFR 7.1을 강제

    valid_ids = {p.id for p in candidates}
    ids = _parse_ids(response.content, valid_ids)
    if not ids:
        raise RuntimeError("LLM returned no valid product ids")

    return [p for p in candidates if p.id in ids]
