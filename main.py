# pylint: disable=global-statement,import-error,too-many-return-statements
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


def stage_changes(new_data):
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
    flask_log = logging.getLogger('werkzeug')
    flask_log.setLevel(logging.ERROR)
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


def check_json_fields(name_field, data_json):
    """"write logs if bad fields"""
    if name_field in data_json:
        if data_json[name_field] is not None:
            LOGGER.info("%s is found!", name_field)
            return True
        else:
            LOGGER.warning(
                "%s is empty. Make sure you fill in it in CRM.", name_field)
    else:
        LOGGER.warning(
            "%s is not found. Make sure you populate it in CRM.", name_field)
        return False
    return True


def ga_request(response, params_for_ga):
    """"make requst to google anylitics"""
    google_analytics_api_uri = "https://www.google-analytics.com"
    google_analytics_collect_endpoint = "/collect"
    try:
        print "parameters for GA:\n", params_for_ga
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
        return Response(status=200)

def when_deal_in_closed_block(response, params_for_ga):
    """"make exclusive ga params change when deals in block CLOSED"""
    if check_json_fields("Amount", response.json()["data"][0]) is False:
        return False
    cd9 = response.json()["data"][0]["Amount"]
    if cd9 is None:
        cd9 = 0
    params_for_ga.update({"cd9": cd9})

    if (check_json_fields("Service", response.json()["data"][0]) is False) or \
            (check_json_fields("Sub_Service", response.json()["data"][0]) is False):
        return False
    cd5 = response.json()["data"][0]["Service"]
    params_for_ga.update({"cd5": cd5})
    cd6 = response.json()["data"][0]["Sub_Service"]
    params_for_ga.update({"cd6": cd6})

    if check_json_fields("Good_Inquiry", response.json()["data"][0]) is False:
        return False
    cd7 = response.json()["data"][0]["Good_Inquiry"]
    params_for_ga.update({"cd7": cd7})

    if check_json_fields("Deal_Size", response.json()["data"][0]) is False:
        return False
    cd8 = response.json()["data"][0]["Deal_Size"]
    params_for_ga.update({"cd8": cd8})

    if check_json_fields("ids", response.json()["data"][0]) is False:
        return False
    cd2 = response.json()["data"][0]["ids"]
    params_for_ga.update({"cd2": cd2})

    return True

def creat_ga_params(response, ids):
    """"Varification for stage and creat parameters for GA requst"""

    params_for_ga = {
        "v": "1",
        "t": "event",
        "ec": "zoho_stage_change",
        "ea": "stage_change",
        "ua": "Opera / 9.80",
        "dp": "ZohoCRM",
    }
    try:
        if check_json_fields("Stage", response.json()["data"][0]) is False:
            return params_for_ga, False
        current_stage = response.json()["data"][0]["Stage"]
        params_for_ga.update({"el": current_stage})
    except ValueError:
        LOGGER.error("Incorrect response JSON data")
        return params_for_ga, False

    LOGGER.info(
        "id=" +
        ids +
        ": current stage is " +
        current_stage)

    if ((check_json_fields("GA_client_id", response.json()["data"][0])) is False) or \
            (check_json_fields("GA_property_id", response.json()["data"][0]) is False):
        return params_for_ga, False
    current_google_id = response.json()["data"][0]["GA_client_id"]
    ga_property_id = response.json()["data"][0]["GA_property_id"]
    if(current_google_id is None) or (ga_property_id is None):
        return params_for_ga, False
    params_for_ga.update({"cid": current_google_id})
    params_for_ga.update({"tid": ga_property_id})

    if "Closed" in current_stage:
        if when_deal_in_closed_block(response, params_for_ga) is False:
            return params_for_ga, False

    if "Disqualified" in current_stage:
        if check_json_fields("Reason_to_Disqualify", response.json()["data"][0]) is False:
            return params_for_ga, False
        cd10 = response.json()["data"][0]["Reason_to_Disqualify"]
        params_for_ga.update({"cd10": cd10})
        ga_request(response, params_for_ga)
        params_for_ga.update({"ec": "crm_details_defined"})
        params_for_ga.update({"ea": "Reason for Disqualify defined"})
        params_for_ga.update({"el": cd10})

    return params_for_ga, True


@APP.route(_ZOHO_NOTIFICATIONS_ENDPOINT, methods=['POST'])
def respond():
    """generate post request to google analytics  """

    # creating _ACCESS_TOKEN and we check: how init this token
    global _ACCESS_TOKEN
    try:
        oauth_client = zoho_crm.ZohoOAuth.get_client_instance()
        _ACCESS_TOKEN = oauth_client.get_access_token(_ZOHO_LOGIN_EMAIL)
    except zoho_crm.OAuthUtility.ZohoOAuthException as ex:
        LOGGER.error("Unable to refresh access token", exc_info=ex)
        return Response(status=500)

    # getting deals records
    auth_header = {"Authorization": "Zoho-oauthtoken " + _ACCESS_TOKEN}
    if "module" not in request.json:
        return Response(status=500)
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
            print response.json()
            params_for_ga, log_flag = creat_ga_params(response, ids)
            if log_flag is False:
                return Response(status=500)
            data_stage = {response.json()["data"][0]["id"]: params_for_ga["el"]}
            if stage_changes(data_stage):
                ga_request(response, params_for_ga)
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
