from dataclasses import dataclass

from . import user


@dataclass(slots=True)
class Snippet(object):
    """ Class that defines User objects for GitLab snippets"""

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


@dataclass(slots=True)
class File(object):

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

    return Snippet(
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
