import json
from datetime import datetime, timedelta
from os import path

import pytz
import zcrmsdk as zoho_crm
import requests
from logging import getLogger

LOGGER = getLogger('app')

class ZohoAPI:
    def __init__(self, configs):
        args = configs.args
        self.client_id = args.client_id
        self.client_secret = args.client_secret
        self.login_email = args.email
        self.grant_token = args.grant_token
        self.api_uri = args.api_uri
        self.api_base_url = "https://www.zohoapis." + self.api_uri
        self.config = {
            "apiBaseUrl": self.api_base_url,
            "token_persistence_path": "./",
            "currentUserEmail": self.login_email,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": "coxit.co",
            "accounts_url": "https://accounts.zoho." + self.api_uri,
        }
        self.access_token = self.init_access_token()
        self.notify_url = configs.ngrok_url + configs.ZOHO_NOTIFICATIONS_ENDPOINT

    def init_access_token(self):
        """creating _ACCESS_TOKEN and we check: how init this token """
        zoho_crm.ZCRMRestClient.initialize(self.config)
        oauth_client = zoho_crm.ZohoOAuth.get_client_instance()
        if path.isfile('./zcrm_oauthtokens.pkl'):
            _access_token = oauth_client.get_access_token(self.login_email)
        else:
            oauth_tokens = oauth_client.generate_access_token(self.grant_token)
            _access_token = oauth_tokens.get_access_token()
        return _access_token

    def refresh_access_token(self):
        """refresh access token"""
        try:
            oauth_client = zoho_crm.ZohoOAuth.get_client_instance()
            self.access_token = oauth_client.get_access_token(self.login_email)
            LOGGER.info("Acccess token refreshed")
        except zoho_crm.OAuthUtility.ZohoOAuthException:
            LOGGER.error("Unable to refresh access token")
            return False
        return True

    def get_response(self, module, ids):
        """take data from zoho and sent them to GA"""
        auth_header = {"Authorization": "Zoho-oauthtoken " + self.access_token}
        try:
            response = requests.get(
                url=self.api_base_url +
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
            return None
        else:
            return response

    def enable_notifications(self):
        """Enable Zoho Notifications"""
        enable_notifications_endpoint = "/crm/v2/actions/watch"

        self.refresh_access_token()

        header = {"Authorization": "Zoho-oauthtoken " + self.access_token,
                  'Content-type': 'application/json'}

        resp = requests.post(
            url=self.api_base_url +
                enable_notifications_endpoint,
            headers=header,
            data=json.dumps(self.make_input_json()))

        if resp.status_code == 202:
            LOGGER.error("Failed to subscribe for notifications")
            LOGGER.error("status_code: %s", str(resp.status_code))
            LOGGER.error(resp.text)

        resp.raise_for_status()

    def make_input_json(self):
        """create json for zoho notification"""
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
                    "notify_url": self.notify_url,
                }]}
        return request_input_json
