# pylint: disable=global-statement,import-error,pointless-string-statement
"""Python script which integrates Zoho CRM deals data with google analytics."""
import argparse
import json
import sys
from os import path

import logging
from logging.config import dictConfig

import requests
import zcrmsdk as zoho_crm
from flask import Flask, request, Response

from config import LOG_CONFIG

_ZOHO_NOTIFICATIONS_ENDPOINT = "/zoho/deals/change"
_ZOHO_LOGIN_EMAIL, _ZOHO_GRANT_TOKEN, _ZOHO_API_URI, _ACCESS_TOKEN, \
    _ZOHO_NOTIFY_URL, _PORT = "", "", "", "", "", ""
LOGGER = logging.getLogger()


def compare_change_in_data(old_data, new_data):
    """compare old stages and new stage. Return false if stage isnt change"""
    flag = False

    for key, value in old_data.items():
        if new_data.keys()[0] == key:
            if new_data.values()[0] != value:
                flag = True
            else:
                flag = False
                break
        else:
            flag = True

    return flag


def db_save_stage_info(new_data):
    """Save and compare data about stage in json file"""
    flag = True
    try:
        with open("data_file.json", "r") as read_file:
            old_data = json.load(read_file)

        if compare_change_in_data(old_data, new_data):
            old_data.update(new_data)
        else:
            flag = False

        with open("data_file.json", "w") as write_file:
            json.dump(old_data, write_file)

    except IOError:
        with open("data_file.json", "w") as write_file:
            json.dump(new_data, write_file)

    return flag


