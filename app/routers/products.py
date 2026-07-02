"""
개발자 B 담당 — 보완상품 조회 API.

[신규] 장바구니/결제 화면에서 담긴 상품의 이름·가격을 보여줘야 하는데, CartEntry엔
ref_id(상품 id)만 저장돼있어서 상품 상세를 따로 조회할 방법이 없었음. 상품이 5개뿐인
정적 시드 데이터라 무겁게 만들 필요 없이 조회용 엔드포인트만 얇게 추가.

GET /products          — 전체 목록 (space_type 쿼리로 필터 가능, FR-04 추천과 동일 로직 재사용)
GET /products/{id}     — 단건 조회, 없으면 404
"""
from fastapi import APIRouter, HTTPException

from app.data import repository

router = APIRouter()


@router.get("")
def list_products(space_type: str | None = None):
    return repository.list_products(space_type)


@router.get("/{product_id}")
def get_product(product_id: str):
    product = next((p for p in repository.list_products() if p.id == product_id), None)
    if product is None:
        raise HTTPException(status_code=404, detail="product not found")
    return product
