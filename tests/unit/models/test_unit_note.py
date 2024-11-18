from gitlab_watchman.models import note, user
from gitlab_watchman.utils import convert_to_utc_datetime

from fixtures import (
    GitLabMockData,
    mock_note
)


def test_note_initialisation(mock_note):
    # Test that the Note object is of the correct type
    assert isinstance(mock_note, note.Note)

    # Test that the Note object has the correct attributes
    assert mock_note.id == GitLabMockData.MOCK_NOTE_DICT.get('id')
    assert mock_note.type == GitLabMockData.MOCK_NOTE_DICT.get('type')
    assert mock_note.body == GitLabMockData.MOCK_NOTE_DICT.get('body')
    assert mock_note.attachment == GitLabMockData.MOCK_NOTE_DICT.get('attachment')
    assert isinstance(mock_note.author, user.User)
    assert mock_note.author.id == GitLabMockData.MOCK_NOTE_DICT.get('author').get('id')
    assert mock_note.author.name == GitLabMockData.MOCK_NOTE_DICT.get('author').get('name')
    assert mock_note.author.username == GitLabMockData.MOCK_NOTE_DICT.get('author').get('username')
    assert mock_note.author.state == GitLabMockData.MOCK_NOTE_DICT.get('author').get('state')
    assert mock_note.author.web_url == GitLabMockData.MOCK_NOTE_DICT.get('author').get('web_url')
    assert mock_note.created_at == convert_to_utc_datetime(GitLabMockData.MOCK_NOTE_DICT.get('created_at'))
    assert mock_note.updated_at == convert_to_utc_datetime(GitLabMockData.MOCK_NOTE_DICT.get('updated_at'))
    assert mock_note.system == GitLabMockData.MOCK_NOTE_DICT.get('system')
    assert mock_note.noteable_id == GitLabMockData.MOCK_NOTE_DICT.get('noteable_id')
    assert mock_note.noteable_type == GitLabMockData.MOCK_NOTE_DICT.get('noteable_type')
    assert mock_note.commit_id == GitLabMockData.MOCK_NOTE_DICT.get('commit_id')
    assert mock_note.resolvable == GitLabMockData.MOCK_NOTE_DICT.get('resolvable')
    assert mock_note.resolved_by is None
    assert mock_note.resolved_at == convert_to_utc_datetime(GitLabMockData.MOCK_NOTE_DICT.get('resolved_at'))
    assert mock_note.confidential == GitLabMockData.MOCK_NOTE_DICT.get('confidential')
    assert mock_note.noteable_iid == GitLabMockData.MOCK_NOTE_DICT.get('noteable_iid')
    assert mock_note.command_changes == GitLabMockData.MOCK_NOTE_DICT.get('command_changes')


def test_note_missing_fields():
    # Crete dict with missing fields
    note_dict = {
        "id": 1,
        "type": "note",
    }
    note_object = note.create_from_dict(note_dict)
    # Test that the Note object is of the correct type
    assert isinstance(note_object, note.Note)

    # Test that the Note object has the correct attributes
    assert note_object.id == note_dict.get('id')
    assert note_object.type == note_dict.get('type')
    assert note_object.body is None
    assert note_object.attachment is None
    assert note_object.author is None
    assert note_object.created_at is None
    assert note_object.updated_at is None
    assert note_object.system is None
    assert note_object.noteable_id is None
    assert note_object.noteable_type is None
    assert note_object.commit_id is None
    assert note_object.resolvable is None
    assert note_object.resolved_by is None
    assert note_object.resolved_at is None
    assert note_object.confidential is None
    assert note_object.noteable_iid is None
    assert note_object.command_changes is None


def test_note_with_resolved_by():
    # Test that the Note object is of the correct type
    note_dict = GitLabMockData.MOCK_NOTE_DICT.copy()
    note_dict['resolved_by'] = {
            "id": 1,
            "name": "Administrator",
            "username": "root",
            "state": "active",
            "avatar_url": "https://www.gravatar.com/avatar/e64c7d89f26bd1972efa854d13d7dd61?s=80&d=identicon",
            "web_url": "http://localhost:3000/root"
        }
    note_object = note.create_from_dict(note_dict)

    # Test that the Note object has the correct attributes
    assert isinstance(note_object, note.Note)
    assert isinstance(note_object.resolved_by, user.User)
    assert note_object.resolved_by.id == note_dict.get('resolved_by').get('id')
    assert note_object.resolved_by.name == note_dict.get('resolved_by').get('name')
    assert note_object.resolved_by.username == note_dict.get('resolved_by').get('username')
    assert note_object.resolved_by.state == note_dict.get('resolved_by').get('state')
    assert note_object.resolved_by.web_url == note_dict.get('resolved_by').get('web_url')