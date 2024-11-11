from gitlab_watchman.models import project
from gitlab_watchman.utils import convert_to_utc_datetime

from fixtures import (
    GitLabMockData,
    mock_project
)


def test_project_initialisation(mock_project):
    # Test that the Project object is of the correct type
    assert isinstance(mock_project, project.Project)

    # Test that the Project object has the correct attributes
    assert mock_project.id == GitLabMockData.MOCK_PROJECT_DICT.get('id')
    assert mock_project.description == GitLabMockData.MOCK_PROJECT_DICT.get('description')
    assert mock_project.name == GitLabMockData.MOCK_PROJECT_DICT.get('name')
    assert mock_project.name_with_namespace == GitLabMockData.MOCK_PROJECT_DICT.get('name_with_namespace')
    assert mock_project.path == GitLabMockData.MOCK_PROJECT_DICT.get('path')
    assert mock_project.path_with_namespace == GitLabMockData.MOCK_PROJECT_DICT.get('path_with_namespace')
    assert mock_project.created_at == convert_to_utc_datetime(GitLabMockData.MOCK_PROJECT_DICT.get('created_at'))
    assert mock_project.web_url == GitLabMockData.MOCK_PROJECT_DICT.get('web_url')
    assert mock_project.last_activity_at == convert_to_utc_datetime(GitLabMockData.MOCK_PROJECT_DICT.get('last_activity_at'))

    # Test that the Namespace object is of the correct type
    assert isinstance(mock_project.namespace, project.Namespace)

    # Test that the Namespace object has the correct attributes
    assert mock_project.namespace.id == GitLabMockData.MOCK_PROJECT_DICT.get('namespace').get('id')
    assert mock_project.namespace.name == GitLabMockData.MOCK_PROJECT_DICT.get('namespace').get('name')
    assert mock_project.namespace.path == GitLabMockData.MOCK_PROJECT_DICT.get('namespace').get('path')
    assert mock_project.namespace.web_url == GitLabMockData.MOCK_PROJECT_DICT.get('namespace').get('web_url')
    assert mock_project.namespace.kind == GitLabMockData.MOCK_PROJECT_DICT.get('namespace').get('kind')
    assert mock_project.namespace.full_path == GitLabMockData.MOCK_PROJECT_DICT.get('namespace').get('full_path')
    assert mock_project.namespace.parent_id == GitLabMockData.MOCK_PROJECT_DICT.get('namespace').get('parent_id')


def test_project_missing_fields():
    # Create a dict with missing fields
    project_dict = {
        "id": "1",
        "description": "Test project",
    }
    project_object = project.create_from_dict(project_dict)
    # Test that the Project object is of the correct type
    assert isinstance(project_object, project.Project)

    # Test that the Project object has the correct attributes
    assert project_object.id == project_dict.get('id')
    assert project_object.description == project_dict.get('description')
    assert project_object.name is None
    assert project_object.name_with_namespace is None
    assert project_object.path is None
    assert project_object.path_with_namespace is None
    assert project_object.created_at is None
    assert project_object.web_url is None
    assert project_object.last_activity_at is None

    # Test that the Namespace object is of the correct type
    assert isinstance(project_object.namespace, project.Namespace)

    # Test that the Namespace object has the correct attributes
    assert project_object.namespace.id is None
    assert project_object.namespace.name is None
    assert project_object.namespace.path is None
    assert project_object.namespace.web_url is None
    assert project_object.namespace.kind is None
    assert project_object.namespace.full_path is None
    assert project_object.namespace.parent_id is None
