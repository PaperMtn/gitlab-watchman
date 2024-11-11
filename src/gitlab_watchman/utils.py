import json
import dataclasses
from datetime import datetime
from typing import List, Dict, Any

import pytz


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def convert_to_epoch(timestamp: str | datetime) -> int | None:
    """ Convert ISO 8601 formatted strings to int epoch timestamps

        ISO 8601 formatted strings are formatted as:
            YYYY-MM-DDTHH:MM:SS.SSS+HH:MM

    Args:
        timestamp: ISO 8601 formatted string, example: 2024-01-01T00:00:00.000+00:00
    Returns:
        int epoch timestamp
    """

    try:
        if isinstance(timestamp, datetime):
            return int(timestamp.timestamp())
        else:
            pattern = '%Y-%m-%dT%H:%M:%S.%f%z'
            return int(datetime.strptime(timestamp, pattern).timestamp())
    except TypeError:
        return None


def convert_to_utc_datetime(timestamp: str) -> datetime | None:
    """ Convert ISO 8601 formatted strings to datetime objects.
        Datetimes are returned in UTC.
        Accepted inputs:
            ISO 8601 Datetime with Timezone: YYYY-MM-DDTHH:MM:SS.SSS+HH:MM
            ISO 8601 Datetime without Timezone: YYYY-MM-DDTHH:MM:SS.SSSZ
            ISO 8601 Date: YYYY-MM-DD

    Args:
        timestamp: ISO 8601 formatted string
    Returns:
        datetime object
    """

    try:
        try:
            dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')
            return dt.astimezone(pytz.utc)
        except ValueError:
            try:
                dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
                return dt.astimezone(pytz.utc)
            except ValueError:
                return datetime.strptime(timestamp, '%Y-%m-%d')
    except TypeError:
        return None


def convert_to_dict(obj: Any) -> Dict:
    """ Returns a dictionary object from a dataclass object or a dict
    containing nested dataclass objects.

    Args:
        obj: dataclass object or dict
    Returns:
        Dictionary object
    """

    json_object = json.dumps(obj, sort_keys=True, cls=EnhancedJSONEncoder)
    return json.loads(json_object)


def deduplicate_results(input_list: List[Any]) -> List[Dict]:
    """ Removes duplicates where results are returned by multiple queries. This is done
    using the `watchman_id` field in the detection data to identify the same findings.

    The `watchman_id` is a hash that is generated for each finding from the match string,
     meaning the same message won't be returned multiple times.

    Args:
        input_list: List of dataclass objects
    Returns:
        List of JSON objects with duplicates removed
    """

    converted_dict_list = [convert_to_dict(t) for t in input_list]
    return list({match.get('watchman_id'): match for match in reversed(converted_dict_list)}.values())


def split_to_chunks(input_list, no_of_chunks):
    """Split the input list into n amount of chunks"""

    return (input_list[i::no_of_chunks] for i in range(no_of_chunks))
