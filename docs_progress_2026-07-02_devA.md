# SpaceMate 개발 진행내역 (2026-07-02, Dev A 트랙)

FR-01(AI 후기 그룹핑)을 중심으로 진행한 작업 요약. 브랜치: `main` 직커밋(팀 실제 관행 반영). 최신 커밋 `d7c725d` 기준.

## 1. 발견 & 수정한 사전 버그

작업 시작 전 로컬에서 서버가 아예 안 켜지는 문제가 있어서 먼저 해결함.

- **`data/seed.py`**: `514b190`에서 `Review` 모델에 `rating`/`created_at`이 필수 필드로 추가됐는데, 하드코딩 후기 30개엔 값이 안 채워져 있어서 import 시점에 `pydantic.ValidationError`로 서버가 죽는 상태였음. → 채워서 수정 (merge 과정에서 Dev B가 별도로 고친, sp03 placeholder 제거 + 실데이터 대체 버전으로 최종 채택).
- **`data/reviews_loader.py`**: CSV가 BOM 포함(`utf-8-sig`)으로 저장돼 있는데 `encoding="utf-8"`로 열어서 `row["id"]`에서 `KeyError` → `except: continue`가 삼켜서 367건 전부 조용히 스킵되던 버그. `encoding="utf-8-sig"`로 수정. 작성자 닉네임 마스킹(`mask_nickname()`)도 같이 적용.
- 이 두 버그는 merge 과정에서 Dev B가 올린 버전에도 동일하게 남아있었던 걸 발견해서, 수정본 기준으로 병합함.

## 2. FR-01 (AI 후기 그룹핑) 신규 구현

### 라우터 (`routers/reviews.py`) — 기존 빈 스텁이었음
- `GET /reviews/{space_id}` — 후기 원문 리스트 (없는 공간은 404)
- `GET /reviews/{space_id}/groups` — 승인된 그룹만 반환
- `POST /admin/generate-groups` — 그룹핑 실행. `body: {space_id, force}`
  - 이미 생성된 그룹 있으면 `force=true` 아닌 한 LLM 재호출 안 함 (비용 절감)
  - 성공 시 캐시 저장, 실패 시 캐시 → 그마저 없으면 원문 순으로 폴백 (NFR 8.2)

### `main.py` 변경 (공용 파일)
`app.include_router(reviews.admin_router, prefix="/admin", ...)` 한 줄 추가 — admin 엔드포인트 등록용.

### `services/review_grouping.py` — 기존 빈 스텁이었음
- 닉네임 마스킹, LangChain+ChatGPT 그룹핑, 캐시 저장/로드 구현
- **PRD NFR 8.3 대응**: sp03처럼 리뷰 367건인 공간은 전부 프롬프트에 넣으면 토큰 예산(4K) 3~5배 초과 → 별점 버킷을 고르게 순회하는 방식으로 50건 샘플링 (`_sample_reviews_for_prompt`). 별점 적은 쪽(1~2점)이 먼저 다 채워지고 남는 자리만 많은 쪽(5점)이 채우는 구조라, 낮은 평점 후기가 누락되지 않음.
- **NFR 7.1/8.3 대응**: `timeout=10`, `max_tokens=1000` 추가 (원래 없어서 응답 안 오면 무한대기하던 문제 수정)
- **NFR 8.1 대응**: LLM이 반환한 `label`이 고정 5개(호스트/청결/접근성/비품/기타) 밖이거나 `review_ids`가 실제 프롬프트에 없던 값이면 필터링
- **FR-02 반영**: PRD "AI 요약은 자동 노출(승인 절차 없음)"에 맞춰 생성 즉시 `status="approved"`. 원래 있던 관리자 승인 큐(pending→approve/reject)는 팀 합의로 제거함 (화면도 안 만들기로 함).
- 라벨 최종 확정: 호스트/청결/접근성/비품/기타 (2026-07-02)

### `models/schemas.py` 변경 (공용 파일)
`ReviewGroup`에 `review_ids: list[str] = []` 필드 추가 (optional, 기존 코드 영향 없음) — 요약 근거 리뷰 추적용.

