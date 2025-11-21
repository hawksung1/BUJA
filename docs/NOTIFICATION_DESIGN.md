# 알림 시스템 설계

> BUJA의 자율적 Agent 알림 제공 방법

## 📱 알림 제공 방법

Streamlit 기반 웹 애플리케이션에서 알림을 제공하는 **다층적 접근 방식**을 사용합니다.

## 🎯 알림 전략 (우선순위별)

### 1. **채팅 메시지로 저장** (기본 방식) ✅

**이미 구현된 방식 활용**

```python
# 모니터링 서비스에서 알림 생성 시
await chat_service.save_message(
    user_id=user_id,
    role="assistant",
    content=f"🔔 자동 모니터링 알림:\n\n{message}",
    project_id=None  # 시스템 알림은 프로젝트 없음
)
```

**장점**:
- ✅ 이미 구현되어 있음
- ✅ 대화 기록으로 남음
- ✅ 사용자가 나중에 다시 확인 가능
- ✅ Agent와의 대화 맥락 유지

**단점**:
- ❌ 사용자가 채팅 페이지에 들어가야 확인 가능
- ❌ 실시간 알림 느낌 부족

**사용 시나리오**:
- 포트폴리오 모니터링 결과
- 목표 진행률 업데이트
- 리밸런싱 권고
- 주간/월간 리포트

---

### 2. **사이드바 알림 배지** (시각적 표시) ⭐

**사이드바에 읽지 않은 알림 개수 표시**

```python
# src/utils/sidebar.py에 추가

def _render_notification_badge(user_id: int):
    """사이드바에 알림 배지 표시"""
    from src.services.notification_service import NotificationService
    
    notification_service = NotificationService()
    unread_count = run_async(
        notification_service.get_unread_count(user_id)
    )
    
    if unread_count > 0:
        st.markdown(f"""
        <div style="
            position: relative;
            display: inline-block;
            margin-bottom: 0.5rem;
        ">
            <a href="/pages/notifications.py" style="
                display: flex;
                align-items: center;
                padding: 0.5rem;
                background-color: rgba(255, 87, 34, 0.1);
                border-radius: 0.5rem;
                text-decoration: none;
                color: inherit;
            ">
                <span style="font-size: 1.2rem;">🔔</span>
                <span style="margin-left: 0.5rem; flex: 1;">알림</span>
                <span style="
                    background-color: #ff5722;
                    color: white;
                    border-radius: 50%;
                    width: 1.5rem;
                    height: 1.5rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 0.75rem;
                    font-weight: bold;
                ">{unread_count}</span>
            </a>
        </div>
        """, unsafe_allow_html=True)
```

**장점**:
- ✅ 모든 페이지에서 알림 존재 확인 가능
- ✅ 시각적으로 눈에 띔
- ✅ 클릭하면 알림 페이지로 이동

**단점**:
- ❌ 새로고침해야 업데이트됨 (Streamlit 제한)

**UI 위치**:
```
사이드바 상단 (메뉴 위)
┌─────────────────┐
│ 🔔 알림 [3]     │  ← 여기
├─────────────────┤
│ 메뉴            │
│ 🤖 에이전트 채팅 │
│ 📊 대시보드     │
└─────────────────┘
```

---

### 3. **별도 알림 페이지** (상세 확인) 📋

**알림 목록을 볼 수 있는 전용 페이지**

```python
# pages/notifications.py (신규 생성)

"""
알림 페이지
"""
import streamlit as st
from src.middleware import auth_middleware
from src.services.notification_service import NotificationService
from src.utils.async_helpers import run_async

st.set_page_config(
    page_title="알림 - BUJA",
    page_icon="🔔",
    layout="wide"
)

user = auth_middleware.get_current_user()
if not user:
    st.switch_page("pages/login.py")
    st.stop()

notification_service = NotificationService()

st.title("🔔 알림")

# 알림 필터
col1, col2 = st.columns([3, 1])
with col1:
    filter_type = st.selectbox(
        "필터",
        ["전체", "읽지 않음", "읽음", "보관됨"],
        key="notification_filter"
    )
with col2:
    if st.button("모두 읽음 처리"):
        run_async(notification_service.mark_all_as_read(user.id))
        st.rerun()

# 알림 목록
notifications = run_async(
    notification_service.get_user_notifications(
        user.id,
        unread_only=(filter_type == "읽지 않음")
    )
)

if notifications:
    for notification in notifications:
        with st.container():
            # 알림 카드
            is_unread = notification.status == "unread"
            border_color = "#ff5722" if is_unread else "transparent"
            
            st.markdown(f"""
            <div style="
                border-left: 4px solid {border_color};
                padding: 1rem;
                margin-bottom: 0.5rem;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 0.5rem;
            ">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0; color: {'#fff' if is_unread else '#aaa'};">
                            {notification.title}
                        </h4>
                        <p style="margin: 0.5rem 0 0 0; color: #ccc;">
                            {notification.message}
                        </p>
                        <small style="color: #888;">
                            {notification.created_at.strftime('%Y-%m-%d %H:%M')}
                        </small>
                    </div>
                    <div>
                        {f'<span style="background: #ff5722; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem;">읽지 않음</span>' if is_unread else ''}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 액션 버튼
            col1, col2 = st.columns([1, 1])
            with col1:
                if is_unread and st.button("읽음 처리", key=f"read_{notification.id}"):
                    run_async(notification_service.mark_as_read(notification.id, user.id))
                    st.rerun()
            with col2:
                if st.button("삭제", key=f"delete_{notification.id}"):
                    run_async(notification_service.delete(notification.id, user.id))
                    st.rerun()
            
            st.markdown("---")
else:
    st.info("알림이 없습니다.")
```

