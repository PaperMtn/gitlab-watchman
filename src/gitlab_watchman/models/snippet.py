from dataclasses import dataclass
from datetime import datetime
from typing import List

from gitlab_watchman.models import user
from gitlab_watchman.utils import convert_to_utc_datetime


@dataclass(slots=True)
class File:
    """ Class that defines File objects for GitLab snippets"""
    path: str
    raw_url: str


@dataclass(slots=True)
class Snippet:
    """ Class that defines User objects for GitLab snippets"""

    id: str
    title: str
    description: str
    visibility: str or bool
    created_at: datetime | None
    updated_at: datetime | None
    web_url: str
    author: user.User
    file_name: str
    files: List[File]


def create_from_dict(snip_dict: dict) -> Snippet:
    """ Create a Snippet object from a dict response from the GitLab API

    Args:
        snip_dict: dict/JSON format data from GitLab API
    Returns:
        A new Snippet object
    """
    file_list = []
    if snip_dict.get('files'):
        for f in snip_dict.get('files'):
            file_list.append(File(
                path=f.get('path'),
                raw_url=f.get('raw_url')
            ))
    else:
        file_list = None

    if snip_dict.get('author'):
        author = user.create_from_dict(snip_dict.get('author'))
    else:
        author = None

    return Snippet(
        id=snip_dict.get('id'),
        title=snip_dict.get('title'),
        description=snip_dict.get('description'),
        visibility=snip_dict.get('visibility'),
        author=author,
        created_at=convert_to_utc_datetime(snip_dict.get('created_at')),
        updated_at=convert_to_utc_datetime(snip_dict.get('updated_at')),
        web_url=snip_dict.get('web_url'),
        file_name=snip_dict.get('file_name'),
        files=file_list
    )
