from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
import datetime

from core.utils import string_to_date
from tsetmc.models import TseTmcCrawlTask, IntraTradeData, ClientTypeData, StaticTreshholdData


# class TradeTest(TestCase):
#
#     def test_valid_create_trade(self):
#         valid_trade = Trade(
#             isin=2400322364771558,
#             date=timezone.now(),
#             volume=100,
#             price=100
#         )
#         valid_trade.full_clean()
#         valid_trade.save()
#         self.assertIs(valid_trade.canceled, False)
#
#     def test_invalid_create_trade(self):
#         invalid_trade = Trade(
#             isin=2400322364771558,
#             date=timezone.now(),
#             volume=-10,
#             price=100
#         )
#         # invalid_trade.save()
#         self.assertRaises(ValidationError, invalid_trade.full_clean)


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
            time=datetime.time(15, 0, 0),
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

    def test_successful_instrument_with_changing_state(self):
        # TODO: http://cdn.tsetmc.com/Loader.aspx?ParTree=15131P&i=35425587644337450&d=20210203
        self.assertEqual(1, 1)
