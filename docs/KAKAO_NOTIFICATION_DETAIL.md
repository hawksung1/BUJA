# 카카오톡 알림 전송 방식 상세 설명

## 📱 카카오톡 알림의 종류

카카오톡 비즈니스 메시지 API는 크게 **3가지 방식**으로 알림을 전송합니다:

### 1. **알림톡** (Notification Talk) ⭐ **BUJA에 가장 적합**

**작동 방식:**
- 사전에 승인받은 **템플릿 메시지**를 사용
- 사용자의 카카오톡 앱에 **푸시 알림**으로 전달
- 사용자가 카카오톡 채널을 친구 추가하지 않아도 받을 수 있음

**전송 방법:**
```
1. 템플릿 작성 및 카카오 승인 (1-2일 소요)
   예: "포트폴리오 리스크 경고가 발생했습니다. {message}"
   
2. 사용자 전화번호 또는 카카오톡 ID로 전송
   API 호출 → 카카오톡 서버 → 사용자 휴대폰 푸시 알림
   
3. 사용자가 카카오톡 앱에서 메시지 확인
```

**예시 메시지:**
```
[BUJA 투자 상담]
포트폴리오 리스크 경고

현재 포트폴리오의 최대 낙폭이 
설정하신 임계값을 초과했습니다.

자세한 내용은 앱에서 확인하세요.
[앱 바로가기] 버튼
```

**장점:**
- ✅ 친구 추가 불필요
- ✅ 높은 도달률
- ✅ 템플릿 승인 후 안정적 사용
- ✅ 버튼으로 앱 바로 이동 가능

**단점:**
- ❌ 템플릿 사전 승인 필요
- ❌ 템플릿 수정 시 재승인 필요
- ❌ 사용자 전화번호 또는 카카오톡 ID 필요

---

### 2. **친구톡** (Friend Talk)

**작동 방식:**
- 사용자가 **카카오톡 채널을 친구 추가**한 경우에만 가능
- 자유로운 형식의 메시지 전송 가능
- 템플릿 승인 불필요

**전송 방법:**
```
1. 사용자가 BUJA 카카오톡 채널 친구 추가
   
2. 친구 추가한 사용자에게만 메시지 전송
   API 호출 → 카카오톡 서버 → 친구 추가한 사용자에게만 전달
   
3. 사용자가 카카오톡 앱에서 메시지 확인
```

**장점:**
- ✅ 템플릿 승인 불필요
- ✅ 자유로운 메시지 형식
- ✅ 이미지, 버튼 등 다양한 콘텐츠

**단점:**
- ❌ 사용자가 채널 친구 추가해야 함
- ❌ 친구 추가하지 않은 사용자에게는 전송 불가
- ❌ 도달률이 낮을 수 있음

---

### 3. **카카오톡 채널 메시지**

**작동 방식:**
- 카카오톡 채널의 **구독자**에게 공지사항 형태로 전송
- 채널 관리자가 직접 전송

**장점:**
- ✅ 많은 사용자에게 한 번에 전송
- ✅ 공지사항 형태

**단점:**
- ❌ 개인화된 알림에는 부적합
- ❌ 사용자가 채널 구독해야 함

---

## 🎯 BUJA에 권장하는 방식

### 옵션 1: **친구톡** (즉시 사용 가능) ⚡ **추천!**

**템플릿 승인 불필요, 즉시 사용 가능!**

**장점:**
- ✅ **템플릿 승인 불필요** - 즉시 사용 가능!
- ✅ 자유로운 메시지 형식
- ✅ 이미지, 버튼 등 다양한 콘텐츠
- ✅ 승인 대기 시간 없음

**단점:**
- ❌ 사용자가 카카오톡 채널을 친구 추가해야 함
- ❌ 친구 추가하지 않은 사용자에게는 전송 불가
- ❌ 도달률이 친구 추가율에 의존

**적용 방법:**
1. 카카오톡 채널 개설 (즉시 가능)
2. 사용자에게 채널 친구 추가 안내
3. 친구 추가한 사용자에게 즉시 메시지 전송 가능

---

### 옵션 2: **알림톡** (승인 필요)

