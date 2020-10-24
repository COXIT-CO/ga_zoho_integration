import json
import sys
from logging.config import dictConfig
from os import path

import requests
import zcrmsdk as zoho_crm
from flask import Flask, request, Response

from config import *

dictConfig(LOG_CONFIG)
LOGGER = logging.getLogger()

APP = Flask(__name__)


def get_access_token():
    if path.isfile(CONFIG_ZOHO['token_persistence_path'] + 'zcrm_oauthtokens.pkl'):
        _access_token = OAUTH_TOKEN.get_access_token(ZOHO_LOGIN_EMAIL)
    else:
        oauth_tokens = OAUTH_TOKEN.generate_access_token(ZOHO_GRANT_TOKEN)
        _access_token = oauth_tokens.get_access_token()
    return _access_token


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
                    LOGGER.info("Update successfully send to Google Analytic")

    return Response(status=200)


if __name__ == '__main__':

    zoho_crm.ZCRMRestClient.initialize(CONFIG_ZOHO)
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
        LOGGER.error("Can`t access to ZohoCRM. Check if grant token and domain is valid")
        LOGGER.exception(ex)
    else:
        APP.run(host=HOST, port=PORT)
