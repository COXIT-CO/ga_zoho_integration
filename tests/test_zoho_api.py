""" This file tests ZohoAPI class """
import logging
from mock import patch, Mock # pylint: disable=import-error
from ..apis.zoho_api import ZohoAPI
from ..config import AppConfig


@patch("ga_zoho_integration.apis.zoho_api.ZohoAPI.__init__")
def test_init_zoho(mock_init):
    """Test checks if __init__ function is called"""
    api_config = Mock(spec=AppConfig)
    mock_init.return_value = None
    ZohoAPI(api_config)
    mock_init.assert_called_once()


def test_make_input_json():
    """Test checks make_input_json function"""
    zoho_api = Mock(spec=ZohoAPI)
    zoho_api.notify_url = 'test.com'
    result = ZohoAPI.make_input_json(zoho_api)
    assert result['watch'][0]['notify_url'] == 'test.com'


def test_enable_notifications():
    """Test checks if runs refresh_access_token function"""
    zoho_api = Mock(spec=ZohoAPI)
    try:
        ZohoAPI.enable_notifications(zoho_api)
    except AttributeError:
        pass

    zoho_api.refresh_access_token.assert_called_once()


def test_raise_refresh_token_error(caplog):
    """Test checks raising log error when access token is not valid"""
    zoho_api = Mock(spec=ZohoAPI)
    zoho_api.login_email = "test_raise_exception@gmail.com"

    with caplog.at_level(logging.DEBUG):
        ZohoAPI.refresh_access_token(zoho_api)

    assert "Unable to refresh access token" in caplog.text


def test_raise_get_response_error(caplog):
    """Test checks raising log error when cannot get access to Zoho"""
    zoho_api = Mock(spec=ZohoAPI)
    zoho_api.api_base_url = "test@gmail.com"
    zoho_api.access_token = "test_token"

    with caplog.at_level(logging.DEBUG):
        ZohoAPI.get_response(zoho_api, 'test', 'test')

    assert "The application can not get access to Zoho. Check the access token" in caplog.text