**장점**:
- ✅ 모든 알림을 한눈에 확인
- ✅ 읽음/읽지 않음 관리
- ✅ 알림 히스토리 보관

**단점**:
- ❌ 사용자가 직접 페이지에 들어가야 함

---

### 4. **Streamlit Toast 알림** (실시간 표시) ⚡

**Streamlit 1.28+의 st.toast 사용**

```python
# 페이지 로드 시 새 알림이 있으면 Toast 표시

# agent_chat.py 상단에 추가
if "notifications_checked" not in st.session_state:
    notification_service = NotificationService()
    new_notifications = run_async(
        notification_service.get_user_notifications(
            user.id,
            unread_only=True,
            limit=5
        )
    )
    
    if new_notifications:
        for notif in new_notifications:
            st.toast(
                f"🔔 {notif.title}\n{notif.message[:50]}...",
                icon="🔔"
            )
    
    st.session_state.notifications_checked = True
```

**장점**:
- ✅ 실시간 알림 느낌
- ✅ 사용자가 페이지에 있으면 즉시 확인 가능
- ✅ 구현 간단

**단점**:
- ❌ Streamlit 1.28+ 필요
- ❌ 페이지 새로고침 시에만 표시
- ❌ 알림이 많으면 스팸 느낌

**사용 시나리오**:
- 긴급한 리스크 경고
- 목표 달성 임박 알림

---

### 5. **브라우저 알림** (선택적) 🌐

**Web Notification API 사용 (사용자 권한 필요)**

```python
# pages/agent_chat.py에 JavaScript 추가

def render_browser_notification_script():
    """브라우저 알림 스크립트"""
    st.markdown("""
    <script>
    // 알림 권한 요청
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
    
    // 새 알림이 있으면 브라우저 알림 표시
    function showBrowserNotification(title, message) {
        if (Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/favicon.ico',
                badge: '/favicon.ico'
            });
        }
    }
    
    // 주기적으로 새 알림 체크 (예: 5분마다)
    setInterval(function() {
        // API 호출하여 새 알림 확인
        fetch('/api/notifications/check')
            .then(response => response.json())
            .then(data => {
                if (data.has_new) {
                    showBrowserNotification(data.title, data.message);
                }
            });
    }, 5 * 60 * 1000); // 5분
    </script>
    """, unsafe_allow_html=True)
```

**장점**:
- ✅ 사용자가 다른 탭에 있어도 알림
- ✅ 데스크톱 알림 느낌

**단점**:
- ❌ 사용자 권한 필요
- ❌ 모바일 지원 제한적
- ❌ 구현 복잡도 높음

**사용 시나리오**:
- 매우 긴급한 알림 (선택적)

---

### 6. **카카오톡 알림** (선택적) 💬

**카카오톡 비즈니스 메시지 API 사용**