**템플릿 승인 후 사용 (1-2일 소요)**

**장점:**
- ✅ 친구 추가 불필요
- ✅ 높은 도달률
- ✅ 안정적 운영

**단점:**
- ❌ 템플릿 승인 필요 (1-2일 소요)
- ❌ 템플릿 수정 시 재승인 필요

---

## 🔧 친구톡 구현 상세 (즉시 사용 가능) ⚡

### 1. 카카오톡 채널 개설

1. **카카오 비즈니스 계정 등록**
   - https://business.kakao.com 접속
   - 비즈니스 계정 생성 (무료)

2. **카카오톡 채널 생성**
   - 채널 관리자 센터에서 채널 생성
   - 채널명: "BUJA 투자 상담" 등
   - 채널 설명, 프로필 이미지 설정

3. **채널 ID 확인**
   - 채널 설정에서 채널 ID 확인
   - API 연동에 필요

**소요 시간: 약 30분~1시간 (즉시 가능!)**

---

### 2. 친구톡 API 구현

```python
# src/services/kakao_friend_talk_service.py

import httpx
from typing import Optional, Dict, Any, List
from config.settings import settings
from config.logging import get_logger

logger = get_logger(__name__)


class KakaoFriendTalkService:
    """카카오톡 친구톡 서비스 (템플릿 승인 불필요)"""
    
    def __init__(self):
        # 카카오 비즈니스 API 설정
        self.api_key = settings.kakao_business_api_key
        self.channel_id = settings.kakao_channel_id  # 채널 ID
        self.base_url = "https://kapi.kakao.com"
    
    async def send_friend_talk(
        self,
        user_kakao_id: str,  # 카카오톡 사용자 ID (또는 UUID)
        message: str,
        button_text: Optional[str] = None,
        button_url: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> bool:
        """
        친구톡 메시지 전송 (템플릿 승인 불필요)
        
        Args:
            user_kakao_id: 카카오톡 사용자 ID (채널 친구 추가한 사용자)
            message: 전송할 메시지
            button_text: 버튼 텍스트 (선택)
            button_url: 버튼 링크 (선택)
            image_url: 이미지 URL (선택)
        
        Returns:
            전송 성공 여부
        """
        try:
            # 액세스 토큰 발급
            access_token = await self._get_access_token()
            
            # 친구톡 전송 API 호출
            url = f"{self.base_url}/v1/api/talk/friends/message/send"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # 메시지 구성
            payload = {
                "receiver_uuids": [user_kakao_id],
                "template_object": {
                    "object_type": "text",
                    "text": message,
                    "link": {
                        "web_url": button_url or "https://buja.app",
                        "mobile_web_url": button_url or "https://buja.app"
                    }
                }
            }
            
            # 버튼 추가
            if button_text and button_url:
                payload["template_object"]["buttons"] = [
                    {
                        "title": button_text,
                        "link": {
                            "web_url": button_url,
                            "mobile_web_url": button_url
                        }
                    }
                ]
            
            # 이미지 추가
            if image_url:
                payload["template_object"]["image_url"] = image_url
                payload["template_object"]["object_type"] = "feed"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Kakao friend talk sent to {user_kakao_id}: {result}")
                return True
                
        except httpx.HTTPStatusError as e:
            error_msg = e.response.text
            logger.error(f"Kakao API HTTP error: {e.response.status_code} - {error_msg}")
            
            # 친구 추가하지 않은 사용자인 경우
            if "not a friend" in error_msg.lower() or e.response.status_code == 403:
                logger.warning(f"User {user_kakao_id} has not added the channel as friend")
            
            return False
        except Exception as e:
            logger.error(f"Failed to send Kakao friend talk: {e}", exc_info=True)
            return False
    
    async def send_risk_alert(
        self,
        user_kakao_id: str,
        risk_type: str,
        max_drawdown: float,
        volatility: float
    ) -> bool:
        """리스크 경고 친구톡 전송"""
        message = f"""🔔 포트폴리오 리스크 경고

{risk_type}이(가) 설정하신 임계값을 초과했습니다.

현재 상태:
• 최대 낙폭: {max_drawdown:.2f}%
• 변동성: {volatility:.2f}%

자세한 내용은 앱에서 확인하세요."""
        
        return await self.send_friend_talk(
            user_kakao_id=user_kakao_id,
            message=message,
            button_text="앱에서 확인하기",
            button_url="https://buja.app/agent_chat"
        )
    
    async def send_goal_progress(
        self,
        user_kakao_id: str,
        goal_name: str,
        progress: float,
        target_amount: float,
        current_amount: float,
        days_remaining: int
    ) -> bool:
        """목표 진행률 친구톡 전송"""
        message = f"""📊 목표 진행률 업데이트

{goal_name} 목표의 현재 진행률은 {progress:.1f}%입니다.

목표 금액: {target_amount:,.0f}원
현재 금액: {current_amount:,.0f}원
남은 기간: {days_remaining}일

목표 달성을 응원합니다! 💪"""
        
        return await self.send_friend_talk(
            user_kakao_id=user_kakao_id,
            message=message,
            button_text="대시보드에서 확인하기",
            button_url="https://buja.app/dashboard"
        )
    
    async def _get_access_token(self) -> str:
        """카카오 API 액세스 토큰 발급"""
        # OAuth 2.0 인증 플로우
        # 실제 구현 시 토큰 관리 필요
        return self.api_key
```

