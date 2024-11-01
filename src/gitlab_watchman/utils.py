import time
import json
import dataclasses
from typing import List, Dict


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def convert_time(timestamp: str) -> int:
    """Convert ISO 8601 timestamp to epoch """

    pattern = '%Y-%m-%dT%H:%M:%S.%f%z'
    return int(time.mktime(time.strptime(timestamp, pattern)))


def deduplicate_results(input_list: List[Dict]) -> List[Dict]:
    """ Removes duplicates where results are returned by multiple queries
    Nested class handles JSON encoding for dataclass objects

    Args:
        input_list: List of dataclass objects
    Returns:
        List of JSON objects with duplicates removed
    """

    json_set = {json.dumps(dictionary, sort_keys=True, cls=EnhancedJSONEncoder) for dictionary in input_list}

    return [json.loads(t) for t in json_set]


def split_to_chunks(input_list, no_of_chunks):
    """Split the input list into n amount of chunks"""

    return (input_list[i::no_of_chunks] for i in range(no_of_chunks))