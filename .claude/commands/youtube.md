# /youtube — 머니머니코믹스 인사이트

머니머니코믹스 유튜브 채널(@moneymoneycomics)의 최신 콘텐츠를 분석하여 투자 인사이트를 추출합니다.

## 채널 정보
- 채널: 머니머니코믹스
- YouTube Handle: @moneymoneycomics
- 채널 URL: https://www.youtube.com/@moneymoneycomics

## 데이터 수집 프로세스

1. YouTube RSS 피드로 최신 영상 목록 조회 (API 키 불필요)
   - `https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID`
   - feedparser로 파싱
2. 영상 제목, 설명 분석
3. 핵심 투자 키워드 추출
4. BUJA 투자 철학과 연계

## 출력 형식
```
## 머니머니코믹스 최신 인사이트
📅 YYYY-MM-DD | BUJA 어드바이저

### 최신 영상
1. **[영상 제목]** (YYYY-MM-DD 업로드)
   - 주요 내용: ...
   - 핵심 종목/테마: ...
   - 조회수: X만회 | 좋아요: X천개
   - 투자 인사이트:
     - ...
   - 관련 투자 철학: [버핏/그레이엄/린치/달리오]

2. ...

### 반복 등장 테마 (최근 1개월)
- #테마1: X회 언급
- #테마2: X회 언급

### 어드바이저 평가
채널의 최근 관심사와 BUJA 관점의 검토:
...

⚠️ 유튜브 콘텐츠는 교육/참고용이며 투자 조언이 아닙니다.
```

## 구현 참고
```python
# src/data/youtube_fetcher.py
import feedparser

CHANNEL_ID = "UCxxxxxxxxxxxxxxxxxxxxxx"  # 머니머니코믹스 채널 ID
RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"

feed = feedparser.parse(RSS_URL)
videos = feed.entries  # 최신 영상 목록 (API 키 불필요)
```
