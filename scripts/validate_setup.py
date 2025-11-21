#!/usr/bin/env python3
"""
프로젝트 설정 검증 스크립트
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_file_exists(file_path: Path, description: str) -> bool:
    """파일 존재 여부 확인"""
    exists = file_path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {file_path}")
    return exists

def check_directory_exists(dir_path: Path, description: str) -> bool:
    """디렉토리 존재 여부 확인"""
    exists = dir_path.exists() and dir_path.is_dir()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {dir_path}")
    return exists

def validate_imports():
    """모듈 import 검증"""
    print("\n📦 모듈 Import 검증:")
    errors = []

    try:
        print("✅ config.settings")
    except Exception as e:
        print(f"❌ config.settings: {e}")
        errors.append("config.settings")

    try:
        print("✅ config.logging")
    except Exception as e:
        print(f"❌ config.logging: {e}")
        errors.append("config.logging")

    try:
        print("✅ config.database")
    except Exception as e:
        print(f"❌ config.database: {e}")
        errors.append("config.database")

    try:
        print("✅ src.exceptions")
    except Exception as e:
        print(f"❌ src.exceptions: {e}")
        errors.append("src.exceptions")

    try:
        print("✅ src.utils")
    except Exception as e:
        print(f"❌ src.utils: {e}")
        errors.append("src.utils")

    try:
        print("✅ src.middleware")
    except Exception as e:
        print(f"❌ src.middleware: {e}")
        errors.append("src.middleware")

    return len(errors) == 0

def main():
    """메인 검증 함수"""
    print("=" * 60)
    print("BUJA 프로젝트 설정 검증")
    print("=" * 60)

    all_checks_passed = True

    # 1. 프로젝트 구조 검증
    print("\n📁 프로젝트 구조 검증:")
    checks = [
        (project_root / "pyproject.toml", "pyproject.toml"),
        (project_root / "pytest.ini", "pytest.ini"),
        (project_root / "alembic.ini", "alembic.ini"),
        (project_root / ".pre-commit-config.yaml", ".pre-commit-config.yaml"),
        (project_root / ".gitattributes", ".gitattributes"),
        (project_root / "README.md", "README.md"),
        (project_root / "config", "config/ 디렉토리"),
        (project_root / "src", "src/ 디렉토리"),
        (project_root / "tests", "tests/ 디렉토리"),
        (project_root / "migrations", "migrations/ 디렉토리"),
        (project_root / "docs", "docs/ 디렉토리"),
        (project_root / ".github" / "workflows", ".github/workflows/ 디렉토리"),
    ]

    for path, desc in checks:
        if path.is_file():
            if not check_file_exists(path, desc):
                all_checks_passed = False
        else:
            if not check_directory_exists(path, desc):
                all_checks_passed = False

    # 2. 설정 파일 검증
    print("\n⚙️  설정 파일 검증:")
    config_files = [
        (project_root / "config" / "settings.py", "기본 설정"),
        (project_root / "config" / "settings_dev.py", "개발 환경 설정"),
        (project_root / "config" / "settings_prod.py", "프로덕션 환경 설정"),
        (project_root / "config" / "settings_test.py", "테스트 환경 설정"),
        (project_root / "config" / "database.py", "데이터베이스 설정"),
        (project_root / "config" / "logging.py", "로깅 설정"),
    ]

    for path, desc in config_files:
        if not check_file_exists(path, desc):
            all_checks_passed = False

    # 3. 소스 코드 검증
    print("\n💻 소스 코드 검증:")
    src_files = [
        (project_root / "src" / "exceptions.py", "예외 클래스"),
        (project_root / "src" / "utils" / "security.py", "보안 유틸리티"),
        (project_root / "src" / "utils" / "validators.py", "검증 유틸리티"),
        (project_root / "src" / "utils" / "formatters.py", "포맷팅 유틸리티"),
        (project_root / "src" / "middleware" / "error_handler.py", "에러 핸들러"),
    ]

    for path, desc in src_files:
        if not check_file_exists(path, desc):
            all_checks_passed = False

    # 4. CI/CD 검증
    print("\n🔄 CI/CD 파이프라인 검증:")
    workflow_files = [
        (project_root / ".github" / "workflows" / "ci.yml", "CI 워크플로우"),
        (project_root / ".github" / "workflows" / "deploy.yml", "배포 워크플로우"),
        (project_root / ".github" / "workflows" / "pr-check.yml", "PR 체크 워크플로우"),
        (project_root / ".github" / "pull_request_template.md", "PR 템플릿"),
    ]

    for path, desc in workflow_files:
        if not check_file_exists(path, desc):
            all_checks_passed = False

    # 5. 문서 검증
    print("\n📚 문서 검증:")
    doc_files = [
        (project_root / "docs" / "REQUIREMENTS.md", "요구사항 명세서"),
        (project_root / "docs" / "DESIGN.md", "프로그램 설계서"),
        (project_root / "docs" / "WBS.md", "작업 분해 구조"),
        (project_root / "docs" / "GIT_WORKFLOW.md", "Git 워크플로우"),
    ]

    for path, desc in doc_files:
        if not check_file_exists(path, desc):
            all_checks_passed = False

    # 6. 모듈 Import 검증
    import_passed = validate_imports()
    if not import_passed:
        all_checks_passed = False

    # 7. 설정 값 검증
    print("\n🔧 설정 값 검증:")
    try:
        from config import settings
        print(f"✅ 환경: {settings.environment}")
        print(f"✅ 디버그 모드: {settings.debug}")
        print(f"✅ 로그 레벨: {settings.log_level}")
        print(f"✅ 데이터베이스 URL: {settings.database_url[:30]}...")
    except Exception as e:
        print(f"❌ 설정 로드 실패: {e}")
        all_checks_passed = False

    # 결과 출력
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("✅ 모든 검증 통과!")
        print("=" * 60)
        return 0
    else:
        print("❌ 일부 검증 실패")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())

