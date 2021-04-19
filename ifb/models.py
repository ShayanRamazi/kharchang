import logging
import math

import requests
from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models

from core.models import BaseModel, CrawlTask
from core.utils import parse_simple_jalali_date, georgian_to_simple_jalali_string, add_month_to_jalali_string, \
    get_first_number_from_string

from django_mysql.models import ListCharField, ListTextField

from ifb.utils import get_url, get_table_data_by_keys, add_key_values_to_dict, get_table_data_by_ids, get_fbid_from_url, \
    post_by_payload

import logging

django_logger = logging.getLogger(__name__)


class IFBInstrument(BaseModel):
    fbid = models.CharField(max_length=10, unique=True)
    ifbUrl = models.URLField(max_length=300, validators=[URLValidator], unique=True)
    symbolFa = models.CharField(max_length=50)
    companyFa = models.CharField(max_length=100)
    mnemonic = models.CharField(max_length=50)
    companyEn = models.CharField(max_length=100)
    isin = models.CharField(max_length=50, unique=True)
    market = models.CharField(max_length=50, null=True, blank=True)
    industry = models.CharField(max_length=50, null=True, blank=True)
    subIndustry = models.CharField(max_length=50)
    parValue = models.IntegerField()
    totalCount = models.IntegerField()
    listedCount = models.IntegerField()
    settlementDate = models.DateField()
    publishDate = models.DateField()
    duration = models.SmallIntegerField()
    subject = models.CharField(max_length=100)
    nominalReturnRate = models.SmallIntegerField()
    couponPeriod = models.SmallIntegerField()
    issuer = models.CharField(max_length=200)
    underWriter = models.CharField(max_length=200, null=True, blank=True)
    guarantor = models.CharField(max_length=200)
    profitDistributionAgent = models.CharField(max_length=200)
    saleAgent = models.CharField(max_length=200, null=True, blank=True)
    marketMaker = models.CharField(max_length=200, null=True, blank=True)
    originator = models.CharField(max_length=200, null=True, blank=True)
    profitDistributionDates = ListCharField(
        base_field=models.CharField(max_length=10),
        size=40,
        max_length=(40 * 11),
        null=True, blank=True
    )
    profitDistributionValues = ListCharField(
        base_field=models.CharField(max_length=12),
        size=40,
        max_length=(40 * 13),
        null=True, blank=True
    )
    paymentDetailsDates = ListTextField(
        base_field=models.CharField(max_length=11),
        null=True, blank=True
    )
    paymentDetailsValues = ListTextField(
        base_field=models.CharField(max_length=14),
        null=True, blank=True
    )

    def validate_payment_details_start(self):
        if self.couponPeriod:
            start_date = parse_simple_jalali_date(self.paymentDetailsDates[0])
            if start_date == self.publishDate:
                return True
            raise ValidationError("Instrument payment detail start date:" +
                                  georgian_to_simple_jalali_string(start_date) +
                                  " is not equal to publish date:" +
                                  georgian_to_simple_jalali_string(self.publishDate)
                                  )
        elif len(self.paymentDetailsDates) == 0:
            return True
        else:
            raise ValidationError("This instrument has no coupons and should have empty payment date list")

    def validate_payment_details_end(self):
        if self.couponPeriod:
            end_date = parse_simple_jalali_date(self.paymentDetailsDates[-1])
            if end_date == self.settlementDate:
                return True
            raise ValidationError("Instrument payment detail end date:" +
                                  georgian_to_simple_jalali_string(end_date) +
                                  " is not equal to settlement date:" +
                                  georgian_to_simple_jalali_string(self.settlementDate)
                                  )
        elif len(self.paymentDetailsDates) == 0:
            return True
        else:
            raise ValidationError("This instrument has no coupons and should have exactly one payment date")

    def validate_payment_details_date_order(self):
        for i in range(len(self.paymentDetailsDates) - 1):
            date1 = parse_simple_jalali_date(self.paymentDetailsDates[i])
            date2 = parse_simple_jalali_date(self.paymentDetailsDates[i + 1])
            if date1 > date2:
                raise ValidationError("payment details dates should be ordered incrementally")
        return True

    def validate_payment_details_length(self):
        if self.couponPeriod and len(self.paymentDetailsDates) == len(self.paymentDetailsValues):
            dates_count = (self.settlementDate - self.publishDate).days + 1
            if len(self.paymentDetailsDates) == dates_count:
                return True
        elif len(self.paymentDetailsDates) == 0 and len(self.paymentDetailsValues) == 0:
            return True
        raise ValidationError("payment details dates and values must have equal lengths, also payment details ")

    def validate_profit_distribution_start(self):
        if self.couponPeriod:
            publish_date_jalali_string = georgian_to_simple_jalali_string(self.publishDate)
            first_coupon_date = parse_simple_jalali_date(
                add_month_to_jalali_string(publish_date_jalali_string, self.couponPeriod))
            start_date = parse_simple_jalali_date(self.profitDistributionDates[0])
            if start_date == first_coupon_date:
                return True
            raise ValidationError("Instrument profit distribution start date: " +
                                  georgian_to_simple_jalali_string(start_date) +
                                  " is not equal to publish date + coupon period:" +
                                  georgian_to_simple_jalali_string(first_coupon_date)
                                  )
        elif len(self.profitDistributionDates) == 0:
            return True
        else:
            raise ValidationError("This instrument has no coupons and should not have any distribution dates")

    def validate_profit_distribution_end(self):
        if self.couponPeriod:
            end_date = parse_simple_jalali_date(self.profitDistributionDates[-1])
            if end_date == self.settlementDate:
                return True
            raise ValidationError("Instrument profit distribution end date:" +
                                  georgian_to_simple_jalali_string(end_date) +
                                  " is not equal to settlement date:" +
                                  georgian_to_simple_jalali_string(self.settlementDate)
                                  )
        elif len(self.profitDistributionDates) == 0:
            return True
        else:
            raise ValidationError("This instrument has no coupons and should not have any distribution dates")

    def validate_profit_distribution_date_order(self):
        for i in range(len(self.profitDistributionDates) - 1):
            date1 = parse_simple_jalali_date(self.profitDistributionDates[i])
            date2 = parse_simple_jalali_date(self.profitDistributionDates[i + 1])
            if date1 > date2:
                raise ValidationError("profit distribution dates should be ordered incrementally")
        return True

    def validate_profit_distribution_length(self):
        if not len(self.profitDistributionDates) == len(self.profitDistributionValues):
            raise ValidationError("profit distribution dates and values must have equal lengths")
        if not self.couponPeriod or \
                math.ceil(self.duration / self.couponPeriod) + 1 == len(self.profitDistributionDates):
            return True
        else:
            raise ValidationError("incorrect number of profit distribution dates")

    def validate(self):
        return self.validate_payment_details_start() and \
               self.validate_payment_details_end() and \
               self.validate_profit_distribution_start() and \
               self.validate_profit_distribution_end() and \
               self.validate_profit_distribution_date_order() and \
               self.validate_payment_details_date_order() and \
               self.validate_payment_details_length() and \
               self.validate_profit_distribution_length()

    def save(self, *args, **kwargs):
        if self.validate():
            return super(IFBInstrument, self).save(*args, **kwargs)
        else:
            raise ValidationError("validation error")


