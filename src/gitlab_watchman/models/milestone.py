from dataclasses import dataclass
from datetime import datetime

from gitlab_watchman.utils import convert_to_utc_datetime


@dataclass(slots=True)
# pylint: disable=too-many-instance-attributes
class Milestone:
    """ Class that defines Milestone objects for GitLab milestones"""

    id: str
    iid: str
    project_id: str
    title: str
    description: str
    state: str
    created_at: datetime | None
    updated_at: datetime | None
    due_date: datetime | None
    start_date: datetime | None
    expired: str
    web_url: str


def create_from_dict(milestone_dict: dict) -> Milestone:
    """ Create a MergeRequest object from a dict response from the GitLab API

    Args:
        milestone_dict: dict/JSON format data from GitLab API
    Returns:
        A new MergeRequest object
    """

    return Milestone(
        id=milestone_dict.get('id'),
        iid=milestone_dict.get('iid'),
        title=milestone_dict.get('title'),
        description=milestone_dict.get('description'),
        state=milestone_dict.get('state'),
        created_at=convert_to_utc_datetime(milestone_dict.get('created_at')),
        updated_at=convert_to_utc_datetime(milestone_dict.get('updated_at')),
        due_date=convert_to_utc_datetime(milestone_dict.get('due_date')),
        start_date=convert_to_utc_datetime(milestone_dict.get('start_date')),
        expired=milestone_dict.get('expired'),
        web_url=milestone_dict.get('web_url'),
        project_id=milestone_dict.get('project_id')
    )
