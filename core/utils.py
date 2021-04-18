import re

import jdatetime


def parse_simple_jalali_date(date_string):
    """
    :param date_string: some string like 1399/11/10, 1400/02/04, 1400/2/4
    :return:
    """
    parts = [int(x) for x in date_string.split("/")]
    return jdatetime.date(*parts).togregorian()


def add_month_to_jalali_string(date_string, months):
    if type(months) == float and months.is_integer():
        months = int(months)
    if type(months) != int:
        raise ValueError("months argument should be int")
    if months < 0:
        raise ValueError("months argument should be positive")
    parts = [int(x) for x in date_string.split("/")]
    temp = parts[1] + months
    parts[1] = temp % 12 if temp % 12 else 12
    parts[0] += (temp - 1) // 12

    parts = [str(x).rjust(2, "0") for x in parts]
    return "/".join(parts)


def georgian_to_simple_jalali_string(g_datetime):
    j_date = jdatetime.date.fromgregorian(year=g_datetime.year, month=g_datetime.month, day=g_datetime.day)
    return "/".join([str(j_date.year).rjust(4, "0"), str(j_date.month).rjust(2, "0"), str(j_date.day).rjust(2, "0")])


def get_first_number_from_string(string):
    temp = string.replace(",", "").replace("/", ".")
    temp_list = re.findall("\d*\.?\d+", temp)
    if len(temp_list) == 0:
        raise ValueError("string has no number in it")
    return float(temp_list[0])
