from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from core.utils import string_to_date
from tsetmc.models import TseTmcCrawlTask, IntraTradeData


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
            date_to_crawl=string_to_date("20210421")
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

    def test_successful_instrument_with_zero_volume(self):
        vatejarat_crawl_task = TseTmcCrawlTask(
            url="http://cdn.tsetmc.com/Loader.aspx?ParTree=15131P&i=63917421733088077&d=20090505",
            instrumentId="35425587644337450",
            date_to_crawl=string_to_date("20210421")
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

    # def test_arad_with_bad_settlement_date(self):
    #     arad36_crawl_task = IFBCrawlTask(url="https://www.ifb.ir/Instrumentsmfi.aspx?id=24894")
    #     res = arad36_crawl_task.run()
    #     self.assertEqual(res, 0)
    #     self.assertEqual(IFBInstrument.objects.filter(fbid=24894).count(), 0)
    #
    # def test_arad_with_bad_payment_detail(self):
    #     arad62_crawl_task = IFBCrawlTask(url="https://www.ifb.ir/Instrumentsmfi.aspx?id=25243")
    #     res = arad62_crawl_task.run()
    #     self.assertEqual(res, 0)
    #     self.assertEqual(IFBInstrument.objects.filter(fbid=25243).count(), 0)
    #
    # def test_successful_akhza(self):
    #     akhza812_crawl_task = IFBCrawlTask(url="https://www.ifb.ir/Instrumentsmfi.aspx?id=24297")
    #     res = akhza812_crawl_task.run()
    #     self.assertEqual(res, 1)
    #     self.assertEqual(IFBInstrument.objects.filter(fbid=24297).count(), 1)
    #
    # def test_successful_akhza_2(self):
    #     akhza1_crawl_task = IFBCrawlTask(url="https://www.ifb.ir/Instrumentsmfi.aspx?id=21783")
    #     res = akhza1_crawl_task.run()
    #     self.assertEqual(res, 1)
    #     self.assertEqual(IFBInstrument.objects.filter(fbid=21783).count(), 1)
    #
    # def test_successful_akhza_3(self):
    #     akhza911_crawl_task = IFBCrawlTask(url="https://www.ifb.ir/Instrumentsmfi.aspx?id=25368")
    #     res = akhza911_crawl_task.run()
    #     self.assertEqual(res, 1)
    #     self.assertEqual(IFBInstrument.objects.filter(fbid=25368).count(), 1)
    #
    # def test_error_url(self):
    #     ifb_crawl_task = IFBCrawlTask(url="https://www.ifb.ir/ytm.aspx")
    #     res = ifb_crawl_task.run()
    #     self.assertEqual(res, 0)
    #     self.assertEqual(IFBInstrument.objects.count(), 0)
    #
    # def test_bad_ifb_instrument(self):
    #     mahan01_crawl_task = IFBCrawlTask(url="https://www.ifb.ir/Instrumentsmfi.aspx?id=25326")
    #     res = mahan01_crawl_task.run()
    #     self.assertEqual(res, 0)
    #     self.assertEqual(IFBInstrument.objects.count(), 0)