class IFBCrawlTask(CrawlTask):

    @staticmethod
    def __parse_url__(url):
        base_url = "https://www.ifb.ir/Instrumentsmfi.aspx?id="
        instrument_data = {
            "ifbUrl": url,
            "fbid": get_fbid_from_url(url),
        }
        django_logger.info("parsing for fbid:", instrument_data["fbid"])
        parsed_html = get_url(url)
        inst_tables = parsed_html.find_all("table", {"class": "insTable"})

        symbol_info_table = inst_tables[0]
        symbol_info_keys = ["companyFa", "symbolFa", "companyEn", "mnemonic"]
        symbol_info_values = get_table_data_by_keys(symbol_info_table)
        instrument_data = add_key_values_to_dict(instrument_data, symbol_info_keys, symbol_info_values)

        market_info_table = inst_tables[1]
        market_info_keys = ["isin", "market", "industry", "subIndustry"]
        market_info_values = get_table_data_by_keys(market_info_table)
        instrument_data = add_key_values_to_dict(instrument_data, market_info_keys, market_info_values)

        # sukuk_info_table_1 = inst_tables[2]
        sukuk_info_map = {
            "parValue": {
                "id": "ContentPlaceHolder1_lblMablaghEsmi",
                "type": "numeric"
            },
            "publishDate": {
                "id": "ContentPlaceHolder1_lblTarikhEnteshar",
                "type": "date"
            },
            "subject": {
                "id": "ContentPlaceHolder1_Label2",
                "type": "string"
            },
            "nominalReturnRate": {
                "id": "ContentPlaceHolder1_Label3",
                "type": "numeric"
            },
            "totalCount": {
                "id": "ContentPlaceHolder1_Label4",
                "type": "numeric"
            },
            "listedCount": {
                "id": "ContentPlaceHolder1_Label5",
                "type": "numeric"
            },
            "settlementDate": {
                "id": "ContentPlaceHolder1_Label8",
                "type": "date"
            },
            "couponPeriod": {
                "id": "ContentPlaceHolder1_Label16",
                "type": "numeric"
            },
            "duration": {
                "id": "ContentPlaceHolder1_lblOragh",
                "type": "numeric"
            },
        }
        sukuk_info_values = get_table_data_by_ids(parsed_html, sukuk_info_map)
        instrument_data = add_key_values_to_dict(instrument_data, list(sukuk_info_map.keys()), sukuk_info_values)

        pillars_info_map = {
            "issuer": {
                "id": "ContentPlaceHolder1_Label6",
                "type": "string"
            },
            "underWriter": {
                "id": "ContentPlaceHolder1_Label7",
                "type": "string"
            },
            "guarantor": {
                "id": "ContentPlaceHolder1_Label10",
                "type": "string"
            },
            "profitDistributionAgent": {
                "id": "ContentPlaceHolder1_Label12",
                "type": "string"
            },
            "originator": {
                "id": "ContentPlaceHolder1_lblBaani",
                "type": "string"
            },
            "marketMaker": {
                "id": "ContentPlaceHolder1_lblBazargardan",
                "type": "string"
            },
            "saleAgent": {
                "id": "ContentPlaceHolder1_lblAmelForoosh",
                "type": "string"
            },
        }
        pillar_info_values = get_table_data_by_ids(parsed_html, pillars_info_map)
        instrument_data = add_key_values_to_dict(instrument_data, list(pillars_info_map.keys()), pillar_info_values)

        def get_excel_data_values(payload, direction=1):
            dates = []
            values = []
            session = requests.Session()
            temp_url = base_url + str(instrument_data["fbid"])
            # my_session = session.get(temp_url)
            # parsed_session = BeautifulSoup(my_session.text, "html.parser")
            # viewstate_tag = parsed_session.find('input', attrs={"type": "hidden"})
            # payload[viewstate_tag['name']] = viewstate_tag['value']
            # excel_resp = session.post(temp_url, payload)
            excel_resp = post_by_payload(temp_url, payload)
            parsed_excel_data = BeautifulSoup(excel_resp.text, "html.parser")
            table_rows = parsed_excel_data.find_all("tr")
            for table_row in table_rows[1:][::direction]:
                tds = table_row.find_all("td")
                # if len(tds) != 2:
                #     continue
                dates.append(tds[0].text.strip())
                values.append(get_first_number_from_string(tds[1].text.strip()))
            return dates, values

        if instrument_data["couponPeriod"]:
            profit_distribution_payload = {
                r'TopControl1$ScriptManager1': r'',
                r'__EVENTTARGET': r'ctl00$ContentPlaceHolder1$LinkButton1',
                r'__EVENTARGUMENT': r'',
                r'ctl00$ContentPlaceHolder1$btnExport': r'',
                r'TopControl1$TxtRecherche': r'',
                r'TopControl1$txtValeur': r'',
                r'hiddenInputToUpdateATBuffer_CommonToolkitScripts': r'1'
            }

            payment_details_payload = {
                r'TopControl1$ScriptManager1': r'',
                r'__EVENTTARGET': r'ctl00$ContentPlaceHolder1$LinkButton1',
                r'__EVENTARGUMENT': r'',
                r'TopControl1$TxtRecherche': r'',
                r'TopControl1$txtValeur': r'',
                r'hiddenInputToUpdateATBuffer_CommonToolkitScripts': r'1'
            }

            django_logger.info("requesting profit distributions data:", instrument_data["fbid"])
            instrument_data["profitDistributionDates"], instrument_data[
                "profitDistributionValues"] = get_excel_data_values(profit_distribution_payload, direction=-1)

            django_logger.info("requesting payment details data:", instrument_data["fbid"])
            instrument_data["paymentDetailsDates"], instrument_data[
                "paymentDetailsValues"] = get_excel_data_values(payment_details_payload, direction=1)
        else:
            instrument_data["profitDistributionDates"] = []
            instrument_data["profitDistributionValues"] = []
            instrument_data["paymentDetailsDates"] = []
            instrument_data["paymentDetailsValues"] = []

        return instrument_data

    @staticmethod
    def __insert_data_to_database__(json_data):
        instrument = IFBInstrument(**json_data)
        instrument.full_clean()
        django_logger.info("saving to database:", instrument.fbid)
        instrument.save()
        return 1
