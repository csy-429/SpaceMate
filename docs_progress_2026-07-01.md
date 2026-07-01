# SpaceMate 공통 작업 진행내역 (2026-07-01)

## 1. 완료된 작업

### 프로젝트 구조 세팅
확정된 공통 파일들을 아래 구조로 `sesac_pjt/SpaceMate`에 배치 완료.

```
app/
  __init__.py
  main.py                  # 라우터 등록만, 로직 없음
  models/
    __init__.py
    schemas.py             # 공용 Pydantic 모델 확정본
  data/
    __init__.py
    seed.py                # 시드 데이터 (공간 6개, 상품 5개, 후기 30개)
    repository.py          # 데이터 접근 함수
  routers/
    __init__.py
    spaces.py, reviews.py, reservations.py,
    recommendations.py, cart.py, checkout.py   # 빈 APIRouter 뼈대
  services/
    __init__.py
    review_grouping.py     # 빈 파일
    recommendation.py      # 빈 파일
requirements.txt
```

기존에 있던 구버전/빈 파일들은 확정본으로 전부 덮어씀. 폴더마다 `__init__.py` 빈 파일 존재 확인 완료.

### 기동 확인
로컬에서 `pip install -r requirements.txt` → `uvicorn app.main:app --reload` 실행, `http://localhost:8000/` 요청 시 정상 응답 확인.
```json
{"status": "ok", "service": "SpaceMate API"}
```

### GitHub 저장소 생성 & 공통 커밋 push
새 GitHub 레포 생성 후 로컬에서 초기화, 커밋, push 완료.
```
git init
git branch -M main
git remote add origin https://github.com/<계정명>/SpaceMate.git
git add .
git commit -m "chore: 공통 스키마/시드/repository/main 뼈대 구성"
git push -u origin main
```
→ 이 커밋이 "절대 흔들리지 않는 기준선".

## 2. 클론 vs 신규 기능 구분 (발표 때 꼭 구분해서 설명)

| 구분 | 포함 기능 |
| --- | --- |
| **[클론] 원본 재현** | 검색/필터/정렬, 상세페이지, 시간대별 요금, 후기 원문, 공간 단독 예약 시 즉시 결제 |
| **[신규] 팀 추가 기능** | AI 후기 그룹핑, 보완상품 추천·장바구니·통합결제 |

결제 흐름: 공간만 예약 → 장바구니 없이 바로 결제 / 상품 추가 담을 때만 → 장바구니 경유 (신규 기능 진입점).

## 3. 역할 분담 & 브랜치 전략

| | 담당자 | 브랜치 | 담당 파일 |
| --- | --- | --- | --- |
| 개발자 A | 팀원 | `feature/spaces-reviews` | `routers/spaces.py`, `routers/reviews.py`, `services/review_grouping.py` |
| 개발자 B | 본인 | `feature/reservation-cart` | `routers/reservations.py`, `routers/recommendations.py`, `routers/cart.py`, `routers/checkout.py`, `services/recommendation.py` |

`models/schemas.py`, `data/seed.py`, `app/main.py`는 공용 파일이라 수정 필요 시 반드시 상대방에게 먼저 알리고 진행.

## 4. 팀원(개발자 A)이 해야 할 것

레포를 처음 받는 것이므로 pull이 아니라 clone부터.
```
git clone https://github.com/<계정명>/SpaceMate.git
cd SpaceMate
git checkout -b feature/spaces-reviews
```

## 5. 다음 단계 (각자 트랙)

- 개발자 A: `GET /spaces` 필터/정렬 → `GET /spaces/{id}` → `GET /reviews/{space_id}` → AI 후기 그룹핑 API 순
- 개발자 B: `GET /spaces/{id}/slots` → `POST /reservations` → `POST /recommendations` → `POST /cart`류 → `POST /checkout` 순
- 작은 단위로 자주 커밋 & PR, 더미 응답부터 먼저 올려서 UI 담당자가 바로 붙여볼 수 있게 하기