```python
# src/services/kakao_notification_service.py (선택적)

import httpx
from typing import Optional
from config.settings import settings
from config.logging import get_logger

logger = get_logger(__name__)


class KakaoNotificationService:
    """카카오톡 알림 서비스"""
    
    def __init__(self):
        self.api_key = settings.kakao_business_api_key
        self.template_id = settings.kakao_template_id
        self.base_url = "https://kapi.kakao.com"
    
    async def send_notification(
        self,
        user_phone: str,  # 또는 카카오톡 ID
        title: str,
        message: str,
        button_text: Optional[str] = None,
        button_url: Optional[str] = None
    ) -> bool:
        """
        카카오톡 알림 전송
        
        Args:
            user_phone: 사용자 전화번호 (또는 카카오톡 ID)
            title: 알림 제목
            message: 알림 메시지
            button_text: 버튼 텍스트 (선택)
            button_url: 버튼 링크 (선택)
        
        Returns:
            전송 성공 여부
        """
        try:
            # 1. 액세스 토큰 발급 (또는 저장된 토큰 사용)
            access_token = await self._get_access_token()
            
            # 2. 알림톡 템플릿 메시지 전송
            url = f"{self.base_url}/v2/api/talk/message/send"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # 템플릿 변수 설정
            template_args = {
                "title": title,
                "message": message
            }
            
            payload = {
                "receiver_uuids": [user_phone],  # 또는 receiver_id
                "template_id": self.template_id,
                "template_args": template_args
            }
            
            if button_text and button_url:
                payload["button"] = {
                    "text": button_text,
                    "url": button_url
                }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                logger.info(f"Kakao notification sent to {user_phone}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send Kakao notification: {e}", exc_info=True)
            return False
    
    async def _get_access_token(self) -> str:
        """카카오 API 액세스 토큰 발급"""
        # 토큰은 캐시하거나 Redis에 저장하여 재사용
        # 여기서는 간단히 API 키를 사용 (실제로는 OAuth 2.0 필요)
        return self.api_key
```

**필요한 설정**:
1. 카카오 비즈니스 계정 등록
2. 카카오 비즈니스 채널 생성
3. API 키 발급
4. 알림톡 템플릿 등록 및 승인
5. 사용자 동의 및 카카오톡 ID/전화번호 수집

**장점**:
- ✅ 한국 사용자에게 친숙한 채널
- ✅ 높은 열람률
- ✅ 실시간 알림
- ✅ 버튼으로 앱 바로 이동 가능

**단점**:
- ❌ 카카오 비즈니스 계정 필요 (유료 가능)
- ❌ 템플릿 승인 필요 (시간 소요)
- ❌ 사용자 카카오톡 ID/전화번호 수집 필요
- ❌ 개인정보 보호법 준수 필요
- ❌ API 사용 제한 및 요금 가능

**사용 시나리오**:
- 긴급 리스크 경고
- 목표 달성 임박 알림
- 중요한 포트폴리오 변경 사항

**구현 단계**:
1. 카카오 비즈니스 계정 등록
2. 템플릿 작성 및 승인 대기
3. 사용자 동의 수집 (온보딩에 추가)
4. API 연동 구현
5. 테스트 및 배포

---

### 7. **이메일 알림** (선택적) 📧

**중요한 알림은 이메일로도 전송**

```python
# src/services/email_service.py (선택적)

class EmailService:
    """이메일 알림 서비스"""
    
    async def send_notification_email(
        self,
        user_email: str,
        notification: Notification
    ):
        """이메일 알림 전송"""
        # SMTP 또는 이메일 서비스 API 사용
        # 중요한 알림만 이메일 전송
        pass
```

**장점**:
- ✅ 사용자가 앱에 없어도 확인 가능
- ✅ 중요한 알림 보장

**단점**:
- ❌ 이메일 서비스 설정 필요
- ❌ 스팸 가능성
- ❌ 구현 복잡도 높음

**사용 시나리오**:
- 목표 달성 위험 (높은 우선순위)
- 긴급 리스크 경고

---

## 🎨 권장 구현 조합

### 기본 구현 (필수)

1. **채팅 메시지로 저장** ✅
   - 모든 알림을 채팅 메시지로 저장
   - 사용자가 채팅에서 확인 가능

2. **사이드바 알림 배지** ⭐
   - 읽지 않은 알림 개수 표시
   - 클릭하면 알림 페이지로 이동

3. **알림 페이지** 📋
   - 알림 목록 확인
   - 읽음/삭제 관리

### 고급 기능 (권장)

4. **Toast 알림** ⚡
   - 페이지 로드 시 새 알림 표시
   - Streamlit 1.28+ 필요

5. **카카오톡 알림** 💬 (한국 서비스에 적합)
   - 긴급/중요 알림만
   - 사용자 동의 필요
   - 카카오 비즈니스 계정 필요

### 고급 기능 (선택)

6. **브라우저 알림** 🌐
   - 매우 긴급한 알림만
   - 사용자 설정으로 켜기/끄기

7. **이메일 알림** 📧
   - 매우 중요한 알림만
   - 사용자 설정으로 켜기/끄기

---

## 📊 알림 우선순위별 전략

