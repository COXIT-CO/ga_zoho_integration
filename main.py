# pylint: disable=global-statement,import-error
"""Python script which integrates Zoho CRM deals data with google analytics"""
import sys
from threading import Timer
from zcrmsdk import OAuthUtility
from config import AppConfig
from flask import Flask, request, Response
from apis.zoho_api import ZohoAPI
from apis.ga_api import GaAPI
from requests import RequestException
from logging import getLogger

APP = Flask(__name__)
CONFIGS = AppConfig()
LOGGER = getLogger('app')

@APP.route(CONFIGS.ZOHO_NOTIFICATIONS_ENDPOINT, methods=['POST'])
def respond():
    """generate post request to google analytics  """

    if zoho.refresh_access_token() :
        return Response(status=500)
    # getting deals records

    if "module" not in request.json:
        return Response(status=500)

    module = request.json["module"]
    ids = request.json["ids"][0]

    zoho_resp = zoho.get_response(module, ids)
    if zoho_resp:
        return ga.send_requests(zoho_resp, ids)


if __name__ == '__main__':
    try:
        zoho = ZohoAPI(CONFIGS)
    except OAuthUtility.ZohoOAuthException as ex:
        LOGGER.error(ex)
        sys.exit("Passed data in parameters is invalid. Script is terminated")
    ga = GaAPI()
    try:
        zoho.enable_notifications()
        t = Timer(23 * 3600, zoho.enable_notifications())
        t.start()

    except RequestException as ex:
        LOGGER.error(
            "ZohoCRM does not response. Check selected scopes generating grant_token",
            exc_info=ex)
    else:
        APP.run(host="0.0.0.0", port=CONFIGS.port)