### 3. 사용자 카카오톡 ID 수집

**온보딩에 추가:**

```python
# pages/onboarding.py에 추가

# 카카오톡 알림 설정
st.markdown("### 카카오톡 알림 설정 (선택)")

kakao_notification_enabled = st.checkbox(
    "카카오톡으로 중요한 알림 받기",
    value=False,
    help="BUJA 카카오톡 채널을 친구 추가하면 알림을 받을 수 있습니다."
)

if kakao_notification_enabled:
    # 카카오톡 채널 친구 추가 안내
    st.info("""
    📱 **카카오톡 채널 친구 추가 방법:**
    
    1. 카카오톡 앱에서 "BUJA 투자 상담" 검색
    2. 채널 프로필에서 "친구 추가" 클릭
    3. 친구 추가 완료 후 알림을 받을 수 있습니다
    
    또는 아래 버튼을 클릭하세요:
    """)
    
    # 카카오톡 채널 링크
    channel_url = "https://pf.kakao.com/_xxxxx"  # 실제 채널 URL
    st.markdown(f'<a href="{channel_url}" target="_blank">카카오톡 채널 친구 추가하기</a>', unsafe_allow_html=True)
    
    # 카카오 로그인으로 사용자 ID 자동 수집 (선택)
    if st.button("카카오 로그인으로 연동"):
        # 카카오 로그인 API 호출
        # 사용자 ID 자동 수집
        pass
```

### 4. 친구 추가 확인 및 전송

```python
# 모니터링 서비스에서 사용

from src.services.kakao_friend_talk_service import KakaoFriendTalkService

kakao_service = KakaoFriendTalkService()

# 사용자가 채널 친구 추가했는지 확인
if user.profile and user.profile.kakao_id:
    # 친구톡 전송 시도
    success = await kakao_service.send_risk_alert(
        user_kakao_id=user.profile.kakao_id,
        risk_type="최대 낙폭",
        max_drawdown=15.5,
        volatility=25.3
    )
    
    if not success:
        # 친구 추가하지 않은 경우 대체 알림 (채팅 메시지)
        logger.warning(f"User {user.id} has not added channel, using chat message instead")
        await chat_service.save_message(...)
```

---

## 🔧 알림톡 구현 상세 (참고용)

### 1. 템플릿 작성 예시

**템플릿 1: 리스크 경고**
```
템플릿명: 포트폴리오 리스크 경고
카테고리: 금융/투자

메시지:
[BUJA 투자 상담]
포트폴리오 리스크 경고

{risk_type}이(가) 설정하신 임계값을 초과했습니다.

현재 상태:
- 최대 낙폭: {max_drawdown}%
- 변동성: {volatility}%

자세한 내용은 앱에서 확인하세요.

[앱 바로가기] 버튼
```

