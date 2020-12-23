# pylint: disable=import-error
"""Python script which integrates Zoho CRM deals data with google analytics"""
from threading import Timer
from logging import getLogger
from flask import Flask, request, Response
from ga_zoho_integration.config import AppConfig
from ga_zoho_integration.apis.zoho_api import ZohoAPI
from ga_zoho_integration.apis.ga_api import GaAPI

APP = Flask(__name__)
CONFIGS = AppConfig()
LOGGER = getLogger('app')


@APP.route(CONFIGS.zoho_notification_endpoint, methods=['POST'])
def respond():
    """receives data from zoho and posts it to google analytics  """
    if "module" not in request.json:
        return Response(status=500)

    module = request.json["module"]
    ids = request.json["ids"][0]

    zoho_resp = ZOHO.get_response(module, ids)
    if zoho_resp:
        return GA.send_requests(zoho_resp, ids)
    return Response(status=500)


if __name__ == '__main__':

    ZOHO = ZohoAPI(CONFIGS)
    GA = GaAPI()

    ZOHO.enable_notifications()

    ENABLE_NOTIFICATIONS_THREAD = Timer(23 * 3600, ZOHO.enable_notifications)
    ENABLE_NOTIFICATIONS_THREAD.start()

    REFRESH_TOKEN_THREAD = Timer(3300, ZOHO.refresh_access_token)
    REFRESH_TOKEN_THREAD.start()

    APP.run(host="0.0.0.0", port=CONFIGS.port)
