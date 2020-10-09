# ga_zoho_integration
Python script which integrates Zoho CRM deals data with google analytics.

## Requirments

Python 2.7

Run `pip install -r requirements.txt` to install all required libraries.

#Zoho API Application set up

zcrmsdk - Python SDK acts as a wrapper for Zoho CRM APIs
Client app must have Python 2.7 for this library

Users have to generate ZOHO_GRANT_TOKEN, so use this Scope:
ZohoCRM.notifications.ALL, ZohoCRM.notifications.WRITE, ZohoCRM.modules.ALL, AAAserver.profile.Read

#Google Analytics set up
Dont forget change this field in variable PARAM
"tid": "your_Tracking ID"
The tracking ID  is a segment of the sample "UA-000000-2".
It must be included in the tracking code to tell Analytics to which account and resource to send data.
