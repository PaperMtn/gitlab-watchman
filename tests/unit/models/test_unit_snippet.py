from gitlab_watchman.models import snippet, user
from gitlab_watchman.utils import convert_to_utc_datetime

from fixtures import (
    GitLabMockData,
    mock_snippet
)


def test_snippet_initialisation(mock_snippet):
    # Test that the Snippet object is of the correct type
    assert isinstance(mock_snippet, snippet.Snippet)

    # Test that the Snippet object has the correct attributes
    assert mock_snippet.id == GitLabMockData.MOCK_SNIPPET_DICT.get('id')
    assert mock_snippet.title == GitLabMockData.MOCK_SNIPPET_DICT.get('title')
    assert mock_snippet.description == GitLabMockData.MOCK_SNIPPET_DICT.get('description')
    assert mock_snippet.visibility == GitLabMockData.MOCK_SNIPPET_DICT.get('visibility')
    assert mock_snippet.created_at == convert_to_utc_datetime(GitLabMockData.MOCK_SNIPPET_DICT.get('created_at'))
    assert mock_snippet.updated_at == convert_to_utc_datetime(GitLabMockData.MOCK_SNIPPET_DICT.get('updated_at'))
    assert mock_snippet.file_name == GitLabMockData.MOCK_SNIPPET_DICT.get('file_name')
    assert mock_snippet.web_url == GitLabMockData.MOCK_SNIPPET_DICT.get('web_url')

    assert mock_snippet.files is None
    assert isinstance(mock_snippet.author, user.User)

    assert mock_snippet.author.id == GitLabMockData.MOCK_SNIPPET_DICT.get('author').get('id')
    assert mock_snippet.author.name == GitLabMockData.MOCK_SNIPPET_DICT.get('author').get('name')
    assert mock_snippet.author.username == GitLabMockData.MOCK_SNIPPET_DICT.get('author').get('username')
    assert mock_snippet.author.state == GitLabMockData.MOCK_SNIPPET_DICT.get('author').get('state')
    assert mock_snippet.author.web_url == GitLabMockData.MOCK_SNIPPET_DICT.get('author').get('web_url')


def test_snippet_missing_fields():
    # Create a dict with missing fields
    snippet_dict = {
        "id": "1",
        "title": "Test snippet",
    }
    snippet_object = snippet.create_from_dict(snippet_dict)
    # Test that the Snippet object is of the correct type
    assert isinstance(snippet_object, snippet.Snippet)

    # Test that the Snippet object has the correct attributes
    assert snippet_object.id == snippet_dict.get('id')
    assert snippet_object.title == snippet_dict.get('title')
    assert snippet_object.description is None
    assert snippet_object.visibility is None
    assert snippet_object.created_at is None
    assert snippet_object.updated_at is None
    assert snippet_object.file_name is None
    assert snippet_object.web_url is None

    assert snippet_object.author is None
    assert snippet_object.files is None


def test_snippet_file_initialisation():
    # Test creating with one file
    snippet_dict_one = GitLabMockData.MOCK_SNIPPET_DICT.copy()
    snippet_dict_one['files'] = [
        {
            'path': 'README.md',
            'raw_url': 'https://gitlab.com/test/test/-/blob/master/README.md'
        }
    ]
    snippet_object_one = snippet.create_from_dict(snippet_dict_one)
    assert isinstance(snippet_object_one.files, list)
    assert len(snippet_object_one.files) == 1
    assert isinstance(snippet_object_one.files[0], snippet.File)
    assert snippet_object_one.files[0].path == 'README.md'
    assert snippet_object_one.files[0].raw_url == 'https://gitlab.com/test/test/-/blob/master/README.md'

    # Test creating with multiple files
    snippet_dict_two = GitLabMockData.MOCK_SNIPPET_DICT.copy()
    snippet_dict_two['files'] = [
        {
            'path': 'README.md',
            'raw_url': 'https://gitlab.com/test/test/-/blob/master/README.md'
        },
        {
            'path': 'LICENSE',
            'raw_url': 'https://gitlab.com/test/test/-/blob/master/LICENSE'
        }
    ]
    snippet_object_two = snippet.create_from_dict(snippet_dict_two)
    assert isinstance(snippet_object_two.files, list)
    assert len(snippet_object_two.files) == 2
    assert isinstance(snippet_object_two.files[0], snippet.File)
    assert isinstance(snippet_object_two.files[1], snippet.File)
    assert snippet_object_two.files[0].path == 'README.md'
    assert snippet_object_two.files[0].raw_url == 'https://gitlab.com/test/test/-/blob/master/README.md'
    assert snippet_object_two.files[1].path == 'LICENSE'
    assert snippet_object_two.files[1].raw_url == 'https://gitlab.com/test/test/-/blob/master/LICENSE'
