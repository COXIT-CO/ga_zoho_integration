import unittest
from main import compare_change_in_data
import requests

class TestChange_in_data(unittest.TestCase):
    def test_func_1(self):
        old_data={"1":"q","2":"w","3":"e"}
        new_data={"3":"d"}
        flag=compare_change_in_data(old_data,new_data)
        self.assertTrue(flag)
    def test_func_2(self):
        old_data={"1":"q","2":"w","3":"e"}
        new_data={"4":"d"}
        flag=compare_change_in_data(old_data,new_data)
        self.assertTrue(flag)
    def test_func_3(self):
        old_data={"1":"q","2":"w","3":"e"}
        new_data={"3":"e"}
        flag=compare_change_in_data(old_data,new_data)
        self.assertFalse(flag)


class Test_responce(unittest.TestCase):
    def test_func_1(self):
        auth_header = {"Authorization": "Zoho-oauthtoken " + "1000.627c111e9881c15fedf96c0efd852354.b65c6e9f074ee727ef83b4b509a430c6"}
        ga_response = requests.get(
            url="https://www.zohoapis.eu" +
            "/crm/v2/" +
            "settings/variables",
            headers=auth_header)
        self.assertEqual(ga_response.status_code, 200)
    def test_func_2(self):
        auth_header = {"Authorization": "Zoho-oauthtoken " + "1000.627c111e9881c15fedf96c0efd852354.b65c6e9f074ee727ef83b4b509a430c6"}
        response = requests.get(
            url="https://www.zohoapis.eu" +
            "/crm/v2/" +
            "Deals" +
            "/"+
            "312530000000243268",
            headers=auth_header)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
