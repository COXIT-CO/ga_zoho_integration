# ga_zoho_integration
Python script which integrates Zoho CRM Deals data with Google Analytics 
sending event hits to Google Analytics property. 

## Requirments

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
`ZohoCRM.notifications.ALL, ZohoCRM.notifications.WRITE, ZohoCRM.modules.ALL, AAAserver.profile.Read`

For more detailed instruction read Zoho CRM API Documentation: https://www.zoho.com/crm/developer/docs/api/v2/.

# Run The Script

To start the script you should have Linux server with Python 2.7 and Pip installed to be able to install 
required libraries from `requirments.txt`. Also you will need public IP to be able to receive notifications 
from Zoho CRM
 
 Copy this command to console replacing parameters with your account data:
 
`python2.7 main.py -gt 1000.ba356065855a909c02543700807d5065.312087b477ec73c1413741a1ad14ef03 
-e email_of_crm_user@email.com -cid 1000.IUOYW5741V7EA7IAV47NGSTUZKJRKU -cs 968c27e883b1c808b3674b7d1a0cb528b92af99cb6 
-api com -tid UA-420308-22`

`-gt`: grant token, is required only for the very first run of the script for CRM

`-e`: email of CRM user

`-cid`: client ID received from CRM app 

`-cs`: client secret received from CRM app 

`-tid`: your GA Tracking ID. The tracking ID  is a segment of the sample "UA-000000-2".
It must be included in the tracking code to tell Analytics to which account and resource to send data.

`-api`: domain-specific Zoho Accounts URL ending. For example it may be `eu`, `in` or other as specified
 here https://www.zoho.com/crm/developer/docs/api/v2/access-refresh.html. `.com` is default option, no need to specify.

`-port`: port for Zoho CRM notifications Webhook server. By default it's 80. 
To use not 80 port you will need to do additional proxy server set up.

`-log`: mode of logging handling. To enable logging to console pass 'console'. By default it's 'file' 

For the very first time you will need to specify grant token `-ga`. How to generate it
follow instruction for Self Client option here https://www.zoho.com/crm/developer/docs/api/v2/auth-request.html.
