# pylint: disable=global-statement,import-error
"""unittest for main.py file"""
import unittest
import main as m

class TestChangeInData(unittest.TestCase):
    """This class testing compare_change_in_data function """
    def test_func_1(self):
        """test funct with fake data.test update value"""
        old_data = {"1": "q", "2": "w", "3": "e"}
        new_data = {"3": "d"}
        flag = m.compare_change_in_data(old_data, new_data)
        self.assertTrue(flag)

    def test_func_2(self):
        """test funct with fake data.test add value"""
        old_data = {"1": "q", "2": "w", "3": "e"}
        new_data = {"4": "d"}
        flag = m.compare_change_in_data(old_data, new_data)
        self.assertTrue(flag)

    def test_func_3(self):
        """test funct with fake data.test compare value"""
        old_data = {"1": "q", "2": "w", "3": "e"}
        new_data = {"3": "e"}
        flag = m.compare_change_in_data(old_data, new_data)
        self.assertFalse(flag)


class TestFunct(unittest.TestCase):
    """This class testing reate_parser and db_save_stage_info function """
    def test_func_1(self):
        """test funct what it return . Must return - True"""
        test_par = m.create_parser()
        self.assertEqual(bool(test_par), True)

    def test_db(self):
        """test funct save new data"""
        test_data = {"1": "test"}
        flag = m.db_save_stage_info(test_data)
        self.assertEqual(flag, False)


if __name__ == '__main__':
    unittest.main()
