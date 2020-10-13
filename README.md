# ga_zoho_integration
Python script which integrates Zoho CRM deals data with google analytics.

## Requirments

Python 2.7

Run `pip install -r requirements.txt` to install all required libraries.

#Zoho API Application set up

zcrmsdk - Python SDK acts as a wrapper for Zoho CRM APIs
Client app must have Python 2.7 for this library

For the first run, you will need to have a grant token specified (see Zoho API instructions about how to generate it).
Users have to generate ZOHO_GRANT_TOKEN use this Scope:
ZohoCRM.notifications.ALL, ZohoCRM.modules.ALL, AAAserver.profile.Read, ZohoCRM.settings.ALL, ZohoCRM.settings.variables.ALL

#Google Analytics set up
Dont forget change this field in variable PARAM
"tid": "your_Tracking ID"
The tracking ID  is a segment of the sample "UA-000000-2".
It must be included in the tracking code to tell Analytics to which account and resource to send data.

#Quick start template
python main.py -gt 1000.cfa0885cc71f4047173d67aaf1ab869f.03f9daf5cfb6fb94458bc3fd5128ddf4 -e bear.victor28@gmail.com -cid 1000.LQ49HO3IAPPHLBZCMOF16EMMR5VUQW -cs f0f4909fe0010021835db0fe48cbb1337eda2f472e -tid UA-179961291-2 -api eu -nu http://ec631955ef56.ngrok.io
