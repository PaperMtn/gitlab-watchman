from dataclasses import dataclass


@dataclass(slots=True)
class Group(object):
    """ Class that defines User objects for GitLab groups"""

    id: str
    name: str
    path: str
    description: str
    visibility: str
    require_two_factor_authentication: bool
    two_factor_grace_period: str
    auto_devops_enabled: bool
    emails_disabled: bool
    request_access_enabled: bool
    full_name: str
    full_path: str
    created_at: str
    web_url: str
    ip_restriction_ranges: str


def create_from_dict(group_dict: dict) -> Group:
    """ Create a Group object from a dict response from the GitLab API

    Args:
        group_dict: dict/JSON format data from GitLab API
    Returns:
        A new Project object
    """

    return Group(
        id=group_dict.get('id'),
        name=group_dict.get('name'),
        path=group_dict.get('path'),
        description=group_dict.get('description'),
        visibility=group_dict.get('visibility'),
        require_two_factor_authentication=group_dict.get('require_two_factor_authentication'),
        two_factor_grace_period=group_dict.get('two_factor_grace_period'),
        auto_devops_enabled=group_dict.get('auto_devops_enabled'),
        emails_disabled=group_dict.get('emails_disabled'),
        request_access_enabled=group_dict.get('request_access_enabled'),
        full_name=group_dict.get('full_name'),
        full_path=group_dict.get('full_path'),
        created_at=group_dict.get('created_at'),
        web_url=group_dict.get('web_url'),
        ip_restriction_ranges=group_dict.get('ip_restriction_ranges')
    )