**템플릿 2: 목표 진행률**
```
템플릿명: 목표 진행률 업데이트
카테고리: 금융/투자

메시지:
[BUJA 투자 상담]
목표 진행률 업데이트

{goal_name} 목표의 현재 진행률은 {progress}%입니다.

목표 금액: {target_amount}원
현재 금액: {current_amount}원
남은 기간: {days_remaining}일

[앱에서 확인하기] 버튼
```

**템플릿 3: 리밸런싱 권고**
```
템플릿명: 리밸런싱 권고
카테고리: 금융/투자

메시지:
[BUJA 투자 상담]
리밸런싱 권고

현재 포트폴리오의 자산 배분이 
목표 비중에서 벗어났습니다.

권장 조치:
- {asset_type1}: {current_pct}% → {target_pct}%
- {asset_type2}: {current_pct}% → {target_pct}%

[포트폴리오 확인하기] 버튼
```

### 2. API 호출 예시

```python
# src/services/kakao_notification_service.py

import httpx
from typing import Optional, Dict, Any
from config.settings import settings
from config.logging import get_logger

logger = get_logger(__name__)


class KakaoNotificationService:
    """카카오톡 알림톡 서비스"""
    
    def __init__(self):
        # 카카오 비즈니스 API 설정
        self.api_key = settings.kakao_business_api_key
        self.service_id = settings.kakao_service_id
        self.base_url = "https://kapi.kakao.com"
        
        # 템플릿 ID (승인 후 발급)
        self.templates = {
            "risk_alert": settings.kakao_template_risk_alert,
            "goal_progress": settings.kakao_template_goal_progress,
            "rebalancing": settings.kakao_template_rebalancing,
        }
    
    async def send_risk_alert(
        self,
        user_phone: str,
        risk_type: str,
        max_drawdown: float,
        volatility: float
    ) -> bool:
        """리스크 경고 알림톡 전송"""
        template_id = self.templates["risk_alert"]
        
        # 템플릿 변수
        template_args = {
            "risk_type": risk_type,
            "max_drawdown": f"{max_drawdown:.2f}",
            "volatility": f"{volatility:.2f}"
        }
        
        return await self._send_notification_talk(
            user_phone=user_phone,
            template_id=template_id,
            template_args=template_args,
            button_text="앱 바로가기",
            button_url="https://buja.app/agent_chat"
        )
    
    async def send_goal_progress(
        self,
        user_phone: str,
        goal_name: str,
        progress: float,
        target_amount: float,
        current_amount: float,
        days_remaining: int
    ) -> bool:
        """목표 진행률 알림톡 전송"""
        template_id = self.templates["goal_progress"]
        
        template_args = {
            "goal_name": goal_name,
            "progress": f"{progress:.1f}",
            "target_amount": f"{target_amount:,.0f}",
            "current_amount": f"{current_amount:,.0f}",
            "days_remaining": str(days_remaining)
        }
        
        return await self._send_notification_talk(
            user_phone=user_phone,
            template_id=template_id,
            template_args=template_args,
            button_text="앱에서 확인하기",
            button_url="https://buja.app/dashboard"
        )
    
    async def _send_notification_talk(
        self,
        user_phone: str,
        template_id: str,
        template_args: Dict[str, str],
        button_text: Optional[str] = None,
        button_url: Optional[str] = None
    ) -> bool:
        """
        알림톡 전송
        
        Args:
            user_phone: 사용자 전화번호 (010-1234-5678 형식)
            template_id: 승인받은 템플릿 ID
            template_args: 템플릿 변수 딕셔너리
            button_text: 버튼 텍스트 (선택)
            button_url: 버튼 링크 (선택)
        
        Returns:
            전송 성공 여부
        """
        try:
            # 1. 액세스 토큰 발급 (또는 저장된 토큰 사용)
            access_token = await self._get_access_token()
            
            # 2. 알림톡 전송 API 호출
            url = f"{self.base_url}/v2/api/talk/message/send"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # 전화번호 형식 변환 (하이픈 제거)
            phone_number = user_phone.replace("-", "")
            
            payload = {
                "receiver_uuids": [phone_number],  # 또는 receiver_id 사용
                "template_id": template_id,
                "template_args": template_args
            }
            
            # 버튼 추가 (선택)
            if button_text and button_url:
                payload["button"] = {
                    "text": button_text,
                    "url": button_url
                }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Kakao notification sent to {user_phone}: {result}")
                return True
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Kakao API HTTP error: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Failed to send Kakao notification: {e}", exc_info=True)
            return False
    
    async def _get_access_token(self) -> str:
        """
        카카오 API 액세스 토큰 발급
        
        실제로는 OAuth 2.0 인증 플로우를 거쳐야 하지만,
        여기서는 간단히 API 키를 사용 (실제 구현 시 토큰 관리 필요)
        """
        # 토큰은 캐시하거나 Redis에 저장하여 재사용
        # 여기서는 간단히 API 키 반환 (실제로는 OAuth 토큰 필요)
        
        # 실제 구현 예시:
        # 1. 토큰이 캐시에 있으면 반환
        # 2. 없으면 새로 발급
        # 3. 토큰 만료 시간 체크
        
        return self.api_key
```

