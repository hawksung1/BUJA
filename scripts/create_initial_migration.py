#!/usr/bin/env python3
"""
초기 마이그레이션 생성 스크립트
"""
import subprocess
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """초기 마이그레이션 생성"""
    print("=" * 60)
    print("초기 Alembic 마이그레이션 생성")
    print("=" * 60)

    # Alembic 초기화 (이미 되어 있다면 스킵)
    print("\n1. Alembic 초기화 확인...")

    # 초기 마이그레이션 생성
    print("\n2. 초기 마이그레이션 생성...")
    try:
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "Initial migration"],
            cwd=project_root,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ 초기 마이그레이션 생성 완료")
            print(result.stdout)
        else:
            print("❌ 마이그레이션 생성 실패")
            print(result.stderr)
            return 1
    except FileNotFoundError:
        print("⚠️  Alembic이 설치되지 않았습니다.")
        print("다음 명령어로 설치하세요: uv sync --extra dev")
        return 1

    print("\n" + "=" * 60)
    print("✅ 완료!")
    print("=" * 60)
    print("\n다음 단계:")
    print("1. 생성된 마이그레이션 파일을 검토하세요")
    print("2. 데이터베이스를 생성하세요")
    print("3. 마이그레이션을 적용하세요: alembic upgrade head")

    return 0

if __name__ == "__main__":
    sys.exit(main())




