# 코드 최적화 및 파일 정리 가이드

## 자동 검사 항목

**기능 구현/수정 후 항상 다음 항목을 검사하고 최적화하세요:**

### 1. 코드 최적화 검사
- [ ] 중복 코드 제거
- [ ] 공통 유틸리티 함수 활용 (`src/utils/converters.py` 등)
- [ ] 데이터베이스 쿼리 최적화 (세션 재사용, 배치 쿼리)
- [ ] 불필요한 데이터 변환 제거
- [ ] 타입 힌팅 개선

### 2. 불필요한 파일 삭제
- [ ] 중복 테스트 파일 확인 및 삭제
- [ ] 임시 파일 삭제
- [ ] 사용되지 않는 스크립트 삭제
- [ ] 빈 구현 파일 삭제

### 3. 코드 품질 검사
- [ ] Linter 오류 수정 (`uv run lint`)
- [ ] 타입 체크 통과 (`uv run type-check`)
- [ ] 테스트 실행 및 통과 확인

## 검사 방법

### 중복 코드 검색
```bash
# 유사한 패턴 검색
grep -r "records_dict = \[" src/
grep -r "async with.*session" src/
```

### 사용되지 않는 파일 확인
```bash
# 테스트 파일 확인
find tests/ -name "*.py" -type f
# 임시 파일 검색
find . -name "*.tmp" -o -name "*_backup.*" -o -name "*.py~"
```

### Linter 실행
```bash
uv run lint
uv run type-check
```

## 최적화 우선순위

1. **성능 최적화**: 데이터베이스 쿼리, 세션 관리
2. **코드 중복 제거**: 공통 함수 추출
3. **파일 정리**: 불필요한 파일 삭제
4. **타입 안정성**: 타입인팅 개선

## 공통 유틸리티 함수

### `src/utils/converters.py`
- `investment_records_to_dict()`: InvestmentRecord 리스트를 딕셔너리로 변환
- `safe_decimal_to_float()`: Decimal을 안전하게 float로 변환

### 사용 예시
```python
from src.utils.converters import investment_records_to_dict

# 기존 코드 (중복)
records_dict = [
    {
        "asset_type": record.asset_type,
        "quantity": float(record.quantity),
        # ...
    }
    for record in records
]

# 최적화된 코드
records_dict = investment_records_to_dict(records, include_dates=True)
```

## 데이터베이스 세션 최적화

### 기존 패턴 (비효율적)
```python
records1 = await repo.get_by_user_id(user_id)
records2 = await repo.get_realized(user_id)
records3 = await repo.get_unrealized(user_id)
```

### 최적화된 패턴
```python
async with db.session() as session:
    records1 = await repo.get_by_user_id(user_id, session=session)
    records2 = await repo.get_realized(user_id, session=session)
    records3 = await repo.get_unrealized(user_id, session=session)
```

## 삭제된 파일 목록

다음 파일들은 중복되거나 사용되지 않아 삭제되었습니다:
- `tests/e2e/test_streamlit_app.py` - 빈 구현
- `tests/e2e/test_playwright_direct.py` - 중복
- `tests/e2e/test_manual_playwright_check.py` - 임시 스크립트
- `tests/e2e/test_browser_visible.py` - 임시 확인 스크립트
- `tests/e2e/test_ui_local.py` - 중복
- `tests/e2e/test_playwright_mcp.py` - 빈 구현
- `tests/e2e/test_streamlit_playwright.py` - 빈 구현
- `test_streamlit_e2e.py` - 루트에 중복
- `test_streamlit_ui.py` - 루트에 중복

## 체크리스트

기능 구현/수정 후 다음을 확인하세요:

1. ✅ 코드 최적화 검사 완료
2. ✅ 불필요한 파일 삭제 완료
3. ✅ Linter 오류 없음
4. ✅ 타입 체크 통과
5. ✅ 테스트 통과

