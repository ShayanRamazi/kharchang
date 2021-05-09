from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
import datetime
import time

from core.models import DatabaseLock
from core.utils import string_to_date
from tsetmc.models import TseTmcCrawlTask, IntraTradeData, ClientTypeData, StaticTreshholdData, BestLimitBuyData, \
    BestLimitSellData, InstrumentStateData


class TseTmcCrawlTaskTest(TestCase):

    def test_successful_instrument(self):
        fameli_crawl_task = TseTmcCrawlTask(
            url="http://cdn.tsetmc.com/Loader.aspx?ParTree=15131P&i=35425587644337450&d=20210421",
            instrumentId="35425587644337450",
            dateToCrawl=string_to_date("20210421")
        )
        res = fameli_crawl_task.run()
        self.assertEqual(res, 1)
        self.assertEqual(TseTmcCrawlTask.objects.filter(instrumentId="35425587644337450").count(), 1)
        intra_trade_count = 8861
        inserted_intra_trade_count = IntraTradeData.objects.filter(
            instrumentId="35425587644337450",
            date=string_to_date("20210421")) \
            .count()
        self.assertEqual(intra_trade_count, inserted_intra_trade_count)
        self.assertEqual(ClientTypeData.objects.filter(
            date=datetime.date(2021, 4, 21),
            # time=datetime.time(15, 0, 0),
            instrumentId="35425587644337450"
        ).count(), 1)

    def test_successful_instrument_with_stopped_state(self):
        vatejarat_crawl_task = TseTmcCrawlTask(
            url="http://cdn.tsetmc.com/Loader.aspx?ParTree=15131P&i=63917421733088077&d=20090505",
            instrumentId="63917421733088077",
            dateToCrawl=string_to_date("20090505")
        )
        res = vatejarat_crawl_task.run()
        self.assertEqual(res, 1)
        self.assertEqual(TseTmcCrawlTask.objects.filter(instrumentId="63917421733088077").count(), 1)
        intra_trade_count = 0
        inserted_intra_trade_count = IntraTradeData.objects.filter(
            instrumentId="63917421733088077",
            date=string_to_date("20090505")) \
            .count()
        self.assertEqual(intra_trade_count, inserted_intra_trade_count)
        self.assertEqual(StaticTreshholdData.objects.filter(instrumentId="63917421733088077",
                                                            date=string_to_date("20090505")).count(), 1)

    def test_instrument_check_time(self):
        start_time = time.time()
        vatejarat_crawl_task = TseTmcCrawlTask(
            url="http://cdn.tsetmc.com/Loader.aspx?ParTree=15131P&i=65883838195688438&d=20210421",
            instrumentId="65883838195688438",
            dateToCrawl=string_to_date("20210421")
        )
        res = vatejarat_crawl_task.run()
        print("--- %s seconds ---" % (time.time() - start_time))

    def test_check_number_of_best_limits(self):
        fameli_crawl_task = TseTmcCrawlTask(
            url="http://cdn.tsetmc.com/Loader.aspx?ParTree=15131P&i=655060129740445&d=20210421",
            instrumentId="655060129740445",
            dateToCrawl=string_to_date("20210421")
        )
        res = fameli_crawl_task.run()
        self.assertEqual(res, 1)
        self.assertEqual(TseTmcCrawlTask.objects.filter(instrumentId="655060129740445").count(), 1)
        best_limits = 7604
        best_limits_buy = BestLimitBuyData.objects.filter(
            instrumentId="655060129740445",
            date=string_to_date("20210421")) \
            .count()
        best_limits_sell = BestLimitSellData.objects.filter(
            instrumentId="655060129740445",
            date=string_to_date("20210421")) \
            .count()
        self.assertGreaterEqual(best_limits_buy + best_limits_sell, best_limits)

    def test_successful_instrument_with_changing_state(self):
        # TODO: http://cdn.tsetmc.com/Loader.aspx?ParTree=15131P&i=35425587644337450&d=20210203
        crawl_task = TseTmcCrawlTask(
            url="http://cdn.tsetmc.com/Loader.aspx?ParTree=15131P&i=35425587644337450&d=20210203",
            instrumentId="35425587644337450",
            dateToCrawl=string_to_date("20210203")
        )
        res = crawl_task.run()
        self.assertEqual(res, 1)
        self.assertEqual(TseTmcCrawlTask.objects.filter(instrumentId="35425587644337450").count(), 1)
        number_of_status = 6
        number_of_status_saved = InstrumentStateData.objects.filter(
            instrumentId="35425587644337450",
            date=string_to_date("20210203")) \
            .count()
        self.assertEqual(number_of_status, number_of_status_saved)

    def test_task_lock_instrument(self):
        fameli_crawl_task = TseTmcCrawlTask(
            url="http://cdn.tsetmc.com/Loader.aspx?ParTree=15131P&i=35425587644337450&d=20210421",
            instrumentId="35425587644337450",
            dateToCrawl=string_to_date("20210421")
        )
        res = fameli_crawl_task.run()
        self.assertEqual(res, 1)
        fameli_crawl_task_another_day = TseTmcCrawlTask(
            url="http://cdn.tsetmc.com/Loader.aspx?ParTree=15131P&i=35425587644337450&d=20210422",
            instrumentId="35425587644337450",
            dateToCrawl=string_to_date("20210422")
        )
        res = fameli_crawl_task_another_day.run()
        self.assertEqual(res, 1)
        fameli_crawl_task_same_day = TseTmcCrawlTask(
            url="http://cdn.tsetmc.com/Loader.aspx?ParTree=15131P&i=35425587644337450&d=20210421",
            instrumentId="35425587644337450",
            dateToCrawl=string_to_date("20210421")
        )
        res = fameli_crawl_task_same_day.run()
        self.assertEqual(res, 0)


class TseTmcCrawlTaskInsertionMethodTest(TestCase):

    def test_atomicity(self):
        json_data = TseTmcCrawlTask.__parse_url__("http://cdn.tsetmc.com/Loader.aspx?ParTree=15131P&i=35425587644337450&d=20210421")[0]
        json_data["StaticTreshholdData"]["numberOfShares"] = "salam"
        # TseTmcCrawlTask.__insert_data_to_database__(json_data)
        self.assertRaises(ValueError, TseTmcCrawlTask.__insert_data_to_database__, json_data)
        inserted_intra_trade_count = IntraTradeData.objects.filter(
            instrumentId="35425587644337450",
            date=string_to_date("20210421")) \
            .count()
        self.assertEqual(inserted_intra_trade_count, 0)
        is_locked, state = DatabaseLock.is_locked("35425587644337450" + "__" + "20210421")
        self.assertEqual(is_locked, False)
