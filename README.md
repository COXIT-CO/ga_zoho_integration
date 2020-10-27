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
python main.py -gt 1000.25b090fd24c8bf5f88ec8f30d3949615.e0e3964415098c16f300b5e79f1b4670 -e victor997212@gmail.com -cid 1000.WW9EIIGBU1G4RLE1LTTEOXL05PXA7Z -cs 97e01d73d4d2c79ec7f53d427c8bd6e1cc2c04f82c -tid UA-179961291-2 -api eu -pt 5000