### 3. 사용자 정보 수집

**온보딩 프로세스에 추가:**

```python
# pages/onboarding.py에 추가

# 카카오톡 알림 수신 동의
st.markdown("### 카카오톡 알림 설정 (선택)")

kakao_notification_enabled = st.checkbox(
    "카카오톡으로 중요한 알림 받기",
    value=False,
    help="리스크 경고, 목표 달성 알림 등을 카카오톡으로 받을 수 있습니다."
)

if kakao_notification_enabled:
    kakao_phone = st.text_input(
        "전화번호",
        placeholder="010-1234-5678",
        help="카카오톡 알림을 받을 전화번호를 입력하세요."
    )
    
    if kakao_phone:
        # 전화번호 형식 검증
        import re
        phone_pattern = re.compile(r'^010-\d{4}-\d{4}$')
        if not phone_pattern.match(kakao_phone):
            st.error("올바른 전화번호 형식을 입력하세요. (010-1234-5678)")
        else:
            # 사용자 프로필에 저장
            user_profile.kakao_phone = kakao_phone
            user_profile.kakao_notification_enabled = True
```

### 4. 모니터링 서비스와 연동

```python
# src/services/portfolio_monitoring_service.py

async def _trigger_agent_action(
    self,
    user_id: int,
    alerts: Dict[str, Any]
):
    """Agent가 자동으로 조치 취하기"""
    from src.agents.autonomous_investment_agent import AutonomousInvestmentAgent
    from src.services.kakao_notification_service import KakaoNotificationService
    
    agent = AutonomousInvestmentAgent()
    kakao_service = KakaoNotificationService()
    
    # 상황에 맞는 메시지 생성
    action_message = self._build_action_message(alerts)
    
    # Agent가 조언 생성
    response = ""
    async for chunk in agent.chat(action_message, context={"user_id": user_id}):
        response += chunk
    
    # 1. 채팅 메시지로 저장
    await self.chat_service.save_message(
        user_id=user_id,
        role="assistant",
        content=f"🔔 자동 모니터링 알림:\n\n{response}",
        project_id=None
    )
    
    # 2. 카카오톡 알림 전송 (사용자가 동의한 경우)
    user = await self.user_repo.get_by_id(user_id)
    if user.profile and user.profile.kakao_notification_enabled:
        if alerts.get("risk_alerts"):
            # 리스크 경고 카카오톡 전송
            await kakao_service.send_risk_alert(
                user_phone=user.profile.kakao_phone,
                risk_type=alerts["risk_alerts"][0]["type"],
                max_drawdown=alerts["risk_alerts"][0]["max_drawdown"],
                volatility=alerts["risk_alerts"][0]["volatility"]
            )
```

---

## 📋 구현 체크리스트

### 친구톡 방식 (즉시 사용 가능) ⚡

**사전 준비 (약 1시간)**
- [ ] 카카오 비즈니스 계정 등록 (무료)
- [ ] 카카오톡 채널 생성
- [ ] 채널 ID 확인
- [ ] API 키 발급
- [ ] 채널 친구 추가 안내 페이지 준비

