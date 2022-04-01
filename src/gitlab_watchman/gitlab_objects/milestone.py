from dataclasses import dataclass


@dataclass
class Milestone(object):
    """ Class that defines Milestone objects for GitLab milestones"""

    __slots__ = [
        'id',
        'iid',
        'project_id',
        'title',
        'description',
        'state',
        'created_at',
        'updated_at',
        'due_date',
        'start_date',
        'expired',
        'web_url'
    ]

    id: str
    iid: str
    project_id: str
    title: str
    description: str
    state: str
    created_at: str
    updated_at: str
    due_date: str
    start_date: str
    expired: str
    web_url: str


def create_from_dict(milestone_dict: dict) -> Milestone:
    """ Create a MergeRequest object from a dict response from the GitLab API

    Args:
        milestone_dict: dict/JSON format data from GitLab API
    Returns:
        A new MergeRequest object
    """

    milestone_object = Milestone(
        id=milestone_dict.get('id'),
        iid=milestone_dict.get('iid'),
        title=milestone_dict.get('title'),
        description=milestone_dict.get('description'),
        state=milestone_dict.get('state'),
        created_at=milestone_dict.get('created_at'),
        updated_at=milestone_dict.get('updated_at'),
        due_date=milestone_dict.get('due_date'),
        start_date=milestone_dict.get('start_date'),
        expired=milestone_dict.get('expired'),
        web_url=milestone_dict.get('web_url'),
        project_id=milestone_dict.get('project_id')
    )

    return milestone_object
