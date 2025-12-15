"""
ChatProjectService 단위 테스트
"""
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from config.database import Database
from src.models.chat_project import ChatProject
from src.services.chat_project_service import ChatProjectService


@pytest.fixture
def mock_db():
    """Mock Database 인스턴스"""
    return MagicMock(spec=Database)


@pytest.fixture
def chat_project_service(mock_db):
    """ChatProjectService 인스턴스"""
    return ChatProjectService(database=mock_db)


class TestChatProjectServiceGetProjects:
    """ChatProjectService.get_projects 테스트"""

    @pytest.mark.asyncio
    async def test_get_projects_success(self, chat_project_service):
        """프로젝트 목록 조회 성공 테스트"""
        now = datetime.now()
        projects = [
            ChatProject(id=1, user_id=1, name="Project 1", description="First project", created_at=now, updated_at=now),
            ChatProject(id=2, user_id=1, name="Project 2", description="Second project", created_at=now, updated_at=now)
        ]

        mock_project_repo = MagicMock()
        mock_project_repo.get_by_user_id = AsyncMock(return_value=projects)
        chat_project_service.project_repo = mock_project_repo

        result = await chat_project_service.get_projects(1)

        assert len(result) == 2
        assert result[0]["name"] == "Project 1"
        assert result[1]["name"] == "Project 2"
        mock_project_repo.get_by_user_id.assert_called_once_with(1, None)

    @pytest.mark.asyncio
    async def test_get_projects_empty(self, chat_project_service):
        """프로젝트가 없는 경우 테스트"""
        mock_project_repo = MagicMock()
        mock_project_repo.get_by_user_id = AsyncMock(return_value=[])
        chat_project_service.project_repo = mock_project_repo

        result = await chat_project_service.get_projects(1)

        assert len(result) == 0


class TestChatProjectServiceGetProject:
    """ChatProjectService.get_project 테스트"""

    @pytest.mark.asyncio
    async def test_get_project_success(self, chat_project_service):
        """프로젝트 조회 성공 테스트"""
        now = datetime.now()
        project = ChatProject(
            id=1, user_id=1, name="Test Project",
            description="Test description", icon="📊",
            created_at=now, updated_at=now
        )

        mock_project_repo = MagicMock()
        mock_project_repo.get_by_id = AsyncMock(return_value=project)
        chat_project_service.project_repo = mock_project_repo

        result = await chat_project_service.get_project(1, 1)

        assert result is not None
        assert result["name"] == "Test Project"
        assert result["description"] == "Test description"
        assert result["icon"] == "📊"
        mock_project_repo.get_by_id.assert_called_once_with(1, 1, None)

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, chat_project_service):
        """존재하지 않는 프로젝트 조회 테스트"""
        mock_project_repo = MagicMock()
        mock_project_repo.get_by_id = AsyncMock(return_value=None)
        chat_project_service.project_repo = mock_project_repo

        result = await chat_project_service.get_project(999, 1)

        assert result is None


class TestChatProjectServiceCreateProject:
    """ChatProjectService.create_project 테스트"""

    @pytest.mark.asyncio
    async def test_create_project_success(self, chat_project_service):
        """프로젝트 생성 성공 테스트"""
        now = datetime.now()
        project = ChatProject(
            id=1, user_id=1, name="New Project",
            description="New project description",
            created_at=now, updated_at=now
        )

        mock_project_repo = MagicMock()
        mock_project_repo.create_project = AsyncMock(return_value=project)
        chat_project_service.project_repo = mock_project_repo

        result = await chat_project_service.create_project(
            user_id=1,
            name="New Project",
            description="New project description"
        )

        assert result["name"] == "New Project"
        assert result["description"] == "New project description"
        mock_project_repo.create_project.assert_called_once_with(
            user_id=1,
            name="New Project",
            description="New project description",
            icon=None,
            session=None
        )

    @pytest.mark.asyncio
    async def test_create_project_with_icon(self, chat_project_service):
        """아이콘이 포함된 프로젝트 생성 테스트"""
        now = datetime.now()
        project = ChatProject(
            id=1, user_id=1, name="Project with Icon",
            icon="📈",
            created_at=now, updated_at=now
        )

        mock_project_repo = MagicMock()
        mock_project_repo.create_project = AsyncMock(return_value=project)
        chat_project_service.project_repo = mock_project_repo

        result = await chat_project_service.create_project(
            user_id=1,
            name="Project with Icon",
            icon="📈"
        )

        assert result["icon"] == "📈"
        call_args = mock_project_repo.create_project.call_args
        assert call_args[1]["icon"] == "📈"


class TestChatProjectServiceUpdateProject:
    """ChatProjectService.update_project 테스트"""

    @pytest.mark.asyncio
    async def test_update_project_success(self, chat_project_service):
        """프로젝트 업데이트 성공 테스트"""
        now = datetime.now()
        project = ChatProject(
            id=1, user_id=1, name="Updated Project",
            description="Updated description",
            created_at=now, updated_at=now
        )

        mock_project_repo = MagicMock()
        mock_project_repo.update_project = AsyncMock(return_value=project)
        chat_project_service.project_repo = mock_project_repo

        result = await chat_project_service.update_project(
            project_id=1,
            user_id=1,
            name="Updated Project",
            description="Updated description"
        )

        assert result is not None
        assert result["name"] == "Updated Project"
        assert result["description"] == "Updated description"
        mock_project_repo.update_project.assert_called_once_with(
            project_id=1,
            user_id=1,
            name="Updated Project",
            description="Updated description",
            icon=None,
            session=None
        )

    @pytest.mark.asyncio
    async def test_update_project_partial(self, chat_project_service):
        """부분 업데이트 테스트"""
        now = datetime.now()
        project = ChatProject(
            id=1, user_id=1, name="Original Name",
            description="Updated description",
            created_at=now, updated_at=now
        )

        mock_project_repo = MagicMock()
        mock_project_repo.update_project = AsyncMock(return_value=project)
        chat_project_service.project_repo = mock_project_repo

        result = await chat_project_service.update_project(
            project_id=1,
            user_id=1,
            description="Updated description"
        )

        assert result is not None
        call_args = mock_project_repo.update_project.call_args
        assert call_args[1]["name"] is None
        assert call_args[1]["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_update_project_not_found(self, chat_project_service):
        """존재하지 않는 프로젝트 업데이트 테스트"""
        mock_project_repo = MagicMock()
        mock_project_repo.update_project = AsyncMock(return_value=None)
        chat_project_service.project_repo = mock_project_repo

        result = await chat_project_service.update_project(
            project_id=999,
            user_id=1,
            name="Updated Name"
        )

        assert result is None


class TestChatProjectServiceDeleteProject:
    """ChatProjectService.delete_project 테스트"""

    @pytest.mark.asyncio
    async def test_delete_project_success(self, chat_project_service):
        """프로젝트 삭제 성공 테스트"""
        mock_project_repo = MagicMock()
        mock_project_repo.delete_project = AsyncMock(return_value=True)
        chat_project_service.project_repo = mock_project_repo

        result = await chat_project_service.delete_project(1, 1)

        assert result is True
        mock_project_repo.delete_project.assert_called_once_with(1, 1, None)

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, chat_project_service):
        """존재하지 않는 프로젝트 삭제 테스트"""
        mock_project_repo = MagicMock()
        mock_project_repo.delete_project = AsyncMock(return_value=False)
        chat_project_service.project_repo = mock_project_repo

        result = await chat_project_service.delete_project(999, 1)

        assert result is False

