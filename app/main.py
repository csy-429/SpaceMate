"""
SpaceMate FastAPI 진입점.
로직은 여기에 넣지 않는다 — 라우터 등록만.
개발자 A/B는 각자 routers/*.py 안에 실제 엔드포인트를 구현한다.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import spaces, reviews, reservations, recommendations, cart, checkout

app = FastAPI(title="SpaceMate API")

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
app.include_router(reservations.router, prefix="/reservations", tags=["reservations"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
app.include_router(cart.router, prefix="/cart", tags=["cart"])
app.include_router(checkout.router, prefix="/checkout", tags=["checkout"])


@app.get("/")
def health_check():
    return {"status": "ok", "service": "SpaceMate API"}
