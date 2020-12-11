"""Module to define GaApi class"""
import json
from logging import getLogger
import requests
from flask import Response


LOGGER = getLogger('app')


class GaAPI:
    """Contains methods to process and send Zoho response to GA"""
    def __init__(self):
        self.response = None
        self.params = {
            "v": "1",
            "t": "event",
            "ec": "zoho_stage_change",
            "ea": "stage_change",
            "ua": "Opera / 9.80",
            "dp": "ZohoCRM",
        }

    @staticmethod
    def post_request(response, params):
        """"make request to google analytics"""
        google_analytics_api_uri = "https://www.google-analytics.com"
        google_analytics_collect_endpoint = "/collect"
        try:
            LOGGER.debug("Parameters for GA:\n" + json.dumps(params, indent=2))
            response = requests.post(
                url=google_analytics_api_uri +
                google_analytics_collect_endpoint,
                params=params)
            response.raise_for_status()
        except requests.RequestException as ex:
            LOGGER.error(
                "Unable to send post request to Google Analytics" +
                "response.status_code = " +
                str(
                    response.status_code) +
                " - " +
                response.text,
                exc_info=ex)
            return Response(status=401)
        else:
            LOGGER.info(
                "Update successfully sent to Google Analytic")
            return Response(status=200)

    def send_requests(self, response, ids):
        """"we watch to special condition for send ga request  """
        current_stage = response.json()["data"][0]["Stage"]
        if self.verify_response(response):
            params = self.update_params(response, ids)
            # first response to ga
            if self.verify_stage(current_stage, ids):
                self.post_request(response, params)
                params = self.update_params_first_request(response, params, ids)
            else:
                return Response(status=500)
            # special conditions
            if "Closed" in current_stage:
                if self.when_deal_in_closed_block(response):
                    params = self.update_params_closed_deal(response, params, ids)

            if "Disqualified" in current_stage:
                if self.has_field("Reason_to_Disqualify", response.json()["data"][0]):
                    if self.verify_stage(current_stage, ids):
                        self.post_request(response, params)
                        params = self.update_params_disqualified_stage(response, params)
                        self.post_request(response, params)
                    else:
                        return Response(status=500)

            if self.verify_stage(current_stage, ids):
                self.post_request(response, params)
            else:
                return Response(status=500)
        else:
            return Response(status=500)
        return Response(status=200)

    @staticmethod
    def update_params_disqualified_stage(response, params):
        """Updates params for request disqualified_stage"""
        cd10 = response.json()["data"][0]["Reason_to_Disqualify"]
        params.update({"cd10": cd10})
        params.update({"ec": "crm_details_defined"})
        params.update({"ea": "Reason for Disqualify defined"})
        params.update({"el": cd10})
        return params

    @staticmethod
    def update_params_closed_deal(response, params, ids):
        """Updates params for request close stage"""
        data_from_field = response.json()["data"][0]["Amount"]
        if data_from_field is None:
            data_from_field = 0
        params.update({"cd9": (data_from_field)})
        params.update({"ev": int(round(data_from_field))})
        data_from_field = response.json()["data"][0]["Service"]
        params.update({"cd5": data_from_field})
        data_from_field = response.json()["data"][0]["Sub_Service"]
        params.update({"cd6": data_from_field})
        data_from_field = response.json()["data"][0]["Good_Inquiry"]
        params.update({"cd7": data_from_field})
        data_from_field = response.json()["data"][0]["Deal_Size"]
        params.update({"cd8": data_from_field})
        params.update({"cd2": ids})
        return params

    @staticmethod
    def update_params_first_request(response, params, current_stage):
        """Updates params on disqualified_stage"""
        expected_revenue = response.json()["data"][0]["Expected_Revenue"]
        if expected_revenue is None:
            expected_revenue = 0
        params.update({"ec": "Expected_revenue_change",
                       "ev": int(round(expected_revenue)),
                       "el": "Exp_revenue " + current_stage})
        return params

    def verify_response(self, response):
        """verifies json of response"""
        if not self.check_main_fields(response):
            return False
        current_google_id = response.json()["data"][0]["GA_client_id"]
        ga_property_id = response.json()["data"][0]["GA_property_id"]
        if (current_google_id is None) or (ga_property_id is None):
            return False
        if not self.has_field("Amount", response.json()["data"][0]) or \
                not self.has_field("Expected_Revenue", response.json()["data"][0]):
            return False
        return True

    def update_params(self, response, ids):
        """"Updates parameters for GA request"""
        _params = self.params
        current_stage = response.json()["data"][0]["Stage"]
        _params.update({"el": current_stage})

        LOGGER.info(
            "id=" +
            ids +
            ": current stage is " +
            current_stage)

        current_google_id = response.json()["data"][0]["GA_client_id"]
        ga_property_id = response.json()["data"][0]["GA_property_id"]
        _params.update({"cid": current_google_id})
        _params.update({"tid": ga_property_id})

        cd9 = response.json()["data"][0]["Amount"]
        if cd9 is None:
            cd9 = 0
        _params.update({"ev": int(round(cd9))})
        return _params

    def verify_stage(self, current_stage, ids):
        """"make verification if stage is change block"""
        data_stage = {ids: current_stage}
        if "Expected_revenue_change" in self.params["ec"]:
            data_stage = {ids + "e": current_stage}
        if self.save_changed_stage(data_stage):
            return True
        LOGGER.info("Stage was not changed. Event was not sent")
        return False

    def when_deal_in_closed_block(self, response):
        """"make exclusive ga params change when deals in block CLOSED"""
        fields_names = {
            "Service",
            "Sub_Service",
            "Good_Inquiry",
            "Deal_Size"}

        for field in fields_names:
            if not self.has_field(field, response.json()["data"][0]):
                return False
        return True

    def check_main_fields(self, response):
        """Do verification. Are main field in json"""
        try:
            fields_names = {"GA_client_id", "GA_property_id", "Stage"}
            for field in fields_names:
                if self.has_field(field, response.json()["data"][0]) is False:
                    return False
        except ValueError:
            LOGGER.error("Incorrect response JSON data")
            return False

        return True

    @staticmethod
    def has_field(name_field, data_json):
        """"write logs if bad fields"""
        if name_field in data_json:
            if data_json[name_field]:
                LOGGER.debug("%s is found!", name_field)
                return True
            LOGGER.warning(
                "%s is empty. Make sure you fill in it in CRM.", name_field)
            return False
        else:
            LOGGER.warning(
                "%s is not found. Make sure you populate it in CRM.", name_field)
            return False

    @staticmethod
    def save_changed_stage(new_data):
        """Save and compare data about stage in json file"""
        flag = True
        try:
            with open("data_file.json", "r") as read_file:
                old_data = json.load(read_file)

            if GaAPI.compare_stages(old_data, new_data):
                old_data.update(new_data)
            else:
                flag = False

            with open("data_file.json", "w") as write_file:
                json.dump(old_data, write_file)

        except IOError:
            with open("data_file.json", "w") as write_file:
                json.dump(new_data, write_file)

        return flag

    @staticmethod
    def compare_stages(old_data, new_data):
        """compare old stages and new stage. Return false if stage isn`t change"""
        flag = False

        for key, value in old_data.items():
            if new_data.keys()[0] == key:
                if new_data.values()[0] != value:
                    flag = True
                else:
                    flag = False
                    break
            else:
                flag = True

        return flag
