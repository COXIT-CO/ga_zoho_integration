import json
import logging
import sys
from logging.config import dictConfig
from os import path

import requests
import zcrmsdk as zoho_crm
from flask import Flask, request, Response
from pyga.entities import Visitor

import config

dictConfig(config.logging_config)
LOGGER = logging.getLogger()

# TODO: make following data configurable on script startup (passed as arguments)
ZOHO_LOGIN_EMAIL = "yehorzhornovyi@gmail.com"
ZOHO_GRANT_TOKEN = "1000.9e7799487e3bf285e5cb24c8e6fc7700.3d4a54cf2a7d353c8e30365df10c7d2c"
ZOHO_CLIENT_ID = "1000.6UBJGFQ9ZBEU8R4OF9X35FZ4KROLJO"
ZOHO_CLIENT_SECRET = "538947a51fc6138b864550f447e75d8c3ba2edd0c3"
ZOHO_ACCOUNT_DOMEN = "eu"

ZOHO_API_URL = "https://www.zohoapis." + ZOHO_ACCOUNT_DOMEN
DEALS_ENDPOINT = "/crm/v2/Deals"
ENABLE_NOTIFICATIONS_ENDPOINT = "/crm/v2/actions/watch"
ZOHO_NOTIFICATIONS_ENDPOINT = "/zoho/deals/change"
GOOGLE_ANALYTICS_API_URL = "https://www.google-analytics.com"
GOOGLE_ANALYTICS_COLLECT_ENDPOINT = "/collect"

CONFIG = {
    "apiBaseUrl": ZOHO_API_URL,
    "token_persistence_path": "./",
    "currentUserEmail": ZOHO_LOGIN_EMAIL,
    "client_id": ZOHO_CLIENT_ID,
    "client_secret": ZOHO_CLIENT_SECRET,
    "redirect_uri": "https://coxit.co",
    "accounts_url": "https://accounts.zoho." + ZOHO_ACCOUNT_DOMEN,
}
REQUEST_INPUT_JSON = {
    "watch": [
        {
            "channel_id": "1000000068002",
            "events": [
                "Deals.edit"
            ],
            "token": "TOKEN_FOR_VERIFICATION_OF_1000000068002",
            "notify_url": "https://dc4925b7ee28.ngrok.io" + ZOHO_NOTIFICATIONS_ENDPOINT,
        }
    ]
}
APP = Flask(__name__)


def get_access_token():
    if path.isfile(CONFIG['token_persistence_path'] + 'zcrm_oauthtokens.pkl'):
        _access_token = oauth_client.get_access_token(ZOHO_LOGIN_EMAIL)
    else:
        oauth_tokens = oauth_client.generate_access_token(ZOHO_GRANT_TOKEN)
        _access_token = oauth_tokens.get_access_token()
    return _access_token


@APP.route(ZOHO_NOTIFICATIONS_ENDPOINT, methods=['POST'])
def respond():
    # get deals records
    auth_header = {"Authorization": "Zoho-oauthtoken " + access_token}
    module = request.json["module"]
    for id_str in request.json["ids"]:
        try:
            resp = requests.get(url=ZOHO_API_URL + "/crm/v2/" + module + "/" + id_str,
                                headers=auth_header)
            resp.raise_for_status()
        except requests.RequestException as ex:
            LOGGER.error("The application can not get access to Zoho. Check the access token")
            LOGGER.exception(ex)
        else:
            try:
                current_stage = resp.json()["data"][0]["Stage"]
                LOGGER.info("id=" + id_str + ": current stage is " + current_stage)
            except IndexError as ex:
                LOGGER.exception(ex)
                return Response(status=500)
            else:
                # TODO:Get record from DB and compare stages,
                #  if stage changed then make POST request to analytic
                user = Visitor()

                params = {
                    "v": "1",
                    "t": "event",
                    # TODO Change initialization of tid and uid parameters.
                    "tid": "UA-180087680-1",
                    "uid": user.generate_unique_id(),
                    "ec": "zoho_stage_change",
                    "ea": "stage_change",
                    "el": current_stage,
                    "ua": "Opera / 9.80"
                }
                try:
                    resp = requests.post(url=GOOGLE_ANALYTICS_API_URL +
                                             GOOGLE_ANALYTICS_COLLECT_ENDPOINT,
                                         params=params)
                    resp.raise_for_status()
                except requests.RequestException as ex:
                    LOGGER.error(ex)
                    return Response(status=401)
                else:
                    LOGGER.info("Update succesfully send to Google Analytic")

    return Response(status=200)


if __name__ == '__main__':

    zoho_crm.ZCRMRestClient.initialize(CONFIG)
    oauth_client = zoho_crm.ZohoOAuth.get_client_instance()
    # Enable Zoho Notifications
    access_token = None
    try:
        access_token = get_access_token()
    except zoho_crm.OAuthUtility.ZohoOAuthException as e:
        LOGGER.exception(e)
        sys.exit("Access token data is invalid")

    header = {"Authorization": "Zoho-oauthtoken " + access_token,
              'Content-type': 'application/json'}
    try:
        resp = requests.post(url=ZOHO_API_URL + ENABLE_NOTIFICATIONS_ENDPOINT, headers=header,
                             data=json.dumps(REQUEST_INPUT_JSON))
        resp.raise_for_status()
    except requests.RequestException as ex:
        LOGGER.error("Can`t access to ZohoCRM. Check if grant token and domen is valid")
        LOGGER.exception(ex)
    else:
        APP.run(host="127.0.0.1", port=5050)
