import datetime
from unittest import TestCase

from core.utils import parse_simple_jalali_date, add_month_to_jalali_string, georgian_to_simple_jalali_string, \
    get_first_number_from_string


class JalaliDateUtilsTest(TestCase):

    def test_parse_simple_jalali_date(self):
        someday_jalali_date_string = "1400/01/25"
        someday = datetime.date(2021, 4, 14)
        date = parse_simple_jalali_date(someday_jalali_date_string)
        self.assertEqual(someday, date)

        someday_jalali_date_string_2 = "1400/2/4"
        someday_2 = datetime.date(2021, 4, 24)
        date = parse_simple_jalali_date(someday_jalali_date_string_2)
        self.assertEqual(someday_2, date)

        bad_jalali_date_string = "1400/13/13"
        self.assertRaises(ValueError, parse_simple_jalali_date, bad_jalali_date_string)

    def test_add_month_to_jalali_string(self):
        day1 = '1399/12/12'
        day2 = '1400/06/12'
        day3 = '1400/07/12'
        day4 = '1400/12/12'
        day5 = '1401/12/12'
        day6 = '1400/01/12'
        day7 = '1401/01/12'

        self.assertEqual(day2, add_month_to_jalali_string(day1, 6))
        self.assertEqual(day3, add_month_to_jalali_string(day1, 7))
        self.assertEqual(day3, add_month_to_jalali_string(day2, 1))
        self.assertEqual(day4, add_month_to_jalali_string(day1, 12))
        self.assertEqual(day5, add_month_to_jalali_string(day1, 24))
        self.assertEqual(day4, add_month_to_jalali_string(day2, 6))
        self.assertEqual(day4, add_month_to_jalali_string(day3, 5))
        self.assertEqual(day6, add_month_to_jalali_string(day1, 1))
        self.assertEqual(day7, add_month_to_jalali_string(day1, 13))
        self.assertRaises(ValueError, add_month_to_jalali_string, day1, -2)
        self.assertRaises(ValueError, add_month_to_jalali_string, day2, 1.5)

    def test_georgian_to_simple_jalali_string(self):
        someday_jalali_date_string = "1400/01/25"
        someday = datetime.datetime(2021, 4, 14)
        date_string = georgian_to_simple_jalali_string(someday)
        self.assertEqual(date_string, someday_jalali_date_string)


class StringManipulationTest(TestCase):

    def test_get_first_number_from_string(self):
        string_1 = "salam123khodahafez2"
        number_1 = 123
        self.assertEqual(number_1, get_first_number_from_string(string_1))
        string_2 = "123"
        number_2 = 123
        self.assertEqual(number_2, get_first_number_from_string(string_2))
        string_3 = "123.123"
        number_3 = 123.123
        self.assertEqual(number_3, get_first_number_from_string(string_3))
        string_4 = "6ماه"
        number_4 = 6
        self.assertEqual(number_4, get_first_number_from_string(string_4))
        string_5 = "0 ماه"
        number_5 = 0
        self.assertEqual(number_5, get_first_number_from_string(string_5))
        string_6 = "20%"
        number_6 = 20
        self.assertEqual(number_6, get_first_number_from_string(string_6))
        string_7 = "1,000,000"
        number_7 = 1000000
        self.assertEqual(number_7, get_first_number_from_string(string_7))
        string_8 = "salam 123/123"
        number_8 = 123.123
        self.assertEqual(number_8, get_first_number_from_string(string_8))
        string_9 = "0123"
        number_9 = 123
        self.assertEqual(number_9, get_first_number_from_string(string_9))
        string_10 = "43/56"
        number_10 = 43.56
        self.assertEqual(number_10, get_first_number_from_string(string_10))
        string_11 = "1400/13/12"
        number_11 = 1400.13
        self.assertEqual(number_11, get_first_number_from_string(string_11))
        string_12 = "salam"
        self.assertRaises(ValueError, get_first_number_from_string, string_12)
        string_13 = ".123"
        number_13 = 0.123
        self.assertEqual(number_13, get_first_number_from_string(string_13))
