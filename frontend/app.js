// SpaceMate 프론트 공용 스크립트.
// 모든 화면(index/detail/recommend/cart/checkout)에서 <script src="app.js"></script>로 불러다 쓴다.

const API_BASE = "https://spacemate-api.onrender.com"; // Render 배포 주소 (2026-07-02)

// 장바구니/결제는 세션ID로 묶이는데, 로그인이 없는 MVP라 브라우저에 고정값 하나 저장해두고
// 화면을 옮겨다녀도 같은 세션ID를 계속 쓰게 한다 (localStorage는 탭/새로고침에도 유지됨).
function getSessionId() {
    let id = localStorage.getItem('spacemate_session_id');
    if (!id) {
        id = 'sess-' + Date.now() + '-' + Math.random().toString(36).slice(2, 10);
        localStorage.setItem('spacemate_session_id', id);
    }
    return id;
}
