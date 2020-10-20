import json
import logging
import sys
from logging.config import dictConfig
from os import path

import requests
import zcrmsdk as zoho_crm
from flask import Flask, request, Response

import config

dictConfig(config.logging_config)
LOGGER = logging.getLogger()

# TODO: make following data configurable on script startup (passed as arguments)
ZOHO_LOGIN_EMAIL = "yehorzhornovyi@gmail.com"
ZOHO_GRANT_TOKEN = "1000.bdc5d0fbe6272a08832501f7d456f6ff.c181a61f97601e4d6c1fe4730d4a7ffb"
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
            "notify_url": "https://3f41dcc5af10.ngrok.io" + ZOHO_NOTIFICATIONS_ENDPOINT,
        }
    ]
}
APP = Flask(__name__)


def get_access_token():
    if path.isfile(CONFIG['token_persistence_path'] + 'zcrm_oauthtokens.pkl'):
        _access_token = OAUTH_TOKEN.get_access_token(ZOHO_LOGIN_EMAIL)
    else:
        oauth_tokens = OAUTH_TOKEN.generate_access_token(ZOHO_GRANT_TOKEN)
        _access_token = oauth_tokens.get_access_token()
    return _access_token


@APP.route(ZOHO_NOTIFICATIONS_ENDPOINT, methods=['POST'])
def respond():
    # get deals records
    auth_header = {"Authorization": "Zoho-oauthtoken " + ACCESS_TOKEN}
    module = request.json["module"]
    for id_str in request.json["ids"]:
        try:
            resp = requests.get(url=ZOHO_API_URL + "/crm/v2/" + module + "/" + id_str,
                                headers=auth_header)
            ga_resp = requests.get(url=ZOHO_API_URL + "/crm/v2/settings/variables",
                                   headers=auth_header)
            resp.raise_for_status()
        except requests.RequestException as ex:
            LOGGER.error("The application can not get access to Zoho. Check the access token")
            LOGGER.exception(ex)
        else:
            try:
                current_stage = resp.json()["data"][0]["Stage"]
                ga_client_id = ga_resp.json()["variables"][0]["value"]
                LOGGER.info("id=" + id_str + ": current stage is " + current_stage)
            except KeyError as ex:
                LOGGER.exception(ex)
                LOGGER.error("Please add a variable in CRM settings "
                             "that contains client_id for Google Analytics")
                return Response(status=500)
            else:
                # TODO:Get record from DB and compare stages,
                #  if stage changed then make POST request to analytic

                params = {
                    "v": "1",
                    "t": "event",
                    "tid": "UA-180087680-1",
                    "cid": ga_client_id,
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
    OAUTH_TOKEN = zoho_crm.ZohoOAuth.get_client_instance()
    # Enable Zoho Notifications
    ACCESS_TOKEN = None
    try:
        ACCESS_TOKEN = get_access_token()
    except zoho_crm.OAuthUtility.ZohoOAuthException as ex:
        LOGGER.exception(ex)
        sys.exit("Access token data is invalid")

    HEADER = {"Authorization": "Zoho-oauthtoken " + ACCESS_TOKEN,
              'Content-type': 'application/json'}
    try:
        RESP = requests.post(url=ZOHO_API_URL + ENABLE_NOTIFICATIONS_ENDPOINT, headers=HEADER,
                             data=json.dumps(REQUEST_INPUT_JSON))
        RESP.raise_for_status()
    except requests.RequestException as ex:
        LOGGER.error("Can`t access to ZohoCRM. Check if grant token and domen is valid")
        LOGGER.exception(ex)
    else:
        APP.run(host="127.0.0.1", port=5050)
