# pylint: disable=global-statement,import-error
"""unittest for main.py file"""
from apis.ga_api import GaAPI as GA
import pytest
from os import path, remove


@pytest.fixture(scope='function')
def resource_setup():
    print("resource_setup")
    yield
    if path.exists("data_file.json"):
        remove("data_file.json")


@pytest.fixture(scope='function', params=[
    ({"3": "d"}, True),
    ({"4": "d"}, True),
    ({"3": "e"}, False),
])
def param_test_compare_change_in_data(request):
    return request.param


@pytest.fixture(scope='function', params=[
    ({"test": 'notNone'}, True),
    ({"test": None}, False),
    ({"NotTest": "notNone"}, False),
])
def param_test_has_field(request):
    return request.param


def test_compare_change_in_data(param_test_compare_change_in_data):
    old_data = {"1": "q", "2": "w", "3": "e"}
    (new_data, expected_output) = param_test_compare_change_in_data
    result = GA.compare_stages(old_data, new_data)
    assert result is expected_output


# def test_stage_changes(resource_setup):
#     """test func save new data"""
#     test_data = {"1": "test"}
#     assert GA.stage_changes(test_data) is True


def test_check_field(param_test_has_field):
    """test json field checker"""
    name_field = "test"
    (data_json, expected_output) = param_test_has_field
    result = GA.has_field(name_field, data_json)
    assert result is expected_output