**개발 (1-2일)**
- [ ] `KakaoFriendTalkService` 구현
- [ ] 온보딩에 채널 친구 추가 안내 추가
- [ ] 사용자 카카오톡 ID 수집 (카카오 로그인 또는 수동 입력)
- [ ] 모니터링 서비스와 연동
- [ ] 친구 추가 확인 로직

**테스트**
- [ ] 친구톡 메시지 전송 테스트
- [ ] 친구 추가하지 않은 사용자 처리 테스트

---

### 알림톡 방식 (승인 필요)

**사전 준비 (1-2일 소요)**
- [ ] 카카오 비즈니스 계정 등록
- [ ] 비즈니스 채널 생성
- [ ] 알림톡 템플릿 작성 (3-5개)
- [ ] 템플릿 승인 대기 (1-2일)
- [ ] API 키 발급

### 개발
- [ ] `KakaoNotificationService` 구현
- [ ] 온보딩에 카카오톡 알림 동의 추가
- [ ] 사용자 전화번호 수집 및 저장
- [ ] 모니터링 서비스와 연동
- [ ] 에러 핸들링 및 재시도 로직

### 테스트
- [ ] 템플릿 메시지 전송 테스트
- [ ] 다양한 시나리오 테스트
- [ ] 에러 케이스 테스트

---

## 💰 비용

카카오톡 알림톡은 일반적으로:
- **무료 플랜**: 제한적 (월 일정 건수 무료)
- **유료 플랜**: 메시지당 과금 또는 월 정액제
- 정확한 요금은 카카오 비즈니스 정책 확인 필요

---

## ⚠️ 주의사항

1. **개인정보 보호**
   - 사용자 전화번호 수집 시 명시적 동의 필요
   - 개인정보 보호법 준수

2. **템플릿 승인**
   - 템플릿 수정 시 재승인 필요
   - 승인 전까지는 테스트만 가능

3. **스팸 방지**
   - 과도한 알림 전송 시 스팸으로 분류될 수 있음
   - 중요 알림만 전송하도록 필터링 필요

4. **에러 핸들링**
   - API 호출 실패 시 대체 알림 방법 사용
   - 재시도 로직 구현

---

## 🎯 요약 및 권장사항

### 즉시 사용 가능: **친구톡** ⚡

**장점:**
- ✅ 템플릿 승인 불필요 - **즉시 사용 가능!**
- ✅ 자유로운 메시지 형식
- ✅ 승인 대기 시간 없음

**단점:**
- ❌ 사용자가 채널 친구 추가 필요
- ❌ 친구 추가율에 따라 도달률 변동

**적용 시나리오:**
- 빠른 프로토타입 및 테스트
- 사용자 친구 추가를 유도할 수 있는 서비스
- 템플릿 승인을 기다릴 수 없는 경우

---

### 승인 후 사용: **알림톡**

**장점:**
- ✅ 친구 추가 불필요
- ✅ 높은 도달률
- ✅ 안정적 운영

**단점:**
- ❌ 템플릿 승인 필요 (1-2일 소요)
- ❌ 템플릿 수정 시 재승인 필요

**적용 시나리오:**
- 안정적인 운영이 필요한 프로덕션 환경
- 친구 추가를 유도하기 어려운 경우
- 승인 대기 시간이 문제되지 않는 경우

---

## 💡 BUJA 권장 전략

**1단계: 친구톡으로 시작** (즉시 구현)
- 빠르게 구현하여 테스트
- 사용자에게 채널 친구 추가 유도
- 친구 추가율 모니터링

**2단계: 알림톡 추가** (선택)
- 친구 추가율이 낮은 경우
- 더 넓은 도달률이 필요한 경우
- 템플릿 승인 후 알림톡 추가

**하이브리드 방식:**
- 친구 추가한 사용자: 친구톡 (즉시, 자유로운 형식)
- 친구 추가하지 않은 사용자: 알림톡 (친구 추가 불필요)

이렇게 하면 **즉시 사용 가능하면서도** 나중에 확장 가능합니다!

