import json
import random
import requests

import zcrmsdk as zoho_crm
from flask import Flask, request, Response


# TODO: make following data configurable on script startup (passed as arguments)
ZOHO_LOGIN_EMAIL = "bear.victor28@gmail.com"
ZOHO_GRANT_TOKEN = "1000.ba356065855a909c02543700807d5065.312087b477ec73c1413741a1ad14ef03"
ZOHO_CLIENT_ID = "1000.IUOYW5741V7EA7IAV47NGSTUZKJRKU"
ZOHO_CLIENT_SECRET = "968c27e883b1c808b3674b7d1a0cb528b92af99cb6"

ZOHO_API_URI = "https://www.zohoapis.eu"

DEALS_ENDPOINT = "/crm/v2/Deals"
ENABLE_NOTIFICATIONS_ENDPOINT = "/crm/v2/actions/watch"
ZOHO_NOTIFICATIONS_ENDPOINT = "/zoho/deals/change"
GOOGLE_ANALYTICS_API_URI = "https://www.google-analytics.com"
GOOGLE_ANALYTICS_COLLECT_ENDPOINT = "/collect"

config = {
    "apiBaseUrl": ZOHO_API_URI,
    "token_persistence_path": "D:/GIT_PROJECTs/ga_zoho_integration",
    "currentUserEmail": ZOHO_LOGIN_EMAIL,
    "client_id": ZOHO_CLIENT_ID,
    "client_secret": ZOHO_CLIENT_SECRET,
    "redirect_uri": "coxit.co",
    "accounts_url": "https://accounts.zoho.eu",
}

request_input_json = {
    "watch": [
        {
            "channel_id": "1000000068002",
            "events": [
                "Deals.edit"
            ],
            "token": "TOKEN_FOR_VERIFICATION_OF_1000000068002",
            "notify_url": "http://f2d4701a51c9.ngrok.io" + ZOHO_NOTIFICATIONS_ENDPOINT,
        }
    ]
}

zoho_crm.ZCRMRestClient.initialize(config)
oauth_client = zoho_crm.ZohoOAuth.get_client_instance()

#first time start
#oauth_tokens = oauth_client.generate_access_token(ZOHO_GRANT_TOKEN)
#access_token = oauth_tokens.get_access_token()

#second time start
access_token = oauth_client.get_access_token(ZOHO_LOGIN_EMAIL)

app = Flask(__name__)


@app.route(ZOHO_NOTIFICATIONS_ENDPOINT, methods=['POST'])
def respond():
    print(request.json)

    # get deals records
    auth_header = {"Authorization": "Zoho-oauthtoken " + access_token}
    module = request.json["module"]
    for id in request.json["ids"]:
        id_str = id
        response = requests.get(url=ZOHO_API_URI + "/crm/v2/" + module + "/" + id_str, headers=auth_header)
        if response.status_code == 200:

            current_stage = response.json()["data"][0]["Stage"]
            print("id=" + id_str + ": current stage is " + current_stage)
            current_google_id = response.json()["data"][0]["id"]
            cookieId="GA1.1."+str(random.randint(1000000000,10000000000))+"."+str(random.randint(1000000000,10000000000))
            print(cookieId)


            # TODO:
            # Get record from DB and compare stages, if stage changed then make POST request to analytic

            PARAMS = {
                "v": "1",
                "t": "event",
                "tid": "UA-179961291-2",
                "cid": cookieId,#"GA1.1.1467240959.1602069460",
                #"uid": current_google_id,
                "ec": "zoho_stage_change",
                "ea": "stage_change",
                "el": current_stage,
                "ua": "Opera / 9.80"
            }

            
            # ?v=1&t=event&tid=UA-178036986-1&cid=93616860.1600348789&ec=zoho_stage_change&ea=stage_change&el=negotiation
            response = requests.post(url=GOOGLE_ANALYTICS_API_URI + GOOGLE_ANALYTICS_COLLECT_ENDPOINT, params=PARAMS)
            if response.status_code == 200:
                print ("Update succesfully send to Google Analytic")

    return Response(status=200)


if __name__ == '__main__':

    # Enable Zoho Notifications
    header = {"Authorization": "Zoho-oauthtoken " + access_token,
              'Content-type': 'application/json'}
    r = requests.post(url=ZOHO_API_URI + ENABLE_NOTIFICATIONS_ENDPOINT, headers=header,
                      data=json.dumps(request_input_json))

    app.run(host="127.0.0.1", port=5000)
