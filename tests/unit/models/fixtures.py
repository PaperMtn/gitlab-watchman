import pytest

from gitlab_watchman.models import (
    commit,
    blob,
    file,
    group,
    issue,
    merge_request,
    milestone,
    note,
    project,
    snippet,
    user,
    wiki_blob,
    signature
)


class GitLabMockData:
    """ Holds mock data for GitLab API responses."""

    MOCK_COMMIT_DICT = {
        "id": "ed899a2f4b50b4370feeea94676502b42383c746",
        "short_id": "ed899a2f4b5",
        "title": "Replace sanitize with escape once",
        "author_name": "Example User",
        "author_email": "user@example.com",
        "authored_date": "2021-09-20T11:50:22.001+00:00",
        "committer_name": "Administrator",
        "committer_email": "admin@example.com",
        "committed_date": "2021-09-20T11:50:22.001+00:00",
        "created_at": "2021-09-20T11:50:22.001+00:00",
        "message": "Replace sanitize with escape once",
        "parent_ids": ["6104942438c14ec7bd21c6cd5bd995272b3faff6"],
        "web_url": "https://gitlab.example.com/janedoe/gitlab-foss/-/commit/"
                   "ed899a2f4b50b4370feeea94676502b42383c746",
        "trailers": {},
        "extended_trailers": {}
    }

    MOCK_BLOB_DICT = {
        "basename": "README",
        "data": "```\n\n## Installation\n\nQuick start using the [pre-built",
        "path": "README.md",
        "filename": "README.md",
        "id": None,
        "ref": "main",
        "startline": 46,
        "project_id": 6
    }

    MOCK_FILE_DICT = {
        "file_name": "key.rb",
        "file_path": "app/models/key.rb",
        "size": 1476,
        "encoding": "base64",
        "content": "IyA9PSBTY2hlbWEgSW5mb3...",
        "content_sha256": "4c294617b60715c1d218e61164a3abd4808a4284cbc30e6728a01ad9aada4481",
        "ref": "main",
        "blob_id": "79f7bbd25901e8334750839545a9bd021f0e4c83",
        "commit_id": "d5a3ff139356ce33e37e73add446f16869741b50",
        "last_commit_id": "570e7b2abdd848b95f2f578043fc23bd6f6fd24d",
        "execute_filemode": False
    }

    MOCK_GROUP_DICT = {
        "id": 4,
        "name": "Twitter",
        "path": "twitter",
        "description": "Aliquid qui quis dignissimos distinctio ut commodi voluptas est.",
        "visibility": "public",
        "avatar_url": None,
        "web_url": "https://gitlab.example.com/groups/twitter",
        "request_access_enabled": False,
        "repository_storage": "default",
        "full_name": "Twitter",
        "full_path": "twitter",
        "runners_token": "ba324ca7b1c77fc20bb9",
        "file_template_project_id": 1,
        "parent_id": None,
        "enabled_git_access_protocol": "all",
        "created_at": "2020-01-15T12:36:29.590Z",
        "shared_with_groups": [
            {
                "group_id": 28,
                "group_name": "H5bp",
                "group_full_path": "h5bp",
                "group_access_level": 20,
                "expires_at": None
            }
        ],
        "prevent_sharing_groups_outside_hierarchy": False,
        "ip_restriction_ranges": None,
        "math_rendering_limits_enabled": None,
        "lock_math_rendering_limits_enabled": None
    }

    MOCK_ISSUE_DICT = {
        "id": 83,
        "iid": 1,
        "project_id": 12,
        "title": "Add file",
        "description": "Add first file",
        "state": "opened",
        "created_at": "2018-01-24T06:02:15.514Z",
        "updated_at": "2018-02-06T12:36:23.263Z",
        "closed_at": '2018-02-06T12:36:23.263Z',
        "closed_by": {
            "id": 1,
            "name": "Administrator",
            "username": "root",
            "state": "active",
            "avatar_url": "https://www.gravatar.com/avatar/e64c7d89f26bd1972efa854d13d7dd61?s=80&d=identicon",
            "web_url": "http://localhost:3000/root"
        },
        "description_html": None,
        "description_text": "Add first file",
        "labels": [],
        "milestone": None,
        "assignees": [{
            "id": 20,
            "name": "Ceola Deckow",
            "username": "sammy.collier",
            "state": "active",
            "avatar_url": "https://www.gravatar.com/avatar/c23d85a4f50e0ea76ab739156c639231?s=80&d=identicon",
            "web_url": "http://localhost:3000/sammy.collier"
        }],
        "author": {
            "id": 1,
            "name": "Administrator",
            "username": "root",
            "state": "active",
            "avatar_url": "https://www.gravatar.com/avatar/e64c7d89f26bd1972efa854d13d7dd61?s=80&d=identicon",
            "web_url": "http://localhost:3000/root"
        },
        "assignee": {
            "id": 20,
            "name": "Ceola Deckow",
            "username": "sammy.collier",
            "state": "active",
            "avatar_url": "https://www.gravatar.com/avatar/c23d85a4f50e0ea76ab739156c639231?s=80&d=identicon",
            "web_url": "http://localhost:3000/sammy.collier"
        },
        "user_notes_count": 0,
        "upvotes": 0,
        "downvotes": 0,
        "due_date": None,
        "confidential": False,
        "discussion_locked": None,
        "web_url": "http://localhost:3000/h5bp/7bp/subgroup-prj/issues/1",
        "time_stats": {
            "time_estimate": 0,
            "total_time_spent": 0,
            "human_time_estimate": None,
            "human_total_time_spent": None
        }
    }

    MOCK_MERGE_REQUEST_DICT = {
        "id": 56,
        "iid": 8,
        "project_id": 6,
        "title": "Add first file",
        "description": "This is a test MR to add file",
        "state": "opened",
        "created_at": "2018-01-22T14:21:50.830Z",
        "updated_at": "2018-02-06T12:40:33.295Z",
        "target_branch": "main",
        "source_branch": "jaja-test",
        "upvotes": 0,
        "downvotes": 0,
        "author": {
            "id": 1,
            "name": "Administrator",
            "username": "root",
            "state": "active",
            "avatar_url": "https://www.gravatar.com/avatar/e64c7d89f26bd1972efa854d13d7dd61?s=80&d=identicon",
            "web_url": "http://localhost:3000/root"
        },
        "assignee": {
            "id": 5,
            "name": "Jacquelyn Kutch",
            "username": "abigail",
            "state": "active",
            "avatar_url": "https://www.gravatar.com/avatar/3138c66095ee4bd11a508c2f7f7772da?s=80&d=identicon",
            "web_url": "http://localhost:3000/abigail"
        },
        "source_project_id": 6,
        "target_project_id": 6,
        "labels": [
            "ruby",
            "tests"
        ],
        "draft": False,
        "work_in_progress": False,
        "milestone": {
            "id": 13,
            "iid": 3,
            "project_id": 6,
            "title": "v2.0",
            "description": "Qui aut qui eos dolor beatae itaque tempore molestiae.",
            "state": "active",
            "created_at": "2017-09-05T07:58:29.099Z",
            "updated_at": "2017-09-05T07:58:29.099Z",
            "due_date": None,
            "start_date": None
        },
        "merge_when_pipeline_succeeds": False,
        "merge_status": "can_be_merged",
        "sha": "78765a2d5e0a43585945c58e61ba2f822e4d090b",
        "merge_commit_sha": None,
        "squash_commit_sha": None,
        "user_notes_count": 0,
        "discussion_locked": None,
        "should_remove_source_branch": None,
        "force_remove_source_branch": True,
        "web_url": "http://localhost:3000/twitter/flight/merge_requests/8",
        "time_stats": {
            "time_estimate": 0,
            "total_time_spent": 0,
            "human_time_estimate": None,
            "human_total_time_spent": None
        }
    }

    MOCK_MILESTONE_DICT = {
        "id": 44,
        "iid": 1,
        "project_id": 12,
        "title": "next release",
        "description": "Next release milestone",
        "state": "active",
        "created_at": "2018-02-06T12:43:39.271Z",
        "updated_at": "2018-02-06T12:44:01.298Z",
        "due_date": "2018-04-18",
        "start_date": "2018-02-04"
    }

    MOCK_NOTE_DICT = {
        "id": 191,
        "body": "Harum maxime consequuntur et et deleniti assumenda facilis.",
        "attachment": None,
        "author": {
            "id": 23,
            "name": "User 1",
            "username": "user1",
            "state": "active",
            "avatar_url": "https://www.gravatar.com/avatar/111d68d06e2d317b5a59c2c6c5bad808?s=80&d=identicon",
            "web_url": "http://localhost:3000/user1"
        },
        "created_at": "2017-09-05T08:01:32.068Z",
        "updated_at": "2017-09-05T08:01:32.068Z",
        "system": None,
        "noteable_id": 22,
        "noteable_type": "Issue",
        "project_id": 6,
        "noteable_iid": 2
    }

    MOCK_PROJECT_DICT = {
        "id": 3,
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "description_html": "<p data-sourcepos=\"1:1-1:56\" dir=\"auto\">Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>",
        "default_branch": "main",
        "visibility": "private",
        "ssh_url_to_repo": "git@example.com:diaspora/diaspora-project-site.git",
        "http_url_to_repo": "http://example.com/diaspora/diaspora-project-site.git",
        "web_url": "http://example.com/diaspora/diaspora-project-site",
        "readme_url": "http://example.com/diaspora/diaspora-project-site/blob/main/README.md",
        "tag_list": [
            "example",
            "disapora project"
        ],
        "topics": [
            "example",
            "disapora project"
        ],
        "owner": {
            "id": 3,
            "name": "Diaspora",
            "created_at": "2013-09-30T13:46:02Z"
        },
        "name": "Diaspora Project Site",
        "name_with_namespace": "Diaspora / Diaspora Project Site",
        "path": "diaspora-project-site",
        "path_with_namespace": "diaspora/diaspora-project-site",
        "issues_enabled": True,
        "open_issues_count": 1,
        "merge_requests_enabled": True,
        "jobs_enabled": True,
        "wiki_enabled": True,
        "snippets_enabled": False,
        "can_create_merge_request_in": True,
        "resolve_outdated_diff_discussions": False,
        "container_registry_enabled": False,
        "container_registry_access_level": "disabled",
        "security_and_compliance_access_level": "disabled",
        "container_expiration_policy": {
            "cadence": "7d",
            "enabled": False,
            "keep_n": None,
            "older_than": None,
            "name_regex": None,
            "name_regex_delete": None,
            "name_regex_keep": None,
            "next_run_at": "2020-01-07T21:42:58.658Z"
        },
        "created_at": "2013-09-30T13:46:02Z",
        "updated_at": "2013-09-30T13:46:02Z",
        "last_activity_at": "2013-09-30T13:46:02Z",
        "creator_id": 3,
        "namespace": {
            "id": 3,
            "name": "Diaspora",
            "path": "diaspora",
            "kind": "group",
            "full_path": "diaspora",
            "avatar_url": "http://localhost:3000/uploads/group/avatar/3/foo.jpg",
            "web_url": "http://localhost:3000/groups/diaspora"
        },
        "import_url": None,
        "import_type": None,
        "import_status": "none",
        "import_error": None,
        "permissions": {
            "project_access": {
                "access_level": 10,
                "notification_level": 3
            },
            "group_access": {
                "access_level": 50,
                "notification_level": 3
            }
        },
        "archived": False,
        "avatar_url": "http://example.com/uploads/project/avatar/3/uploads/avatar.png",
        "license_url": "http://example.com/diaspora/diaspora-client/blob/main/LICENSE",
        "license": {
            "key": "lgpl-3.0",
            "name": "GNU Lesser General Public License v3.0",
            "nickname": "GNU LGPLv3",
            "html_url": "http://choosealicense.com/licenses/lgpl-3.0/",
            "source_url": "http://www.gnu.org/licenses/lgpl-3.0.txt"
        },
        "shared_runners_enabled": True,
        "group_runners_enabled": True,
        "forks_count": 0,
        "star_count": 0,
        "runners_token": "b8bc4a7a29eb76ea83cf79e4908c2b",
        "ci_default_git_depth": 50,
        "ci_forward_deployment_enabled": True,
        "ci_forward_deployment_rollback_allowed": True,
        "ci_allow_fork_pipelines_to_run_in_parent_project": True,
        "ci_separated_caches": True,
        "ci_restrict_pipeline_cancellation_role": "developer",
        "ci_pipeline_variables_minimum_override_role": "maintainer",
        "ci_push_repository_for_job_token_allowed": False,
        "public_jobs": True,
        "shared_with_groups": [
            {
                "group_id": 4,
                "group_name": "Twitter",
                "group_full_path": "twitter",
                "group_access_level": 30
            },
            {
                "group_id": 3,
                "group_name": "Gitlab Org",
                "group_full_path": "gitlab-org",
                "group_access_level": 10
            }
        ],
        "repository_storage": "default",
        "only_allow_merge_if_pipeline_succeeds": False,
        "allow_merge_on_skipped_pipeline": False,
        "allow_pipeline_trigger_approve_deployment": False,
        "restrict_user_defined_variables": False,
        "only_allow_merge_if_all_discussions_are_resolved": False,
        "remove_source_branch_after_merge": False,
        "printing_merge_requests_link_enabled": True,
        "request_access_enabled": False,
        "merge_method": "merge",
        "squash_option": "default_on",
        "auto_devops_enabled": True,
        "auto_devops_deploy_strategy": "continuous",
        "approvals_before_merge": 0,
        "mirror": False,
        "mirror_user_id": 45,
        "mirror_trigger_builds": False,
        "only_mirror_protected_branches": False,
        "mirror_overwrites_diverged_branches": False,
        "external_authorization_classification_label": None,
        "packages_enabled": True,
        "service_desk_enabled": False,
        "service_desk_address": None,
        "autoclose_referenced_issues": True,
        "suggestion_commit_message": None,
        "enforce_auth_checks_on_uploads": True,
        "merge_commit_template": None,
        "squash_commit_template": None,
        "issue_branch_template": "gitlab/%{id}-%{title}",
        "marked_for_deletion_at": "2020-04-03",
        "marked_for_deletion_on": "2020-04-03",
        "compliance_frameworks": ["sox"],
        "warn_about_potentially_unwanted_characters": True,
        "statistics": {
            "commit_count": 37,
            "storage_size": 1038090,
            "repository_size": 1038090,
            "wiki_size": 0,
            "lfs_objects_size": 0,
            "job_artifacts_size": 0,
            "pipeline_artifacts_size": 0,
            "packages_size": 0,
            "snippets_size": 0,
            "uploads_size": 0,
            "container_registry_size": 0
        },
        "container_registry_image_prefix": "registry.example.com/diaspora/diaspora-client",
        "_links": {
            "self": "http://example.com/api/v4/projects",
            "issues": "http://example.com/api/v4/projects/1/issues",
            "merge_requests": "http://example.com/api/v4/projects/1/merge_requests",
            "repo_branches": "http://example.com/api/v4/projects/1/repository_branches",
            "labels": "http://example.com/api/v4/projects/1/labels",
            "events": "http://example.com/api/v4/projects/1/events",
            "members": "http://example.com/api/v4/projects/1/members",
            "cluster_agents": "http://example.com/api/v4/projects/1/cluster_agents"
        }
    }

    MOCK_SNIPPET_DICT = {
        "id": 1,
        "title": "test",
        "file_name": "add.rb",
        "description": "Ruby test snippet",
        "author": {
            "id": 1,
            "username": "john_smith",
            "email": "john@example.com",
            "name": "John Smith",
            "state": "active",
            "created_at": "2012-05-23T08:00:58Z"
        },
        "updated_at": "2012-06-28T10:52:04Z",
        "created_at": "2012-06-28T10:52:04Z",
        "imported": False,
        "imported_from": "none",
        "project_id": 1,
        "web_url": "http://example.com/example/example/snippets/1",
        "raw_url": "http://example.com/example/example/snippets/1/raw"
    }

    MOCK_USER_DICT = {
        "id": 1,
        "username": "john_smith",
        "name": "John Smith",
        "state": "active",
        "locked": False,
        "avatar_url": "http://localhost:3000/uploads/user/avatar/1/cd8.jpeg",
        "web_url": "http://localhost:3000/john_smith"
    }

    MOCK_WIKI_BLOB_DICT = {
        "basename": "home",
        "data": "hello\n\nand bye\n\nend",
        "path": "home.md",
        "filename": "home.md",
        "id": None,
        "ref": "main",
        "startline": 5,
        "project_id": 6,
        "group_id": None
    }

    MOCK_SIGNATURE_DICT = {
        'name': 'Akamai API Access Tokens',
        'status': 'enabled',
        'author': 'PaperMtn',
        'date': '2023-12-22',
        'description': 'Detects exposed Akamai API Access tokens',
        'severity': '90',
        'notes': None,
        'references': None,
        'watchman_apps': {
            'gitlab': {
                'scope': [
                    'blobs'
                ],
                'search_strings': [
                    'akab-'
                ]
            }
        },
        'test_cases': {
            'match_cases': [
                'client_token: akab-rWdcwwASNbe9fcGk-00qwecOueticOXxA'
            ],
            'fail_cases': [
                'host: akab-fakehost.akamaiapis.net'
            ]
        },
        'patterns': [
            'akab-[0-9a-zA-Z]{16}-[0-9a-zA-Z]{16}'
        ]
    }


