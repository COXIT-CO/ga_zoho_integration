"""Python script which integrates Zoho CRM deals data with google analytics."""
import sys
import random
import argparse
import json
import requests


import zcrmsdk as zoho_crm
from flask import Flask, request, Response

_ZOHO_NOTIFICATIONS_ENDPOINT = "/zoho/deals/change"
_ZOHO_LOGIN_EMAIL, _ZOHO_GRANT_TOKEN, _ZOHO_API_URI, _ACCESS_TOKEN = "", "", "", ""


def create_parser():
    """Creat parameters passing from console"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--email')
    parser.add_argument('-gt', '--grant_token')
    parser.add_argument('-cid', '--client_id')
    parser.add_argument('-cs', '--client_secret')
    parser.add_argument('-api', '--api_uri', default='eu')

    return parser


def initialize_variebles():
    """TODO: make following data configurable on script startup (passed as
    arguments)"""

    # change global variebles
    global _ZOHO_LOGIN_EMAIL, _ZOHO_GRANT_TOKEN, _ZOHO_API_URI

    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    # Add parameters passing from console
    zoho_client_id = namespace.client_id
    zoho_client_secret = namespace.client_secret

    _ZOHO_LOGIN_EMAIL = namespace.email
    _ZOHO_GRANT_TOKEN = namespace.grant_token
    _ZOHO_API_URI = "https://www.zohoapis." + namespace.api_uri

    config = {
        "apiBaseUrl": _ZOHO_API_URI,
        "token_persistence_path": "D:/GIT_PROJECTs/ga_zoho_integration",
        "currentUserEmail": _ZOHO_LOGIN_EMAIL,
        "client_id": zoho_client_id,
        "client_secret": zoho_client_secret,
        "redirect_uri": "coxit.co",
        "accounts_url": "https://accounts.zoho.eu",
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
    google_analytics_api_uri = "https://www.google-analytics.com"
    google_analytics_collect_endpoint = "/collect"

    # get deals records
    auth_header = {"Authorization": "Zoho-oauthtoken " + _ACCESS_TOKEN}
    module = request.json["module"]
    for ids in request.json["ids"]:

        response = requests.get(
            url=_ZOHO_API_URI +
            "/crm/v2/" +
            module +
            "/" +
            ids,
            headers=auth_header)
        if response.status_code == 200:

            current_stage = response.json()["data"][0]["Stage"]
            print "id=" + ids + ": current stage is " + current_stage
            #current_google_id = response.json()["data"][0]["id"]
            cookie_id = "GA1.1." + str(random.randint(1000000000, 10000000000)) + \
                "." + str(random.randint(1000000000, 10000000000))
            print cookie_id

            params_for_ga = {
                "v": "1",
                "t": "event",
                "tid": "UA-179961291-2",
                "cid": cookie_id,  # "GA1.1.1467240959.1602069460",
                # "uid": current_google_id,
                "ec": "zoho_stage_change",
                "ea": "stage_change",
                "el": current_stage,
                "ua": "Opera / 9.80"
            }

# ?v=1&t=event&tid=UA-178036986-1&cid=93616860.1600348789&
# ec=zoho_stage_change&ea=stage_change&el=negotiation
            response = requests.post(
                url=google_analytics_api_uri +
                google_analytics_collect_endpoint,
                params=params_for_ga)
            if response.status_code == 200:
                print "Update succesfully send to Google Analytic"

    return Response(status=200)


def creat_requests():
    """creating request using web huk"""
    enable_notifications_endpoint = "/crm/v2/actions/watch"

    request_input_json = {
        "watch": [
            {
                "channel_id": "1000000068002",
                "events": ["Deals.edit"],
                "token": "TOKEN_FOR_VERIFICATION_OF_1000000068002",
                "notify_url": "http://6ba554ad50a5.ngrok.io" +
                              _ZOHO_NOTIFICATIONS_ENDPOINT,
            }]}

    # Enable Zoho Notifications
    header = {"Authorization": "Zoho-oauthtoken " + _ACCESS_TOKEN,
              'Content-type': 'application/json'}
    requests.post(
        url=_ZOHO_API_URI +
        enable_notifications_endpoint,
        headers=header,
        data=json.dumps(request_input_json))


if __name__ == '__main__':

    creat_init_access_token()

    creat_requests()

    APP.run(host="127.0.0.1", port=5000)