def create_parser():
    """Creat parameters passing from console"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--email')
    parser.add_argument('-gt', '--grant_token')
    parser.add_argument('-cid', '--client_id')
    parser.add_argument('-cs', '--client_secret')
    parser.add_argument('-api', '--api_uri', default='com')
    public_ip = "http://" + requests.get('http://ipinfo.io/json').json()['ip']
    parser.add_argument('-nu', '--notify_url', default=public_ip)
    parser.add_argument('-port', '--port', default='80')
    parser.add_argument('-log', '--logging', default='file')

    return parser


def initialize_variebles():
    """TODO: make following data configurable on script startup (passed as
    arguments)"""

    # change global variebles
    global _ZOHO_LOGIN_EMAIL, _ZOHO_GRANT_TOKEN, _ZOHO_API_URI, _ZOHO_NOTIFY_URL, \
        _PORT, LOGGER

    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    # Add parameters passing from console
    zoho_client_id = namespace.client_id
    zoho_client_secret = namespace.client_secret

    _ZOHO_LOGIN_EMAIL = namespace.email
    _ZOHO_GRANT_TOKEN = namespace.grant_token
    _ZOHO_API_URI = "https://www.zohoapis." + namespace.api_uri
    _ZOHO_NOTIFY_URL = namespace.notify_url
    _PORT = namespace.port

    LOG_CONFIG['root']['handlers'].append(namespace.logging)
    dictConfig(LOG_CONFIG)
    LOGGER = logging.getLogger()

    config = {
        "apiBaseUrl": _ZOHO_API_URI,
        "token_persistence_path": "./",
        "currentUserEmail": _ZOHO_LOGIN_EMAIL,
        "client_id": zoho_client_id,
        "client_secret": zoho_client_secret,
        "redirect_uri": "coxit.co",
        "accounts_url": "https://accounts.zoho." + namespace.api_uri,
    }

    return config


def creat_init_access_token():
    """creating _ACCESS_TOKEN and we check: how init this token """
    global _ACCESS_TOKEN

    zoho_crm.ZCRMRestClient.initialize(initialize_variebles())
    oauth_client = zoho_crm.ZohoOAuth.get_client_instance()
    if path.isfile('./zcrm_oauthtokens.pkl'):
        _ACCESS_TOKEN = oauth_client.get_access_token(_ZOHO_LOGIN_EMAIL)
    else:
        oauth_tokens = oauth_client.generate_access_token(_ZOHO_GRANT_TOKEN)
        _ACCESS_TOKEN = oauth_tokens.get_access_token()


APP = Flask(__name__)


@APP.route(_ZOHO_NOTIFICATIONS_ENDPOINT, methods=['POST'])
def respond():
    """generate post request to google analytics  """
    google_analytics_api_uri = "https://www.google-analytics.com"
    google_analytics_collect_endpoint = "/collect"

    """creating _ACCESS_TOKEN and we check: how init this token """
    global _ACCESS_TOKEN
    try:
        oauth_client = zoho_crm.ZohoOAuth.get_client_instance()
        _ACCESS_TOKEN = oauth_client.get_access_token(_ZOHO_LOGIN_EMAIL)
    except zoho_crm.OAuthUtility.ZohoOAuthException as ex:
        LOGGER.error("Unable to refresh access token", exc_info=ex)
        return Response(status=500)

    """ getting deals records """
    auth_header = {"Authorization": "Zoho-oauthtoken " + _ACCESS_TOKEN}
    module = request.json["module"]
    for ids in request.json["ids"]:
        try:
            response = requests.get(
                url=_ZOHO_API_URI +
                "/crm/v2/" +
                module +
                "/" +
                ids,
                headers=auth_header)
            response.raise_for_status()
        except requests.RequestException as ex:
            LOGGER.error(
                "The application can not get access to Zoho. Check the access token",
                exc_info=ex)
        else:
            try:
                current_stage = response.json()["data"][0]["Stage"]
                LOGGER.info(
                    "id=" +
                    ids +
                    ": current stage is " +
                    current_stage)

                current_google_id = response.json()["data"][0]["GA_client_id"]
                if current_google_id is None:
                    LOGGER.warning(
                        "GA_client_id is not found. Make sure you populate it in CRM.")
                LOGGER.info("GA_client_id is found!")

                ga_property_id = response.json()["data"][0]["GA_property_id"]
                if ga_property_id is None:
                    LOGGER.warning(
                        "GA_property_id is not found. Make sure you populate it in CRM. ")
                LOGGER.info("GA_property_id is found")
            except KeyError as ex:
                LOGGER.error(
                    "Incorrect response data. "
                    "Check if you added GA_client_id and GA_property_id variable to ZohoCRM",
                    exc_info=ex)
                LOGGER.info(response.json()["data"][0])
                return Response(status=500)
            else:
                params_for_ga = {
                    "v": "1",
                    "t": "event",
                    "tid": ga_property_id,
                    "cid": current_google_id,
                    "ec": "zoho_stage_change",
                    "ea": "stage_change",
                    "el": current_stage,
                    "ua": "Opera / 9.80"
                }
                data_stage = {response.json()["data"][0]["id"]: current_stage}
                if db_save_stage_info(data_stage):
                    try:
                        response = requests.post(
                            url=google_analytics_api_uri +
                            google_analytics_collect_endpoint,
                            params=params_for_ga)
                        response.raise_for_status()
                    except requests.RequestException as ex:
                        LOGGER.error(
                            "Unable to send post request to Google Analytics" +
                            "response.status_code = " +
                            str(
                                response.status_code) +
                            " - " +
                            response.text,
                            exc_info=ex)
                        return Response(status=401)
                    else:
                        LOGGER.info(
                            "Update successfully sent to Google Analytic")
                else:
                    LOGGER.info("Stage was not changed. Event was not sent")
    return Response(status=200)


def creat_requests():
    """creating request using webhook"""
    enable_notifications_endpoint = "/crm/v2/actions/watch"
    notify_url = _ZOHO_NOTIFY_URL + _ZOHO_NOTIFICATIONS_ENDPOINT

    request_input_json = {
        "watch": [
            {
                "channel_id": "1000000068002",
                "events": ["Deals.edit"],
                "token": "TOKEN_FOR_VERIFICATION_OF_1000000068002",
                "notify_url": notify_url,
            }]}

    # Enable Zoho Notifications
    header = {"Authorization": "Zoho-oauthtoken " + _ACCESS_TOKEN,
              'Content-type': 'application/json'}
    LOGGER.info(msg="Zoho-oauthtoken " + _ACCESS_TOKEN)
    resp = requests.post(
        url=_ZOHO_API_URI +
        enable_notifications_endpoint,
        headers=header,
        data=json.dumps(request_input_json))
    resp.raise_for_status()


if __name__ == '__main__':

    try:
        creat_init_access_token()
    except zoho_crm.OAuthUtility.ZohoOAuthException as ex:
        LOGGER.error(ex)
        sys.exit("Passed data in parameters is invalid. Script is terminated")

    try:
        creat_requests()
    except requests.RequestException as ex:
        LOGGER.error(
            "ZohoCRM does not response. Check selected scopes generating grant_token",
            exc_info=ex)
    else:
        APP.run(host="0.0.0.0", port=_PORT)