@pytest.fixture
def mock_commit():
    return commit.create_from_dict(GitLabMockData.MOCK_COMMIT_DICT)


@pytest.fixture
def mock_blob():
    return blob.create_from_dict(GitLabMockData.MOCK_BLOB_DICT)


@pytest.fixture
def mock_file():
    return file.create_from_dict(GitLabMockData.MOCK_FILE_DICT)


@pytest.fixture
def mock_group():
    return group.create_from_dict(GitLabMockData.MOCK_GROUP_DICT)


@pytest.fixture
def mock_issue():
    return issue.create_from_dict(GitLabMockData.MOCK_ISSUE_DICT)


@pytest.fixture
def mock_merge_request():
    return merge_request.create_from_dict(GitLabMockData.MOCK_MERGE_REQUEST_DICT)


@pytest.fixture
def mock_milestone():
    return milestone.create_from_dict(GitLabMockData.MOCK_MILESTONE_DICT)


@pytest.fixture
def mock_note():
    return note.create_from_dict(GitLabMockData.MOCK_NOTE_DICT)


@pytest.fixture
def mock_project():
    return project.create_from_dict(GitLabMockData.MOCK_PROJECT_DICT)


@pytest.fixture
def mock_snippet():
    return snippet.create_from_dict(GitLabMockData.MOCK_SNIPPET_DICT)


@pytest.fixture
def mock_user():
    return user.create_from_dict(GitLabMockData.MOCK_USER_DICT)


@pytest.fixture
def mock_wiki_blob():
    return wiki_blob.create_from_dict(GitLabMockData.MOCK_WIKI_BLOB_DICT)

@pytest.fixture
def mock_signature():
    return signature.create_from_dict(GitLabMockData.MOCK_SIGNATURE_DICT)