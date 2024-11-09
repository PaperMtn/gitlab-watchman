from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

import pytest

from gitlab_watchman.utils import (
    convert_to_epoch,
    convert_to_utc_datetime,
    deduplicate_results,
    convert_to_dict
)


def test_convert_to_epoch():
    # Test with a correct ISO 8601 timestamp containing seconds
    string_timestamp = '2021-09-20T10:00:00.000+00:00'
    expected_output = 1632132000
    assert convert_to_epoch(string_timestamp) == expected_output

    # Test with a correct ISO 8601 timestamp containing milliseconds
    string_timestamp = '2021-09-20T10:00:00.123+00:00'
    expected_output = 1632132000
    assert convert_to_epoch(string_timestamp) == expected_output

    # Test with a correct ISO 8601 timestamp containing microseconds
    string_timestamp = '2021-09-20T10:00:00.123456+00:00'
    expected_output = 1632132000
    assert convert_to_epoch(string_timestamp) == expected_output

    # Test with a correct ISO 8601 timestamp with different timezone - +05:00
    string_timestamp = '2021-09-20T15:00:00.000+05:00'
    expected_output = 1632132000
    assert convert_to_epoch(string_timestamp) == expected_output

    # Test with a correct ISO 8601 timestamp with different timezone - -05:00
    string_timestamp = '2021-09-20T05:00:00.000-05:00'
    expected_output = 1632132000
    assert convert_to_epoch(string_timestamp) == expected_output

    # Test with None input - Should gracefully fail and return None
    string_timestamp = None
    expected_output = None
    assert convert_to_epoch(string_timestamp) == expected_output


def test_convert_to_utc_datetime():
    # Test datetime object is returned
    assert isinstance(convert_to_utc_datetime('2021-09-20T10:00:00.000+00:00'), datetime)

    # Test with a correct ISO 8601 timestamp containing seconds
    string_timestamp = '2021-09-20T10:00:00.000+00:00'
    expected_output = '2021-09-20 10:00:00'
    assert convert_to_utc_datetime(string_timestamp).strftime('%Y-%m-%d %H:%M:%S') == expected_output

    # Test with a correct ISO 8601 timestamp containing milliseconds
    string_timestamp = '2021-09-20T10:00:00.123+00:00'
    expected_output = '2021-09-20 10:00:00'
    assert convert_to_utc_datetime(string_timestamp).strftime('%Y-%m-%d %H:%M:%S') == expected_output

    # Test with a correct ISO 8601 timestamp containing microseconds
    string_timestamp = '2021-09-20T10:00:00.123456+00:00'
    expected_output = '2021-09-20 10:00:00'
    assert convert_to_utc_datetime(string_timestamp).strftime('%Y-%m-%d %H:%M:%S') == expected_output

    # Test with a correct ISO 8601 timestamp with different timezone - +05:00
    string_timestamp = '2021-09-20T15:00:00.000+05:00'
    expected_output = '2021-09-20 10:00:00'
    assert convert_to_utc_datetime(string_timestamp).strftime('%Y-%m-%d %H:%M:%S') == expected_output

    # Test with a correct ISO 8601 timestamp with different timezone - -05:00
    string_timestamp = '2021-09-20T05:00:00.000-05:00'
    expected_output = '2021-09-20 10:00:00'
    assert convert_to_utc_datetime(string_timestamp).strftime('%Y-%m-%d %H:%M:%S') == expected_output

    # Test with output string containing timezone
    string_timestamp = '2021-09-20T05:00:00.000-05:00'
    expected_output = '2021-09-20 10:00:00 UTC'
    assert convert_to_utc_datetime(string_timestamp).strftime('%Y-%m-%d %H:%M:%S %Z') == expected_output

    # Test with None input - Should gracefully fail and return None
    string_timestamp = None
    expected_output = None
    assert convert_to_utc_datetime(string_timestamp) == expected_output


@dataclass
class TestClass:
    __test__ = False
    name: str
    age: int


@pytest.fixture
def simple_example_result() -> Dict[Any, Any]:
    return {
        "file": {
            "created": "2024-01-01 00:00:00 UTC",
            "editable": False,
            "user": "UABC123"
        },
        "user": {
            "name": "Joe Bloggs",
            "age": 30,
        },
        "watchman_id": "abc123"
    }


@pytest.fixture
def dataclass_example_result_one() -> Dict[Any, Any]:
    return {
        "file": {
            "created": "2024-01-01 00:00:00 UTC",
            "editable": False,
            "user": "UABC123"
        },
        "user": TestClass(name='Joe Bloggs', age=30),
        "watchman_id": "abc123"
    }


@pytest.fixture
def dataclass_example_result_two() -> Dict[Any, Any]:
    return {
        "match_string": "2840631",
        "message": {
            "created": "2024-01-01 00:00:00 UTC",
            "id": "abcdefghijklmnopqrstuvwxyz",
            "permalink": "https://example.com",
            "text": "This is a message",
            "timestamp": "1729257170.452549",
            "type": "message",
            "user": TestClass(name='John Smith', age=30)
        },
        "watchman_id": "abc1234"
    }


def test_convert_to_dict(simple_example_result: Dict[Any, Any],
                         dataclass_example_result_one: Dict[Any, Any]) -> None:
    # Test with simple example
    assert convert_to_dict(simple_example_result) == simple_example_result

    # Test with dataclass example
    assert convert_to_dict(dataclass_example_result_one) == simple_example_result


def test_deduplicate_results(simple_example_result: Dict[Any, Any],
                             dataclass_example_result_one: Dict[Any, Any],
                             dataclass_example_result_two: Dict[Any, Any]) -> None:
    # Test with a single result
    assert deduplicate_results([simple_example_result]) == [simple_example_result]

    # Test with multiple results containing duplicates
    assert deduplicate_results([simple_example_result, simple_example_result]) == [
        simple_example_result]

    # Test with dataclass example
    assert deduplicate_results([dataclass_example_result_one]) == [convert_to_dict(dataclass_example_result_one)]

    # Test with multiple dataclass examples with no duplicates
    assert deduplicate_results([dataclass_example_result_one, dataclass_example_result_two]) == [
        convert_to_dict(dataclass_example_result_two), convert_to_dict(dataclass_example_result_one)]

    # Test with multiple dataclass examples with duplicates
    assert (deduplicate_results([dataclass_example_result_one, dataclass_example_result_one]) ==
            [convert_to_dict(dataclass_example_result_one)])
