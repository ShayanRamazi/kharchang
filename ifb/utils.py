import requests
from bs4 import BeautifulSoup
import re

from core.utils import parse_simple_jalali_date, get_first_number_from_string


def get_url(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser")


def ifb_td_get_value_by_title(title, tds):
    for td in tds:
        if td.find(text=re.compile(title)):
            return td.find_next_sibling().text.strip()


def ifb_td_get_value_by_span_id(span_id, parsed_html):
    span = parsed_html.find("span", {"id": span_id})
    if span is not None:
        return span.find_parent().find_next_sibling().text.strip()
    return None


def get_table_data_by_keys(table_html):
    values = []
    table_rows = table_html.find_all("tr")
    for tr in table_rows:
        values.append(tr.find_all("td")[1].text.strip())
    return values


def get_table_data_by_ids(table_html, id_map):
    values = []
    for key in id_map.keys():
        item = id_map[key]
        val = ifb_td_get_value_by_span_id(item["id"], table_html)
        if item["type"] == "numeric":
            val = get_first_number_from_string(val)
        elif item["type"] == "date":
            val = parse_simple_jalali_date(val)
        values.append(val)
    return values


def add_key_values_to_dict(my_dict, keys, values):
    if len(keys) != len(values):
        raise ValueError("keys and values should have same length")
    for i in range(len(keys)):
        my_dict[keys[i]] = values[i]
    return my_dict


def get_fbid_from_url(url):
    ids = re.findall("id=+([0-9]*)", url)
    if len(ids) > 0:
        return ids[0]
    else:
        return None
