# pylint: disable=global-statement,import-error
""""In this module, we write all imports and global variables"""
import argparse
from datetime import datetime, timedelta
import time
import threading
import json
import sys
from os import path

import logging
from logging.config import dictConfig
import pytz

import requests
import zcrmsdk as zoho_crm
from flask import Flask, request, Response
from pyngrok import ngrok

from config import LOG_CONFIG

ZOHO_NOTIFICATIONS_ENDPOINT = "/zoho/deals/change"
ZOHO_LOGIN_EMAIL, ZOHO_GRANT_TOKEN, ZOHO_API_URI, ACCESS_TOKEN, \
    NGROK_TOKEN, PORT = "", "", "", "", "", ""
LOGGER = logging.getLogger()


def create_parser():
    """Creat parameters passing from console"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--email')
    parser.add_argument('-gt', '--grant_token')
    parser.add_argument('-cid', '--client_id')
    parser.add_argument('-cs', '--client_secret')
    parser.add_argument('-api', '--api_uri', default='com')
    parser.add_argument('-ngrok', '--ngrok_token')
    parser.add_argument('-port', '--port', default='80')
    parser.add_argument('-log', '--logging', default='file')

    return parser


def initialize_variables():
    """TODO: make following data configurable on script startup (passed as
    arguments)"""

    # change global variebles
    global ZOHO_LOGIN_EMAIL, ZOHO_GRANT_TOKEN, ZOHO_API_URI, NGROK_TOKEN, \
        PORT, LOGGER, LOG_CONFIG

    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    # Add parameters passing from console
    zoho_client_id = namespace.client_id
    zoho_client_secret = namespace.client_secret

    ZOHO_LOGIN_EMAIL = namespace.email
    ZOHO_GRANT_TOKEN = namespace.grant_token
    ZOHO_API_URI = "https://www.zohoapis." + namespace.api_uri
    NGROK_TOKEN = namespace.ngrok_token
    PORT = namespace.port

    LOG_CONFIG['root']['handlers'].append(namespace.logging)
    flask_log = logging.getLogger('werkzeug')
    flask_log.setLevel(logging.ERROR)
    dictConfig(LOG_CONFIG)
    LOGGER = logging.getLogger()

    config = {
        "apiBaseUrl": ZOHO_API_URI,
        "token_persistence_path": "./",
        "currentUserEmail": ZOHO_LOGIN_EMAIL,
        "client_id": zoho_client_id,
        "client_secret": zoho_client_secret,
        "redirect_uri": "coxit.co",
        "accounts_url": "https://accounts.zoho." + namespace.api_uri,
    }

    return config


def creat_init_access_token():
    """creating _ACCESS_TOKEN and we check: how init this token """
    global ACCESS_TOKEN
    current_dir = path.dirname(__file__)
    file_path = path.join(current_dir, 'zcrm_oauthtokens.pkl')

    zoho_crm.ZCRMRestClient.initialize(initialize_variables())
    oauth_client = zoho_crm.ZohoOAuth.get_client_instance()
    if path.isfile(file_path):
        ACCESS_TOKEN = oauth_client.get_access_token(ZOHO_LOGIN_EMAIL)
    else:
        oauth_tokens = oauth_client.generate_access_token(ZOHO_GRANT_TOKEN)
        ACCESS_TOKEN = oauth_tokens.get_access_token()


def refresh_access_token():
    """refresh access token"""
    global ACCESS_TOKEN
    try:
        oauth_client = zoho_crm.ZohoOAuth.get_client_instance()
        ACCESS_TOKEN = oauth_client.get_access_token(ZOHO_LOGIN_EMAIL)
    except zoho_crm.OAuthUtility.ZohoOAuthException as ex:
        LOGGER.error("Unable to refresh access token", exc_info=ex)
        return False
    return True



def compare_change_in_data(old_data, new_data):
    """compare old stages and new stage. Return false if stage isn`t change"""
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


def when_deal_in_closed_block(response, params_for_ga, ids):
    """"make exclusive ga params change when deals in block CLOSED"""
    fields_names = {
        "Service",
        "Sub_Service",
        "Good_Inquiry",
        "Deal_Size"}
    for field in fields_names:
        if check_json_fields(field, response.json()["data"][0]) is False:
            return False

    data_from_field = response.json()["data"][0]["Amount"]
    if data_from_field is None:
        data_from_field = 0
    params_for_ga.update({"cd9": (data_from_field)})
    params_for_ga.update({"ev": int(round(data_from_field))})

    data_from_field = response.json()["data"][0]["Service"]
    params_for_ga.update({"cd5": data_from_field})
    data_from_field = response.json()["data"][0]["Sub_Service"]
    params_for_ga.update({"cd6": data_from_field})
    data_from_field = response.json()["data"][0]["Good_Inquiry"]
    params_for_ga.update({"cd7": data_from_field})

    data_from_field = response.json()["data"][0]["Deal_Size"]
    params_for_ga.update({"cd8": data_from_field})

    params_for_ga.update({"cd2": ids})

    return True


def check_main_fields(response):
    """Do varification.Are main field in json"""
    try:
        fields_names = {"GA_client_id", "GA_property_id", "Stage",}
        for field in fields_names:
            if check_json_fields(field, response.json()["data"][0]) is False:
                return False
    except ValueError:
        LOGGER.error("Incorrect response JSON data")
        return False

    return True


def varification_ga_request(response, params_for_ga, current_stage, ids):
    """"make varification if stage is change block"""
    data_stage = {ids: current_stage}
    if "Expected_revenue_change" in params_for_ga["ec"]:
        data_stage = {ids + "e": current_stage}
    if stage_changes(data_stage):
        ga_request(response, params_for_ga)
    else:
        LOGGER.info("Stage was not changed. Event was not sent")
        return False
    return True


def special_condition(response, current_stage, params_for_ga, ids):
    """"Special move when some deal in specific block """
    if "Closed" in current_stage:
        if when_deal_in_closed_block(response, params_for_ga, ids) is False:
            return False

    if "Disqualified" in current_stage:
        if check_json_fields("Reason_to_Disqualify", response.json()["data"][0]) is False:
            return False
        cd10 = response.json()["data"][0]["Reason_to_Disqualify"]
        if varification_ga_request(response, params_for_ga, current_stage, ids) is False:
            return False
        params_for_ga.update({"cd10": cd10})
        params_for_ga.update({"ec": "crm_details_defined"})
        params_for_ga.update({"ea": "Reason for Disqualify defined"})
        params_for_ga.update({"el": cd10})
        ga_request(response, params_for_ga)

    return True


def first_response_to_ga(response, params_for_ga, current_stage, ids):
    """do another response to ga"""
    if varification_ga_request(response, params_for_ga, current_stage, ids) is False:
        return False
    expected_revenue = response.json()["data"][0]["Expected_Revenue"]
    params_for_ga.update({"ec": "Expected_revenue_change"})
    params_for_ga.update({"ev": expected_revenue})
    params_for_ga.update({"el": "Exp_revenue " + current_stage})

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
    if check_main_fields(response) is False:
        return False

    current_stage = response.json()["data"][0]["Stage"]
    params_for_ga.update({"el": current_stage})

    LOGGER.info(
        "id=" +
        ids +
        ": current stage is " +
        current_stage)

    current_google_id = response.json()["data"][0]["GA_client_id"]
    ga_property_id = response.json()["data"][0]["GA_property_id"]
    if(current_google_id is None) or (ga_property_id is None):
        return False
    params_for_ga.update({"cid": current_google_id})
    params_for_ga.update({"tid": ga_property_id})

    if (check_json_fields("Amount", response.json()["data"][0]) is False) or \
            (check_json_fields("Expected_Revenue", response.json()["data"][0]) is False):
        return False

    cd9 = response.json()["data"][0]["Amount"]
    if cd9 is None:
        cd9 = 0
    params_for_ga.update({"ev": int(round(cd9))})

    if sent_request_to_ga(response, params_for_ga, current_stage, ids) is False:
        return False

    return True


def sent_request_to_ga(response, params_for_ga, current_stage, ids):
    """"we watch to special condition for send ga requst  """
    if first_response_to_ga(response, params_for_ga, current_stage, ids) is False:
        return False

    if special_condition(response, current_stage, params_for_ga, ids) is False:
        return False

    if varification_ga_request(response, params_for_ga, current_stage, ids) is False:
        return False

    return True


def zoho_ga_requests(module, ids):
    """take dat from zoho and sent them to GA"""
    auth_header = {"Authorization": "Zoho-oauthtoken " + ACCESS_TOKEN}
    try:
        response = requests.get(
            url=ZOHO_API_URI +
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
        return False
    else:
        good_response_flag = creat_ga_params(response, ids)
        if good_response_flag is False:
            return False

    return True



def ngrok_settings():
    """configure ngrok settings"""
    ngrok.set_auth_token(NGROK_TOKEN)
    return str(ngrok.connect(port=PORT))


def make_input_json():
    """create json for zoho notification"""
    notify_url = ngrok_settings() + ZOHO_NOTIFICATIONS_ENDPOINT

    notifications_expiration_time = datetime.utcnow().replace(microsecond=0) + \
        timedelta(days=1)
    expiration_time_iso_format = notifications_expiration_time.replace(
        tzinfo=pytz.utc).isoformat()
    LOGGER.warning(
        "Notifications channel will expire at %s",
        expiration_time_iso_format)

    request_input_json = {
        "watch": [
            {
                "channel_id": "1000000068002",
                "channel_expiry": expiration_time_iso_format,
                "events": ["Deals.edit"],
                "token": "TOKEN_FOR_VERIFICATION_OF_1000000068002",
                "notify_url": notify_url,
            }]}
    return request_input_json

def enable_notifications():
    """Enable Zoho Notifications"""
    enable_notifications_endpoint = "/crm/v2/actions/watch"

    refresh_access_token()

    header = {"Authorization": "Zoho-oauthtoken " + ACCESS_TOKEN,
              'Content-type': 'application/json'}

    resp = requests.post(
        url=ZOHO_API_URI +
        enable_notifications_endpoint,
        headers=header,
        data=json.dumps(make_input_json()))

    if resp.status_code == 202:
        LOGGER.error("Failed to subscribe for notifications")
        LOGGER.error("status_code: %s", str(resp.status_code))
        LOGGER.error(resp.text)

    resp.raise_for_status()


def treade_notification_deamon(sec=0, minutes=0, hours=0):
    """This func refresh another func , which create response to notification"""
    while True:
        sleep_time = sec + (minutes * 60) + (hours * 3600)
        time.sleep(sleep_time)
        enable_notifications()
        print "Refresh enable notification"


def create_tread():
    """Create deamon thred for endless notofication from zoho"""
    enable_notification_thread = threading.Thread(
        target=treade_notification_deamon, kwargs=({"hours": 23}))
    enable_notification_thread.daemon = True
    enable_notification_thread.start()


APP = Flask(__name__)


@APP.route(ZOHO_NOTIFICATIONS_ENDPOINT, methods=['POST'])
def respond():
    """generate post request to google analytics  """

    if refresh_access_token() is False:
        return Response(status=500)
    # getting deals records

    if "module" not in request.json:
        return Response(status=500)

    module = request.json["module"]
    ids = request.json["ids"][0]

    if zoho_ga_requests(module, ids) is False:
        Response(status=500)
    return Response(status=200)


if __name__ == '__main__':
    try:
        creat_init_access_token()
    except zoho_crm.OAuthUtility.ZohoOAuthException as ex:
        LOGGER.error(ex)
        sys.exit("Passed data in parameters is invalid. Script is terminated")
    try:
        create_tread()
        enable_notifications()
    except requests.RequestException as ex:
        LOGGER.error(
            "ZohoCRM does not response. Check selected scopes generating grant_token",
            exc_info=ex)
    else:
        APP.run(host="0.0.0.0", port=PORT)
