import logging

import argparser

LOG_CONFIG = dict(
    version=1,
    formatters={
        'f': {'format':
                  '[%(levelname)s] - Line: %(lineno)d '
                  '- %(name)s - : %(message)s.'}
    },
    handlers={
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.ERROR}
    },
    root={
        'handlers': ['h'],
        'level': logging.ERROR,
    },
)

PARSER = argparser.init_parser()
ARGS_P = PARSER.parse_args()
ZOHO_LOGIN_EMAIL = ARGS_P.email
ZOHO_GRANT_TOKEN = ARGS_P.grant_token
ZOHO_CLIENT_ID = ARGS_P.client_id
ZOHO_CLIENT_SECRET = ARGS_P.client_secret
ZOHO_ACCOUNT_DOMAIN = ARGS_P.domain

HOST = ARGS_P.host
PORT = ARGS_P.port

ZOHO_API_URL = "https://www.zohoapis." + ZOHO_ACCOUNT_DOMAIN
DEALS_ENDPOINT = "/crm/v2/Deals"
ENABLE_NOTIFICATIONS_ENDPOINT = "/crm/v2/actions/watch"
ZOHO_NOTIFICATIONS_ENDPOINT = "/zoho/deals/change"
GOOGLE_ANALYTICS_API_URL = "https://www.google-analytics.com"
GOOGLE_ANALYTICS_COLLECT_ENDPOINT = "/collect"

CONFIG_ZOHO = {
    "apiBaseUrl": ZOHO_API_URL,
    "token_persistence_path": "./",
    "currentUserEmail": ZOHO_LOGIN_EMAIL,
    "client_id": ZOHO_CLIENT_ID,
    "client_secret": ZOHO_CLIENT_SECRET,
    "redirect_uri": "https://coxit.co",
    "accounts_url": "https://accounts.zoho." + ZOHO_ACCOUNT_DOMAIN,
}
REQUEST_INPUT_JSON = {
    "watch": [
        {
            "channel_id": "1000000068002",
            "events": [
                "Deals.edit"
            ],
            "token": "TOKEN_FOR_VERIFICATION_OF_1000000068002",
            "notify_url": ARGS_P.notify_url + ZOHO_NOTIFICATIONS_ENDPOINT,
        }
    ]
}
