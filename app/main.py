"""
SpaceMate FastAPI 진입점.
로직은 여기에 넣지 않는다 — 라우터 등록만.
개발자 A/B는 각자 routers/*.py 안에 실제 엔드포인트를 구현한다.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import spaces, reviews, reservations, recommendations, cart, checkout, products
from app.data import repository
from app.services.review_grouping import load_groups_cache

app = FastAPI(title="SpaceMate API")


@app.on_event("startup")
def load_review_group_caches() -> None:
    """서버 시작 시 데모용 후기 그룹 캐시를 미리 메모리에 채워둔다.

    repository._review_groups는 인메모리라 서버가 재시작되면 항상 비워지는데,
    캐시가 없으면 누군가 /admin/generate-groups를 수동으로 호출하기 전까지
    GET /spaces/{id}가 계속 raw(원문 후기) 모드로만 응답한다.
    캐시가 있으면 첫 요청부터 grouped 모드로 응답해서, 재시작/라이브 API 실패
    여부와 무관하게 데모에서 항상 AI 요약이 노출되도록 보장한다 (NFR 8.2).
    """
    for space_id in ["sp03"]:
        cached = load_groups_cache(space_id)
        if cached:
            repository.replace_review_groups(space_id, cached)

# 프론트(Vercel)에서 fetch로 호출하므로 CORS 허용 필수.
# 배포 시 allow_origins를 실제 Vercel 도메인으로 좁힐 것.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(spaces.router, prefix="/spaces", tags=["spaces"])
app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
app.include_router(reviews.admin_router, prefix="/admin", tags=["admin"])
app.include_router(reservations.router, prefix="/reservations", tags=["reservations"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
app.include_router(cart.router, prefix="/cart", tags=["cart"])
app.include_router(checkout.router, prefix="/checkout", tags=["checkout"])
app.include_router(products.router, prefix="/products", tags=["products"])


@app.get("/")
def health_check():
    return {"status": "ok", "service": "SpaceMate API"}
