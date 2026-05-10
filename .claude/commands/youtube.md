# /youtube — 머니머니코믹스 인사이트

머니머니코믹스(@moneymoneycomics) 최신 콘텐츠를 분석하여 투자 인사이트를 추출합니다.

## 프로세스

1. YouTube RSS 피드에서 최신 영상 목록 파싱 (`src/data/youtube_fetcher.py`)
   - `https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID`
2. 영상 제목·설명에서 핵심 투자 키워드 추출
3. 5대 투자자 철학과 연계하여 인사이트 정리
4. 최근 1개월 반복 테마 집계

출력: 최신 영상 요약·핵심 인사이트·반복 테마·어드바이저 평가
