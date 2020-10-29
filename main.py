"""Python script which integrates Zoho CRM deals data with google analytics."""
import sys
import argparse
import json
import requests


import zcrmsdk as zoho_crm
from flask import Flask, request, Response

_ZOHO_NOTIFICATIONS_ENDPOINT = "/zoho/deals/change"
_ZOHO_LOGIN_EMAIL, _ZOHO_GRANT_TOKEN, _ZOHO_API_URI, _ACCESS_TOKEN, \
_ZOHO_NOTIFY_URL, _GA_TID, _PORT = "", "", "", "", "", "", ""


def compare_change_in_data(old_data, new_data):
    """compare old stages and new stage. Return false if stage isnt change"""
    flag = False
    print "\n Old stage: ", old_data.keys(), "\n", old_data.values()
    print "\n New stage: ", new_data.keys(), new_data.values()

    for key, value in old_data.items():
        if new_data.keys()[0] == key:
            if new_data.values()[0] != value:
                flag = True
                break
            else:
                flag = False
                break
        else:
            #print "Add to json file return true"
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
    ip = "http://" + requests.get('http://ipinfo.io/json').json()['ip']
    parser.add_argument('-nu', '--notify_url', default=ip)
    parser.add_argument('-tid', '--ga_tid')
    parser.add_argument('-port', '--port', default='80')

    return parser


def initialize_variebles():
    """TODO: make following data configurable on script startup (passed as
    arguments)"""

    # change global variebles
    global _ZOHO_LOGIN_EMAIL, _ZOHO_GRANT_TOKEN, _ZOHO_API_URI, _ZOHO_NOTIFY_URL, _GA_TID, _PORT

    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    # Add parameters passing from console
    zoho_client_id = namespace.client_id
    zoho_client_secret = namespace.client_secret

    _ZOHO_LOGIN_EMAIL = namespace.email
    _ZOHO_GRANT_TOKEN = namespace.grant_token
    _ZOHO_API_URI = "https://www.zohoapis." + namespace.api_uri
    _ZOHO_NOTIFY_URL = namespace.notify_url
    _GA_TID = namespace.ga_tid
    _PORT = namespace.port

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
    try:
        _ACCESS_TOKEN = oauth_client.get_access_token(_ZOHO_LOGIN_EMAIL)
    except BaseException:
        oauth_tokens = oauth_client.generate_access_token(_ZOHO_GRANT_TOKEN)
        _ACCESS_TOKEN = oauth_tokens.get_access_token()


APP = Flask(__name__)


@APP.route(_ZOHO_NOTIFICATIONS_ENDPOINT, methods=['POST'])
def respond():
    """generate post request to google analytics  """

    # creating _ACCESS_TOKEN and we check: how init this token
    global _ACCESS_TOKEN
    oauth_client = zoho_crm.ZohoOAuth.get_client_instance()
    _ACCESS_TOKEN = oauth_client.get_access_token(_ZOHO_LOGIN_EMAIL)

    google_analytics_api_uri = "https://www.google-analytics.com"
    google_analytics_collect_endpoint = "/collect"

    # get deals records
    auth_header = {"Authorization": "Zoho-oauthtoken " + _ACCESS_TOKEN}
    module = request.json["module"]
    print "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW"
    for ids in request.json["ids"]:
        try:
            ga_response = requests.get(
                url=_ZOHO_API_URI +
                "/crm/v2/" +
                "settings/variables",
                headers=auth_header)
        except BaseException:
            print "Create variable 'GA_client_id' in ZOHO CRM"
            break

        response = requests.get(
            url=_ZOHO_API_URI +
            "/crm/v2/" +
            module +
            "/" +
            ids,
            headers=auth_header)
        if response.status_code == 200:

            current_stage = response.json()["data"][0]["Stage"]
            print("\n id=" + ids + ": current stage is " + current_stage)
            if ga_response.json()[
                    "variables"][0]["api_name"] == "GA_client_id":
                print "\n GA_client_id is finding"
                current_google_id = ga_response.json()["variables"][0]["value"]
            else:
                print "\n GA_client_id is not finding"

            params_for_ga = {
                "v": "1",
                "t": "event",
                "tid": _GA_TID,
                "cid": current_google_id,
                "ec": "zoho_stage_change",
                "ea": "stage_change",
                "el": current_stage,
                "ua": "Opera / 9.80"
            }
            data_stage = {response.json()["data"][0]["id"]: current_stage}
            if db_save_stage_info(data_stage):
                response = requests.post(
                    url=google_analytics_api_uri +
                    google_analytics_collect_endpoint,
                    params=params_for_ga)
                if response.status_code == 200:
                    print 50 * "*", "\n Update succesfully send to Google Analytic"
        else:
            print ("response.status_code = " +
                   str(response.status_code) + " - " + response.text)

    return Response(status=200)


def creat_requests():
    """creating request using webhook"""
    enable_notifications_endpoint = "/crm/v2/actions/watch"
    notify_url = _ZOHO_NOTIFY_URL + _ZOHO_NOTIFICATIONS_ENDPOINT
    print ("notify_url: " + notify_url)
    print ("_ZOHO_NOTIFY_URL: " + notify_url)
    print ("_ZOHO_NOTIFICATIONS_ENDPOINT: " + _ZOHO_NOTIFICATIONS_ENDPOINT)

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
    print ("Zoho-oauthtoken " + _ACCESS_TOKEN + "\n")
    requests.post(
        url=_ZOHO_API_URI +
        enable_notifications_endpoint,
        headers=header,
        data=json.dumps(request_input_json))


if __name__ == '__main__':

    creat_init_access_token()

    creat_requests()

    APP.run(host="0.0.0.0", port=_PORT)
