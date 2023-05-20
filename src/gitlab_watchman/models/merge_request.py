from dataclasses import dataclass

from . import user


@dataclass(slots=True)
class MergeRequest(object):
    """ Class that defines MergeRequest objects for GitLab merge requests"""

    id: str
    iid: str
    project_id: str
    title: str
    description: str
    state: str
    created_at: str
    updated_at: str
    merged_by: user.User
    merged_at: str
    target_branch: str
    source_branch: str
    author: user.User
    source_project_id: str
    target_project_id: str
    merge_status: str
    web_url: str


def create_from_dict(mr_dict: dict) -> MergeRequest:
    """ Create a MergeRequest object from a dict response from the GitLab API

    Args:
        mr_dict: dict/JSON format data from GitLab API
    Returns:
        A new MergeRequest object
    """
    if mr_dict.get('merged_by'):
        merged_by = user.create_from_dict(mr_dict.get('merged_by'))
    else:
        merged_by = None

    return MergeRequest(
        id=mr_dict.get('id'),
        iid=mr_dict.get('iid'),
        project_id=mr_dict.get('project_id'),
        title=mr_dict.get('title'),
        description=mr_dict.get('description'),
        state=mr_dict.get('state'),
        created_at=mr_dict.get('created_at'),
        updated_at=mr_dict.get('updated_at'),
        merged_by=merged_by,
        merged_at=mr_dict.get('merged_at'),
        target_branch=mr_dict.get('target_branch'),
        source_branch=mr_dict.get('source_branch'),
        author=user.create_from_dict(mr_dict.get('author')),
        source_project_id=mr_dict.get('source_project_id'),
        target_project_id=mr_dict.get('target_project_id'),
        merge_status=mr_dict.get('merge_status'),
        web_url=mr_dict.get('web_url'),
    )
