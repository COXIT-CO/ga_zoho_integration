import logging

logging_config = dict(
    version = 1,
    formatters = {
        'f': {'format':
              '[%(levelname)s] - Line: %(lineno)d - %(name)s - : %(message)s.'}
        },
    handlers = {
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.ERROR}
        },
    root = {
        'handlers': ['h'],
        'level': logging.ERROR,
        },
)

# config = {
#     "apiBaseUrl": ZOHO_API_URL,
#     "token_persistence_path": "/Users/yehorzhornovyi/PycharmProjects/ga_zoho_integration/env/",
#     "currentUserEmail": ZOHO_LOGIN_EMAIL,
#     "client_id": ZOHO_CLIENT_ID,
#     "client_secret": ZOHO_CLIENT_SECRET,
#     "redirect_uri": "https://coxit.co",
#     "accounts_url": "https://accounts.zoho."+ZOHO_ACCOUNT_DOMEN,
# }

# ZOHO_LOGIN_EMAIL = "yehorzhornovyi@gmail.com"
# ZOHO_GRANT_TOKEN = "1000.58ee4e53d9f5e522e2d842d66d4e08a9.62282898ecfb46fdc051f20db36bc8fe"
# ZOHO_CLIENT_ID = "1000.6UBJGFQ9ZBEU8R4OF9X35FZ4KROLJO"
# ZOHO_CLIENT_SECRET = "538947a51fc6138b864550f447e75d8c3ba2edd0c3"
# ZOHO_ACCOUNT_DOMEN = "eu"
#
# ZOHO_API_URL = "https://www.zohoapis." + ZOHO_ACCOUNT_DOMEN
# DEALS_ENDPOINT = "/crm/v2/Deals"
# ENABLE_NOTIFICATIONS_ENDPOINT = "/crm/v2/actions/watch"
# ZOHO_NOTIFICATIONS_ENDPOINT = "/zoho/deals/change"
# GOOGLE_ANALYTICS_API_URL = "https://www.google-analytics.com"
# GOOGLE_ANALYTICS_COLLECT_ENDPOINT = "/collect"

# params = {
#                 "v": "1",
#                 "t": "event",
#                 "tid": "UA-180087680-1",
#                 "uid": user.generate_unique_id(),
#                 "ec": "zoho_stage_change",
#                 "ea": "stage_change",
#                 "el": current_stage,
#                 "ua": "Opera / 9.80"
#             }

# host = "127.0.0.1"
# port = 5050