### `data/repository.py` 변경
`add_review_group`/`update_review_group_status`/`list_pending_groups`(승인 큐용) 삭제 → `replace_review_groups(space_id, groups)`로 대체. 같은 공간에 그룹핑 재실행해도 그룹이 중복 누적되지 않고 통째로 교체됨.

### `.gitignore`
`app/data/cache/`를 커밋 대상에서 제외하던 줄 삭제 — 그룹핑 캐시(`review_groups_{space_id}.json`)가 "발표 당일 라이브 API 실패 대비 안전장치" 역할을 하려면 커밋이 돼야 하는데 gitignore에 걸려있으면 그 목적이 무의미해짐.

## 3. 파일 배치 (기존 로컬 작업물 반영)
- `data/reviews_loader.py`, `data/spacecloud_reviews.csv`(367건 실제 크롤링 후기) — 신규 배치
- `scripts/spacecloud_review_crawler_api.py` — 크롤러 스크립트, 앱 런타임과 무관해서 `app/` 밖 별도 폴더로 분리
- `requirements.txt`에 `requests` 추가 (크롤러 스크립트 의존성 누락돼있었음)

## 4. 검증
- 샘플링/라벨·id 검증/캐시 저장로드/중복방지 로직: 별도 스크립트로 단위 테스트 통과
- 실제 LLM 호출(`POST /admin/generate-groups`): 로컬(Dev A 컴퓨터)에서는 Windows 보안 정책이 `openai` SDK의 `jiter` 네이티브 DLL을 차단해서 확인 불가 → **Dev B 컴퓨터에서 정상 동작 확인 완료**
- sp03 실제 크롤링 후기 367건 로딩 테스트 통과 (`author` 마스킹 정상 적용 확인)

## 5. 알려진 이슈 / 의도적으로 보류한 것
- **리뷰 본문 내 개인정보 마스킹 미적용**: 작성자명만 마스킹되고 리뷰 내용(전화번호 등)은 그대로 프롬프트/화면에 노출됨. NFR 7.2 요구사항이지만 시간 관계상 팀 판단으로 스킵.
- **PRD 기술스택(Chroma/RAG)과 실제 구현 차이**: PRD엔 "벡터DB: Chroma(후기 RAG 전용)"라고 돼있지만 실제론 RAG 없이 리뷰를 샘플링해 프롬프트에 직접 주입하는 방식. 기능상 문제는 없으나, 발표자료(AI 아키텍처 슬라이드)에서 표현 맞출 필요 있음.
- **Dev A 컴퓨터의 jiter 차단 문제**: 미해결. 캐시 폴백으로 결과 화면은 정상 작동하지만, 그 컴퓨터로 "AI가 실시간으로 그룹핑하는" 라이브 시연은 어려움.

## 6. 남은 작업 (우선순위순)
1. Dev B 컴퓨터에서 생성된 `app/data/cache/review_groups_sp03.json` 커밋 (데모 안전장치 실체화)
2. Dev B의 `repository.py`/`spaces.py` 로컬 변경사항, `frontend/` 폴더(현재 미추적) 커밋/push
3. 배포 준비: `main.py`의 `allow_origins=["*"]`를 실제 Vercel 도메인으로 좁히기, `OPENAI_API_KEY`를 Render/Railway 환경변수로 설정, 시작 명령 설정
4. 프론트-백엔드 연동 확인 (`API_REFERENCE_devB.md` 기준)
5. 나머지 산출물(PPT, IA, wireframe, AI 아키텍처 다이어그램) 준비

## 커밋 히스토리 (이번 트랙)
```
0286a99 fix: seed.py 필수필드 수정 + FR-01 리뷰 그룹핑 라우터/로더 연동
2425e2f merge: Dev B FR-08/sp03 실데이터 병합 + reviews_loader 버그수정본 유지 + FR-01 리뷰 라우터 연동
d7c725d fix: review_grouping.py 토큰예산/타임아웃/라벨·id검증/캐시연동/재호출방지 반영, FR-01 승인절차 제거
```
