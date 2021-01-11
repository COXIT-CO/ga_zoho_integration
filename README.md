[![Build Status](https://www.travis-ci.com/COXIT-CO/ga_zoho_integration.svg?branch=issue_65)](https://www.travis-ci.com/COXIT-CO/ga_zoho_integration)
[![Coverage Status](https://coveralls.io/repos/github/COXIT-CO/ga_zoho_integration/badge.svg?branch=issue_65)](https://coveralls.io/github/COXIT-CO/ga_zoho_integration?branch=issue_65)

# ga_zoho_integration
Python script which integrates Zoho CRM Deals data with Google Analytics
sending event hits to Google Analytics property.

## Requirements

Python 2.7

Run `pip install -r requirements.txt` to install all required libraries.

## Zoho CRM set up
Zoho CRM Deals should contain `GA_client_id` field which should be populated by Google Analytics Client Id value.

## Google Analytics set up

Set up goals in GA for every deal stage. Goal type: `Event`. Goal IDs has to be in the same order as the CRM pipeline.

# Zoho API Application set up

zcrmsdk - Python SDK acts as a wrapper for Zoho CRM APIs
Client app must have Python 2.7 for this library

Users have to generate `ZOHO_GRANT_TOKEN`, so use this Scope:
'ZohoCRM.notifications.ALL, ZohoCRM.modules.ALL, AAAserver.profile.Read, ZohoCRM.settings.ALL'

For more detailed instruction read Zoho CRM API Documentation: https://www.zoho.com/crm/developer/docs/api/v2/.

# First start

To start the script you should have Linux server with Python 2.7 and Pip installed to be able to install
required libraries from `requirements.txt`. Also you will need public IP to be able to receive notifications
from Zoho CRM

When you clone this repo and want to start programme:
First of all u have to run 'setup.py' file with parameters:

`-gt`: grant token, how to generate it follow instruction for Self Client option here
 https://www.zoho.com/crm/developer/docs/api/v2/auth-request.html

`-e`: email of CRM user

`-cid`: client ID received from CRM app

`-cs`: client secret received from CRM app

`-api`: domain-specific Zoho Accounts URL ending. For example it may be `eu`, `in` or other as specified
 here https://www.zoho.com/crm/developer/docs/api/v2/access-refresh.html. `.com` is default option, no need to specify.

`-port`: port for Zoho CRM notifications Webhook server. By default it's 80.
To use not 80 port you will need to do additional proxy server set up.

`-logmode`: mode of logging handling. To enable logging to console pass 'console'. By default it's 'file'

`-logpath`: path of storing logs. By default it's script path + 'logs' directory.

`-ngrok`: your ngrok token from https://dashboard.ngrok.com/login

`-debug`: parameter without value. Enable to show debug level logs.



After ending, in `ga_zoho_integration` folder created `Settings.ini` file with all your data. So next time u have not to input all of them


# Run The Script

Just run `main.py` file.