| 우선순위 | 알림 유형 | 제공 방법 |
|---------|----------|----------|
| **높음** | 리스크 경고, 목표 달성 위험 | 채팅 + 배지 + Toast + 카카오톡 + 이메일 |
| **중간** | 리밸런싱 필요, 목표 진행률 | 채팅 + 배지 + Toast + 카카오톡 |
| **낮음** | 주간 리포트, 월간 리포트 | 채팅 + 배지 |

---

## 🔧 구현 순서

### Phase 1: 기본 알림 (1주)

1. **알림 모델 및 서비스**
   - [ ] Notification 모델 생성
   - [ ] NotificationService 구현
   - [ ] Repository 구현

2. **채팅 메시지 통합**
   - [ ] 모니터링 서비스에서 채팅 메시지로 저장
   - [ ] 알림 메시지 포맷 정의

3. **사이드바 배지**
   - [ ] 사이드바에 알림 배지 추가
   - [ ] 읽지 않은 알림 개수 표시

4. **알림 페이지**
   - [ ] `pages/notifications.py` 생성
   - [ ] 알림 목록 표시
   - [ ] 읽음/삭제 기능

### Phase 2: 고급 알림 (권장, 1주)

5. **Toast 알림**
   - [ ] 페이지 로드 시 새 알림 체크
   - [ ] Toast로 표시

6. **카카오톡 알림** (한국 서비스 권장)
   - [ ] 카카오 비즈니스 계정 등록
   - [ ] 템플릿 작성 및 승인
   - [ ] 사용자 동의 수집 (온보딩에 추가)
   - [ ] KakaoNotificationService 구현
   - [ ] API 연동 및 테스트

### Phase 3: 추가 알림 (선택, 3일)

7. **브라우저 알림** (선택)
   - [ ] 권한 요청
   - [ ] JavaScript로 주기적 체크
   - [ ] 브라우저 알림 표시

8. **이메일 알림** (선택)
   - [ ] 이메일 서비스 구현
   - [ ] 중요 알림만 이메일 전송

---

## 💡 사용자 경험 흐름

### 시나리오 1: 일반적인 알림

```
1. 백그라운드 모니터링 실행
   ↓
2. 리밸런싱 필요 감지
   ↓
3. 알림 생성 (DB 저장)
   ↓
4. 채팅 메시지로 저장
   ↓
5. 사용자가 다음에 채팅 페이지 접속 시
   - 사이드바에 "🔔 알림 [1]" 배지 표시
   - 채팅에 자동 알림 메시지 표시
   ↓
6. 사용자가 알림 페이지 클릭
   - 알림 상세 확인
   - 읽음 처리
```

### 시나리오 2: 긴급 알림

```
1. 리스크 경고 감지
   ↓
2. 알림 생성 (높은 우선순위)
   ↓
3. 채팅 메시지 저장
   ↓
4. Toast 알림 표시 (페이지에 있으면)
   ↓
5. 이메일 전송 (설정된 경우)
   ↓
6. 사이드바 배지 강조 표시
```

---

## 🎯 최종 권장사항

**1단계 (필수)**: 기본 알림 시스템
- ✅ 채팅 메시지로 저장
- ✅ 사이드바 알림 배지
- ✅ 알림 페이지

**2단계 (권장)**: 실시간 알림 추가
- ⚡ Toast 알림 (페이지 로드 시)
- 💬 카카오톡 알림 (한국 서비스에 매우 효과적)

**3단계 (선택)**: 추가 채널
- 🌐 브라우저 알림 (긴급 알림만)
- 📧 이메일 알림 (중요 알림만)

### 카카오톡 알림 특별 고려사항

**한국 서비스의 경우 카카오톡 알림을 강력히 권장합니다:**
- ✅ 한국 사용자에게 가장 친숙한 채널
- ✅ 높은 열람률 (90% 이상)
- ✅ 실시간 푸시 알림
- ✅ 버튼으로 앱 바로 이동 가능

**구현 전 준비사항:**
1. 카카오 비즈니스 계정 등록 (https://business.kakao.com)
2. 비즈니스 채널 생성
3. 알림톡 템플릿 작성 및 승인 (1-2일 소요)
4. 사용자 동의 수집 (온보딩 프로세스에 추가)
5. 카카오톡 ID 또는 전화번호 수집

**비용:**
- 기본 플랜: 무료 또는 저렴한 요금제
- 메시지당 과금 또는 월 정액제 (카카오 정책 확인 필요)

이렇게 단계적으로 구현하면 사용자 경험을 점진적으로 개선할 수 있습니다.

