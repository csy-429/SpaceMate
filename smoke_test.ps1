[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$base = "http://127.0.0.1:8000"
$sessionId = "smoketest-" + (Get-Random)

function Step($title) {
    Write-Host ""
    Write-Host "=== $title ===" -ForegroundColor Cyan
}

Step "1. 공간 목록 (파티룸, 인기순)"
$list = Invoke-RestMethod -Uri "$base/spaces?type=파티룸&sort=popularity" -Method Get
$list | ConvertTo-Json -Depth 3
if ($list.count -lt 1) { Write-Host "FAIL: 목록이 비어있음" -ForegroundColor Red; exit 1 }

Step "2. 공간 상세 (sp03)"
$detail = Invoke-RestMethod -Uri "$base/spaces/sp03" -Method Get
Write-Host ("이름: " + $detail.space.name)
Write-Host ("review_mode: " + $detail.review_mode + " / 후기 수: " + $detail.reviews.Count)
if ($detail.reviews.Count -lt 300) { Write-Host "WARN: 후기 수가 예상(367)보다 적음" -ForegroundColor Yellow }

Step "3. 슬롯 조회 (sp03, 평일)"
$slotDate = "2026-07-13"
$slots = Invoke-RestMethod -Uri "$base/reservations/sp03/slots?date=$slotDate" -Method Get
Write-Host ("is_weekend: " + $slots.is_weekend + " / 0시 요금: " + $slots.hourly_slots[0].price + " / 패키지가: " + $slots.package.price)

Step "4. 예약 생성 (hourly, 20시부터 3시간, 8인 -> capacity 10 이내)"
$resBody = @{
    space_id = "sp03"
    date = $slotDate
    reservation_type = "hourly"
    start_hour = 20
    hours = 3
    guest_count = 8
} | ConvertTo-Json
$reservation = Invoke-RestMethod -Uri "$base/reservations" -Method Post -Body $resBody -ContentType "application/json; charset=utf-8"
$reservation | ConvertTo-Json
$expectedPrice = 13000 * 3 + (8 - 6) * 10000  # 평일요금 x 3시간 + 초과인원(8-6)x10000
if ($reservation.total_price -ne $expectedPrice) {
    Write-Host "FAIL: 예상 가격 $expectedPrice, 실제 $($reservation.total_price)" -ForegroundColor Red
} else {
    Write-Host "가격 계산 정상 ($expectedPrice)" -ForegroundColor Green
}

Step "5. 예약을 장바구니에 담기 (공간 항목)"
$cartSpaceBody = @{
    session_id = $sessionId
    item_type = "space"
    ref_id = $reservation.reservation_id
    quantity = 1
} | ConvertTo-Json
$cartSpaceEntry = Invoke-RestMethod -Uri "$base/cart" -Method Post -Body $cartSpaceBody -ContentType "application/json; charset=utf-8"
$cartSpaceEntry | ConvertTo-Json

Step "6. 보완상품 추천"
$recBody = @{ space_type = "파티룸"; capacity = 8; time_slot = "20:00~23:00" } | ConvertTo-Json
$rec = Invoke-RestMethod -Uri "$base/recommendations" -Method Post -Body $recBody -ContentType "application/json; charset=utf-8"
Write-Host ("source: " + $rec.source + " / 추천 상품 수: " + $rec.products.Count)
$rec.products | ForEach-Object { Write-Host (" - " + $_.id + " " + $_.name + " " + $_.price + "원") }
if ($rec.products.Count -lt 1) { Write-Host "FAIL: 추천 상품이 없음" -ForegroundColor Red; exit 1 }

Step "7. 추천 상품 1개 장바구니에 담기"
$firstProduct = $rec.products[0]
$cartProductBody = @{
    session_id = $sessionId
    item_type = "product"
    ref_id = $firstProduct.id
    quantity = 1
} | ConvertTo-Json
$cartProductEntry = Invoke-RestMethod -Uri "$base/cart" -Method Post -Body $cartProductBody -ContentType "application/json; charset=utf-8"
$cartProductEntry | ConvertTo-Json

Step "8. 장바구니 조회 (아이템 2개 있어야 함: 공간+상품)"
$cart = Invoke-RestMethod -Uri "$base/cart/$sessionId" -Method Get
Write-Host ("장바구니 아이템 수: " + $cart.Count)
if ($cart.Count -ne 2) { Write-Host "FAIL: 아이템 수가 2가 아님" -ForegroundColor Red }

Step "9. 통합결제"
$checkoutBody = @{ session_id = $sessionId } | ConvertTo-Json
$order = Invoke-RestMethod -Uri "$base/checkout" -Method Post -Body $checkoutBody -ContentType "application/json; charset=utf-8"
$order | ConvertTo-Json -Depth 3
$expectedTotal = $reservation.total_price + $firstProduct.price
if ($order.total_price -ne $expectedTotal) {
    Write-Host "FAIL: 예상 합계 $expectedTotal, 실제 $($order.total_price)" -ForegroundColor Red
} else {
    Write-Host "결제 합계 정상 ($expectedTotal = 예약 $($reservation.total_price) + 상품 $($firstProduct.price))" -ForegroundColor Green
}

Step "10. 결제 후 장바구니 비워졌는지 확인"
$cartAfter = Invoke-RestMethod -Uri "$base/cart/$sessionId" -Method Get
Write-Host ("결제 후 장바구니 아이템 수: " + $cartAfter.Count)
if ($cartAfter.Count -ne 0) { Write-Host "FAIL: 결제 후에도 장바구니가 안 비워짐" -ForegroundColor Red } else { Write-Host "정상적으로 비워짐" -ForegroundColor Green }

Write-Host ""
Write-Host "=== 통테스트 완료 ===" -ForegroundColor Cyan
