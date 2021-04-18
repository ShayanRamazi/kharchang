import datetime
import random

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from core.utils import parse_simple_jalali_date, georgian_to_simple_jalali_string
from ifb.models import IFBInstrument, IFBCrawlTask

akhza_data_dict = {
    "ifbUrl": "https://ifb.ir/132143355",
    "fbid": 132143355,
    "symbolFa": "اخزا۸۱۰",
    "companyFa": "اسنادخزانه-م۱۰بودجه۸۷۳۸۳۰-۰۹۸۲۶۳۳",
    "mnemonic": "TB641",
    "companyEn": "TreasurayBill86351",
    "isin": "IRB3TB6400A1",
    "market": "اوراق با در‌آمد ثابت",
    "industry": 'اوراق تامین مالی',
    "subIndustry": "اسناد خزانه اسلامی",
    "parValue": 1000000,
    "totalCount": 10000000,
    "listedCount": 10000000,
    "settlementDate": parse_simple_jalali_date("1401/10/06"),
    "publishDate": parse_simple_jalali_date("1398/03/18"),
    "duration": 48,
    "subject": "اسناد خزانه",
    "nominalReturnRate": 0,
    "couponPeriod": 0,
    "issuer": "وزارت امور اقتصادی و دارایی",
    "guarantor": "خزانه داری کل کشور",
    "profitDistributionAgent": "شرکت سپرده گذاری مرکزی اوراق بهادار و تسویه وجوه",
    "profitDistributionDates": [],
    "profitDistributionValues": [],
    "paymentDetailsDates": [],
    "paymentDetailsValues": []
}

arad_data_dict = {
    "ifbUrl": "https://ifb.ir/13214343143355",
    "fbid": 1323355,
    "symbolFa": "اخزا۸۱۰",
    "companyFa": "اسنادخزانه-م۱۰بودجه۸۷۳۸۳۰-۰۹۸۲۶۳۳",
    "mnemonic": "TB641",
    "companyEn": "TreasurayBill86351",
    "isin": "IRB4SG5100A1",
    "market": "اوراق با در‌آمد ثابت",
    "industry": 'اوراق تامین مالی',
    "subIndustry": "اسناد خزانه اسلامی",
    "parValue": 1000000,
    "totalCount": 10000000,
    "listedCount": 10000000,
    "settlementDate": parse_simple_jalali_date("1400/10/25"),
    "publishDate": parse_simple_jalali_date("1399/06/25"),
    "subject": "اسناد خزانه",
    "nominalReturnRate": 15,
    "couponPeriod": 6,
    "duration": 16,
    "issuer": "وزارت امور اقتصادی و دارایی",
    "guarantor": "خزانه داری کل کشور",
    "profitDistributionAgent": "شرکت سپرده گذاری مرکزی اوراق بهادار و تسویه وجوه",
    "profitDistributionDates": ["1399/12/25",
                                "1400/06/25",
                                "1400/10/25",
                                "1400/10/25"],
    "profitDistributionValues": [74183.33, 75819.67, 1000000, 49726.03],
    "paymentDetailsDates": [],
    "paymentDetailsValues": []
}

total_dates = (arad_data_dict["settlementDate"] - arad_data_dict["publishDate"]).days + 1
one_day = datetime.timedelta(days=1)
for i in range(total_dates):
    arad_data_dict["paymentDetailsDates"].append(
        georgian_to_simple_jalali_string(arad_data_dict["publishDate"] + i * one_day))
    arad_data_dict["paymentDetailsValues"].append((random.random() - .5) * 1000)


