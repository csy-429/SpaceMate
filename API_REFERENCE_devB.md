# 개발자 B API 레퍼런스 (예약 · 추천 · 장바구니 · 결제)

베이스 URL: `http://localhost:8000` (배포 시 Render/Railway 도메인으로 교체)

모든 POST 바디는 `Content-Type: application/json`. 프론트는 Vanilla JS `fetch()` 기준으로 예시 작성.

---

## 1. 시간대별 요금 + 패키지 여부 조회

```
GET /reservations/{space_id}/slots?date=YYYY-MM-DD
```

**예시**: `GET /reservations/sp03/slots?date=2026-07-13`

**응답**
```json
{
  "space_id": "sp03",
  "date": "2026-07-13",
  "is_weekend": false,
  "min_hours": 2,
  "capacity": 10,
  "base_capacity": 6,
  "extra_person_fee": 10000,
  "hourly_slots": [
    { "hour": 0, "price": 13000, "available": true },
    { "hour": 1, "price": 13000, "available": true }
  ],
  "package": {
    "price": 100000,
    "time_range": "18:00~익일 08:00",
    "available": true
  }
}
```

- `is_weekend`: 토/일이면 true → 그날은 `price`가 전부 주말 요금(예: sp03은 18,000)
- `package`이 `null`이면 그 공간은 패키지 예약 미제공 (해당 UI 숨기기)
- `capacity`: 최대 인원 (이 이상은 프론트에서 인원 + 버튼 비활성화 권장)
- `base_capacity`: 기준 인원, 이거 넘으면 인당 `extra_person_fee` 추가된다는 걸 프론트에서 안내 문구로 표시

**fetch 예시**
```js
const res = await fetch(`/reservations/${spaceId}/slots?date=${date}`);
const data = await res.json();
```

---

## 2. 예약 생성 (즉시확정)

```
POST /reservations
```

**시간 단위 예약 요청**
```json
{
  "space_id": "sp03",
  "date": "2026-07-13",
  "reservation_type": "hourly",
  "start_hour": 20,
  "hours": 3,
  "guest_count": 2
}
```

**올나잇 패키지 예약 요청** (start_hour/hours 불필요)
```json
{
  "space_id": "sp03",
  "date": "2026-07-12",
  "reservation_type": "package",
  "guest_count": 2
}
```

**응답 (공통)**
```json
{
  "reservation_id": "e169fd3d",
  "space_id": "sp03",
  "date": "2026-07-18",
  "reservation_type": "hourly",
  "start_hour": 20,
  "hours": 3,
  "guest_count": 8,
  "total_price": 74000,
  "status": "confirmed"
}
```

- `status: "confirmed"`가 곧 "결제 완료"임 (목업, 별도 결제 API 없음). 공간만 예약하는 원본 클론 플로우는 이 응답 받는 순간 바로 결제완료 화면으로 넘어가면 됨.
- `guest_count`가 `capacity`를 넘으면 에러 없이 자동으로 `capacity` 값으로 조정되어 저장됨 (프론트는 애초에 + 버튼을 capacity에서 막아두는 게 정석).
- 검증 실패 시 에러 응답: `hours < 2`(시간 단위 최소 2시간), `start_hour` 범위 밖, 해당 공간이 패키지 미제공인데 `reservation_type: "package"`로 요청한 경우 → `400 { "detail": "..." }`

**fetch 예시**
```js
const res = await fetch('/reservations', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ space_id, date, reservation_type: 'hourly', start_hour, hours, guest_count }),
});
const reservation = await res.json();
```

---

## 3. 예약 단건 조회

```
GET /reservations/{reservation_id}
```
응답 형식은 위 예약 생성 응답과 동일. 없는 id면 `404`.

---

## 4. 보완상품 추천

```
POST /recommendations
```

**요청**
```json
{ "space_type": "파티룸", "capacity": 10 }
```

**응답**
```json
{
  "source": "fallback",
  "products": [
    { "id": "pd01", "name": "생일 케이크", "price": 35000, "target_space_types": ["파티룸"] },
    { "id": "pd02", "name": "풍선 데코 세트", "price": 15000, "target_space_types": ["파티룸"] },
    { "id": "pd04", "name": "음향기기 대여", "price": 25000, "target_space_types": ["회의실", "파티룸"] }
  ]
}
```
- 지금은 항상 `source: "fallback"` (LLM 연동 전). 응답 형식은 LLM 붙어도 안 바뀔 예정이라 프론트는 지금 붙여도 됨.
- 예약 완료 직후 화면에서 이걸 호출해서 "추가로 이런 상품 어때요?" 노출.

---

## 5. 장바구니

```
POST   /cart                          — 담기
GET    /cart/{session_id}             — 조회
DELETE /cart/{session_id}/{item_id}   — 삭제
```

**담기 요청**
```json
{ "session_id": "user-abc123", "item_type": "product", "ref_id": "pd01", "quantity": 1 }
```
`item_type`은 `"product"` 또는 `"space"`(이미 확정된 예약을 담을 때 `ref_id`에 `reservation_id`).

**담기 응답**
```json
{ "item_type": "product", "ref_id": "pd01", "quantity": 1, "id": "0626224c" }
```

**조회 응답**: 위 아이템들의 배열.

**삭제**: 응답 `{ "status": "deleted", "item_id": "0626224c" }`

`session_id`는 프론트에서 아무 방식으로 발급해서 유지(로그인 없는 MVP라 임의 문자열 또는 브라우저 세션 하나 고정값으로 써도 됨).

---

## 6. 통합결제 (목업)

```
POST /checkout
```

**요청**
```json
{ "session_id": "user-abc123" }
```

**응답**
```json
{
  "order_id": "714edcdf",
  "session_id": "user-abc123",
  "items": [ { "item_type": "product", "ref_id": "pd01", "quantity": 1, "id": "0626224c" } ],
  "total_price": 35000,
  "status": "completed"
}
```
- 실제 결제 없음, `order_id` 발급 + `completed` 상태만 반환.
- 호출 즉시 서버 쪽 장바구니는 비워짐 — 프론트도 결제 완료 후 장바구니 화면 비우기.
- 분리정산(호스트 수수료 10%) 안내 문구는 백엔드에서 안 내려줌 — 프론트에서 고정 텍스트로 표시.

---

## 참고

- 공간만 예약(장바구니 안 거침) = `POST /reservations` 응답만으로 끝 → **/checkout 호출 불필요**
- 보완상품을 담았을 때만 = `POST /cart` → `POST /checkout` 순서로 진행
- 이 두 흐름이 다른 화면/버튼이라는 걸 UI로 구분해서 보여줘야 함 (PRD·업무분장서 참고)
