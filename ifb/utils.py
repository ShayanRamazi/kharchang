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


def post_by_payload(url, payload):
    session = requests.Session()
    response_1 = session.get(url)
    parsed_response = BeautifulSoup(response_1.text, "html.parser")
    viewstate_tag = parsed_response.find('input', attrs={"type": "hidden"})
    payload[viewstate_tag['name']] = viewstate_tag['value']
    return session.post(url, payload)


def get_akhza_list_from_ifb_site():
    akhza_list = []
    base_url = 'https://www.ifb.ir/Instrumentsmfi.aspx?id='
    number_in_page = 50
    url = 'https://www.ifb.ir/MFI/khazaneList.aspx'
    payload = {
        # r'TopControl1$ScriptManager1': r'',
        r'__EVENTTARGET': r'ctl00$ContentPlaceHolder1$grdFinancialData',
        r'__LASTFOCUS': r'',
        r'__EVENTARGUMENT': r'Page$1',
        # r'ctl00$ContentPlaceHolder1$grdFinancialData$ctl53$ctl04': r'',
        r'__VIEWSTATE': r'',
        r'__VIEWSTATEGENERATOR': r'',
        r'ctl00$ContentPlaceHolder1$grdFinancialData$ctl13$ctl12': r'' + str(number_in_page),
        r'ctl00$ContentPlaceHolder1$hddInstrument:': r'',
        r'ctl00$ContentPlaceHolder1$hddType': r'',
        # r'hiddenInputToUpdateATBuffer_CommonToolkitScripts': r'1'
    }
    for i in range(1, 10):
        payload[r'__EVENTARGUMENT'] = r'Page$' + str(i)
        response = post_by_payload(url, payload)
        parsed_html = BeautifulSoup(response.text, "html.parser")
        main_table = parsed_html.find("table", {"id": "ContentPlaceHolder1_grdFinancialData"})
        if not main_table:
            break
        links = main_table.find_all("a")
        if not links or len(links) == 0:
            break
        if len(links) > number_in_page:
            links = links[:number_in_page]
        for link in links:
            fbid = get_fbid_from_url(link['href'])
            akhza_list.append({
                'fbid': fbid,
                'url': base_url + str(fbid)
            })
    return akhza_list


def get_arad_list_from_ifb_site():
    arad_list = []
    base_url = 'https://www.ifb.ir/Instrumentsmfi.aspx?id='
    url = 'https://www.ifb.ir/ytm.aspx'
    parsed_html = get_url(url)
    arad_table = parsed_html.find("table", {"id": "ContentPlaceHolder1_grdytm"})
    links = arad_table.find_all("a")
    for link in links:
        fbid = get_fbid_from_url(link['href'])
        arad_list.append({
            'fbid': fbid,
            'url': base_url + str(fbid)
        })
    return arad_list