class IFBInstrumentTest(TestCase):

    def test_akhza_save(self):
        inst = IFBInstrument(**akhza_data_dict)
        inst.full_clean()
        inst.save()
        retrieved_inst = IFBInstrument.objects.get(id=inst.id)
        self.assertEqual(retrieved_inst.profitDistributionAgent, akhza_data_dict["profitDistributionAgent"])
        self.assertEqual(len(retrieved_inst.profitDistributionDates), 0)

    def test_isin_unique(self):
        inst = IFBInstrument(**akhza_data_dict)
        inst.save()
        inst2 = IFBInstrument(**akhza_data_dict)
        self.assertRaises(IntegrityError, inst2.save)

    def test_arad_save(self):
        inst = IFBInstrument(**arad_data_dict)
        inst.full_clean()
        inst.save()
        retrieved_inst = IFBInstrument.objects.get(id=inst.id)
        self.assertEqual(len(retrieved_inst.profitDistributionDates), len(arad_data_dict["profitDistributionDates"]))
        self.assertEqual(len(retrieved_inst.paymentDetailsDates), len(arad_data_dict["paymentDetailsDates"]))

    def test_validate_payment_details(self):
        arad_data_dict["paymentDetailsDates"].append(
            georgian_to_simple_jalali_string(arad_data_dict["settlementDate"])
        )
        inst = IFBInstrument(**arad_data_dict)
        self.assertRaises(ValidationError, inst.save)
        arad_data_dict["paymentDetailsValues"].append(10)
        inst = IFBInstrument(**arad_data_dict)
        self.assertRaises(ValidationError, inst.save)
        a = arad_data_dict["paymentDetailsDates"][0]
        b = arad_data_dict["paymentDetailsValues"][0]
        del arad_data_dict["paymentDetailsDates"][0]
        del arad_data_dict["paymentDetailsValues"][0]
        inst = IFBInstrument(**arad_data_dict)
        self.assertRaises(ValidationError, inst.save)
        del arad_data_dict["paymentDetailsDates"][-1]
        del arad_data_dict["paymentDetailsValues"][-1]
        arad_data_dict["paymentDetailsDates"].insert(0, a)
        arad_data_dict["paymentDetailsValues"].insert(0, b)
        inst = IFBInstrument(**arad_data_dict)
        inst.save()

    def test_validate_profit_distribution(self):
        arad_data_dict["isin"] = "sdfsdfsdfsdfsdf"
        arad_data_dict["ifbUrl"] = "https:\\sdfsdfsdfsdfsdf.com"
        arad_data_dict["fbid"] = "345462345"
        inst = IFBInstrument(**arad_data_dict)
        inst.save()
        arad_data_dict["isin"] = "y832b421j4b123"
        arad_data_dict["ifbUrl"] = "https:\\y832b421j4b123.com"
        arad_data_dict["fbid"] = "359462345"
        arad_data_dict["profitDistributionDates"].append(
            georgian_to_simple_jalali_string(arad_data_dict["settlementDate"])
        )
        inst = IFBInstrument(**arad_data_dict)
        self.assertRaises(ValidationError, inst.save)
        arad_data_dict["profitDistributionValues"].append(10)
        inst = IFBInstrument(**arad_data_dict)
        self.assertRaises(ValidationError, inst.save)
        a = arad_data_dict["profitDistributionDates"][0]
        b = arad_data_dict["profitDistributionValues"][0]
        del arad_data_dict["profitDistributionDates"][0]
        del arad_data_dict["profitDistributionValues"][0]
        inst = IFBInstrument(**arad_data_dict)
        self.assertRaises(ValidationError, inst.save)
        arad_data_dict["profitDistributionDates"].insert(0, a)
        arad_data_dict["profitDistributionValues"].insert(0, b)
        del arad_data_dict["profitDistributionDates"][-1]
        del arad_data_dict["profitDistributionValues"][-1]
        inst.save()


class IFBCrawlTaskTest(TestCase):

    def test_successful_arad(self):
        arad51_crawl_task = IFBCrawlTask(url="https://www.ifb.ir/Instrumentsmfi.aspx?id=25090")
        res = arad51_crawl_task.run()
        self.assertEqual(res, 1)
        self.assertEqual(IFBInstrument.objects.filter(fbid=25090).count(), 1)

    def test_successful_akhza(self):
        akhza812_crawl_task = IFBCrawlTask(url="https://www.ifb.ir/Instrumentsmfi.aspx?id=24297")
        res = akhza812_crawl_task.run()
        self.assertEqual(res, 1)
        self.assertEqual(IFBInstrument.objects.filter(fbid=24297).count(), 1)

    def test_error_url(self):
        ifb_crawl_task = IFBCrawlTask(url="https://www.ifb.ir/ytm.aspx")
        res = ifb_crawl_task.run()
        self.assertEqual(res, 0)
        self.assertEqual(IFBInstrument.objects.count(), 0)

    def test_bad_ifb_instrument(self):
        mahan01_crawl_task = IFBCrawlTask(url="https://www.ifb.ir/Instrumentsmfi.aspx?id=25326")
        res = mahan01_crawl_task.run()
        self.assertEqual(res, 0)
        self.assertEqual(IFBInstrument.objects.count(), 0)
