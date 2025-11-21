# 자율적 Agent 기능

## 개요

BUJA의 자율적 Agent는 사용자의 포트폴리오를 자동으로 모니터링하고, 필요시 능동적으로 조치를 취하는 시스템입니다.

## 주요 기능

### 1. 포트폴리오 모니터링
- 매일 자동으로 포트폴리오 분석
- 리스크 임계값 체크
- 목표 진행률 추적
- 리밸런싱 필요성 판단

### 2. 자동 알림
- 이메일 알림 (구현 완료)
- 채팅 메시지로 저장
- 카카오톡/SMS (추후 확장 가능)

### 3. 목표 추적
- 목표 진행률 실시간 계산
- 목표 달성 예측
- 위험도 평가

## 사용 방법

### 백그라운드 워커 실행

```bash
python scripts/start_background_worker.py
```

### 설정

`.env.local`에 이메일 설정 추가:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=BUJA 투자 상담
```

## 관련 문서

- [구현 계획](./AUTONOMOUS_AGENT_IMPLEMENTATION_PLAN.md)
- [구현 완료 요약](./AUTONOMOUS_AGENT_IMPLEMENTATION_SUMMARY.md)
- [알림 시스템 설계](./NOTIFICATION_DESIGN.md)
- [카카오톡 알림 상세](./KAKAO_NOTIFICATION_DETAIL.md)

