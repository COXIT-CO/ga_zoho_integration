import json
import zcrmsdk as zoho_crm
import requests
from flask import Flask, request, Response
from pyga.entities import Visitor
import logging
from os import path

logger = logging.getLogger()
log_console_format = "[%(levelname)s] - Line: %(lineno)d - %(name)s - : %(message)s."
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(logging.Formatter(log_console_format))
logger.addHandler(console_handler)

# TODO: make following data configurable on script startup (passed as arguments)
ZOHO_LOGIN_EMAIL = "yehorzhornovyi@gmail.com"
ZOHO_GRANT_TOKEN = "1000.58ee4e53d9f5e522e2d842d66d4e08a9.62282898ecfb46fdc051f20db36bc8fe"
ZOHO_CLIENT_ID = "1000.6UBJGFQ9ZBEU8R4OF9X35FZ4KROLJO"
ZOHO_CLIENT_SECRET = "538947a51fc6138b864550f447e75d8c3ba2edd0c3"
ZOHO_ACCOUNT_DOMEN = "eu"

ZOHO_API_URL = "https://www.zohoapis." + ZOHO_ACCOUNT_DOMEN
DEALS_ENDPOINT = "/crm/v2/Deals"
ENABLE_NOTIFICATIONS_ENDPOINT = "/crm/v2/actions/watch"
ZOHO_NOTIFICATIONS_ENDPOINT = "/zoho/deals/change"
GOOGLE_ANALYTICS_API_URL = "https://www.google-analytics.com"
GOOGLE_ANALYTICS_COLLECT_ENDPOINT = "/collect"

config = {
    "apiBaseUrl": ZOHO_API_URL,
    "token_persistence_path": "/Users/yehorzhornovyi/PycharmProjects/ga_zoho_integration/env/",
    "currentUserEmail": ZOHO_LOGIN_EMAIL,
    "client_id": ZOHO_CLIENT_ID,
    "client_secret": ZOHO_CLIENT_SECRET,
    "redirect_uri": "https://coxit.co",
    "accounts_url": "https://accounts.zoho."+ZOHO_ACCOUNT_DOMEN,
}
request_input_json = {
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
app = Flask(__name__)

def get_access_token():
    access_token = None
    if path.isfile(config['token_persistence_path'] + 'zcrm_oauthtokens.pkl'):
        try:
            access_token = oauth_client.get_access_token(ZOHO_LOGIN_EMAIL)
        except Exception as e:
            logger.error(e)
    else:
        try:
            oauth_tokens = oauth_client.generate_access_token(ZOHO_GRANT_TOKEN)
            access_token = oauth_tokens.get_access_token()
        except Exception as ex :
            logger.error(ex)
    return access_token

@app.route(ZOHO_NOTIFICATIONS_ENDPOINT, methods=['POST'])
def respond():
    # get deals records
    auth_header = {"Authorization": "Zoho-oauthtoken " + access_token}
    module = request.json["module"]
    for i in request.json["ids"]:
        id_str = i

        resp = requests.get(url=ZOHO_API_URL + "/crm/v2/" + module + "/" + id_str,
                                headers=auth_header)
        if resp.status_code == 200:
            current_stage = resp.json()["data"][0]["Stage"]
            print("id=" + id_str + ": current stage is " + current_stage)

            # TODO:Get record from DB and compare stages,
            #  if stage changed then make POST request to analytic
            user = Visitor()
            params = {
                "v": "1",
                "t": "event",
                "tid": "UA-180087680-1",
                "uid": user.generate_unique_id(),
                "ec": "zoho_stage_change",
                "ea": "stage_change",
                "el": current_stage,
                "ua": "Opera / 9.80"
            }

            resp = requests.post(url=GOOGLE_ANALYTICS_API_URL+GOOGLE_ANALYTICS_COLLECT_ENDPOINT,
                                     params=params)
            if resp.status_code == 200:
                print ("Update succesfully send to Google Analytic")
        else:
            logger.error("The application can not get access to Zoho. Check the access token")

    return Response(status=200)

if __name__ == '__main__':

    zoho_crm.ZCRMRestClient.initialize(config)
    oauth_client = zoho_crm.ZohoOAuth.get_client_instance()
    # Enable Zoho Notifications
    access_token = get_access_token()

    if access_token:
        header = {"Authorization": "Zoho-oauthtoken " + access_token,
                  'Content-type': 'application/json'}
        resp = requests.post(url=ZOHO_API_URL + ENABLE_NOTIFICATIONS_ENDPOINT, headers=header,
                          data=json.dumps(request_input_json))
        if not resp:
            logger.error("Most likely you defined the wrong scopes generating the grant token! Enable Zoho Notifications API.")
        else:
            app.run(host="127.0.0.1", port=5050)
