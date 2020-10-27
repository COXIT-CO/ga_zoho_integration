import unittest
import main as m
import requests

class TestChange_in_data(unittest.TestCase):
    def test_func_1(self):
        old_data={"1":"q","2":"w","3":"e"}
        new_data={"3":"d"}
        flag=m.compare_change_in_data(old_data,new_data)
        self.assertTrue(flag)
    def test_func_2(self):
        old_data={"1":"q","2":"w","3":"e"}
        new_data={"4":"d"}
        flag=m.compare_change_in_data(old_data,new_data)
        self.assertTrue(flag)
    def test_func_3(self):
        old_data={"1":"q","2":"w","3":"e"}
        new_data={"3":"e"}
        flag=m.compare_change_in_data(old_data,new_data)
        self.assertFalse(flag)


class Test_responce(unittest.TestCase):
    token="1000.d816650a06c2191707cd7936e0062ba3.9ae6ec4407999bf81acb765435e23a26"
    def test_func_1(self):
        auth_header = {"Authorization": "Zoho-oauthtoken " + self.token}
        ga_response = requests.get(
            url="https://www.zohoapis.eu" +
            "/crm/v2/" +
            "settings/variables",
            headers=auth_header)
        self.assertEqual(ga_response.status_code, 200)
    def test_func_2(self):
        auth_header = {"Authorization": "Zoho-oauthtoken " + self.token}
        response = requests.get(
            url="https://www.zohoapis.eu" +
            "/crm/v2/" +
            "Deals" +
            "/"+
            "312530000000243268",
            headers=auth_header)
        self.assertEqual(response.status_code, 200)
    def test_creat_req(self):
        m.creat_requests()

class Test_funct(unittest.TestCase):
    def test_func_1(self):
        test_par=m.create_parser()
        self.assertEqual(bool(test_par), True)

    def test_db(self):
        test_data={"1":"test"}
        m.db_save_stage_info(test_data)

    def test_init(self):
        test_config = m.initialize_variebles()
        self.assertEqual(bool(test_config), True)


if __name__ == '__main__':
    unittest.main()
