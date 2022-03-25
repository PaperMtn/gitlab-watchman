from dataclasses import dataclass

from gitlab_watchman.gitlab_objects import user


@dataclass
class Snippet(object):
    """ Class that defines User objects for GitLab snippets"""

    __slots__ = [
        'id',
        'title',
        'description',
        'visibility',
        'updated_at',
        'created_at',
        'web_url',
        'author',
        'file_name',
        'files',
    ]

    id: str
    title: str
    description: str
    visibility: str or bool
    created_at: str
    updated_at: str
    web_url: str
    author: user.User
    file_name: str
    files: list


@dataclass
class File(object):
    __slots__ = [
        'path',
        'raw_url',
    ]

    path: str
    raw_url: str


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

    snippet_object = Snippet(
        id=snip_dict.get('id'),
        title=snip_dict.get('title'),
        description=snip_dict.get('description'),
        visibility=snip_dict.get('visibility'),
        author=user.create_from_dict(snip_dict.get('author', {})),
        created_at=snip_dict.get('created_at'),
        updated_at=snip_dict.get('updated_at'),
        web_url=snip_dict.get('web_url'),
        file_name=snip_dict.get('file_name'),
        files=file_list
    )

    return snippet_object
