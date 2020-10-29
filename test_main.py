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


class Test_funct(unittest.TestCase):
    def test_func_1(self):
        test_par=m.create_parser()
        self.assertEqual(bool(test_par), True)

    def test_db(self):
        test_data={"1":"test"}
        m.db_save_stage_info(test_data)

if __name__ == '__main__':
    unittest.main()
