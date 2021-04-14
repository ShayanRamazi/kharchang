import datetime
from unittest import TestCase

from core.utils import parse_simple_jalali_date, add_month_to_jalali_string, georgian_to_simple_jalali_string


class JalaliDateUtilsTest(TestCase):

    def test_parse_simple_jalali_date(self):
        someday_jalali_date_string = "1400/01/25"
        someday = datetime.datetime(2021, 4, 14)
        date = parse_simple_jalali_date(someday_jalali_date_string)
        self.assertEqual(someday, date)

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
