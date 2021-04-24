from django.core.validators import MinValueValidator
from django.db import models
from core.models import BaseModel, CrawlTask
import logging

from core.utils import insert_list_to_database
from tsetmc.utils import create_entity_list, create_historical_buy_best_limits_list, \
    create_historical_sell_best_limits_list

django_logger = logging.getLogger(__name__)


class ShareHolderData(BaseModel):
    date = models.DateField()
    instrumentId = models.CharField(max_length=30)
    isinShareHolder = models.CharField(max_length=20, null=False)
    name = models.CharField(max_length=150)
    percentage = models.FloatField(default=0.0, validators=[MinValueValidator(1.0)])
    amountOfShares = models.BigIntegerField()
    isStart = models.BooleanField(null=True, blank=True)


class IntraTradeData(BaseModel):
    date = models.DateField()
    instrumentId = models.CharField(max_length=30)
    time = models.TimeField(null=False)
    amount = models.PositiveIntegerField(null=False, validators=[MinValueValidator(1)])
    price = models.IntegerField(null=False, validators=[MinValueValidator(0)])
    canceled = models.BooleanField(default=False)


class ClientTypeData(BaseModel):
    date = models.DateField()
    time = models.TimeField()
    instrumentId = models.CharField(max_length=30)
    numberBuyReal = models.IntegerField()
    volumeBuyReal = models.IntegerField()
    valueBuyReal = models.IntegerField()
    priceBuyReal = models.FloatField()
    numberBuyLegal = models.IntegerField()
    volumeBuyLegal = models.IntegerField()
    valueBuyLegal = models.IntegerField()
    priceBuyLegal = models.FloatField()
    numberSellReal = models.IntegerField()
    volumeSellReal = models.IntegerField()
    valueSellReal = models.IntegerField()
    priceSellReal = models.FloatField()
    numberSellRegal = models.IntegerField()
    volumeSellLegal = models.IntegerField()
    valueSellLegal = models.IntegerField()
    priceSellLegal = models.FloatField()
    changeLegalToReal = models.IntegerField()


class InstrumentPriceData(BaseModel):
    date = models.DateField()
    instrumentId = models.CharField(max_length=30)
    time = models.TimeField()
    lastTradePrice = models.IntegerField()
    lastPrice = models.IntegerField()
    firstPrice = models.IntegerField()
    yesterdayPrice = models.IntegerField()
    maxPrice = models.IntegerField()
    minPrice = models.IntegerField()
    numberOfTransactions = models.IntegerField()
    turnover = models.IntegerField()
    valueOfTransactions = models.IntegerField()
    status = models.BooleanField(default=True)


class BestLimitBuyData(BaseModel):
    date = models.DateField()
    instrumentId = models.CharField(max_length=30)
    time = models.TimeField()
    row = models.IntegerField(validators=[MinValueValidator[0]])
    amount = models.IntegerField()
    volume = models.IntegerField()
    price = models.IntegerField()


class BestLimitSellData(BaseModel):
    date = models.DateField()
    instrumentId = models.CharField(max_length=30)
    time = models.TimeField()
    row = models.IntegerField(validators=[MinValueValidator[0]])
    amount = models.IntegerField()
    volume = models.IntegerField()
    price = models.IntegerField()


class StaticTreshholdData(BaseModel):
    date = models.DateField()
    instrumentId = models.CharField(max_length=30)
    maxAllowed = models.IntegerField()
    minAllowed = models.IntegerField()
    baseVolume = models.BigIntegerField()
    numberOfShares = models.BigIntegerField()
    yesterdayPrice = models.IntegerField()


class TseTmcCrawlTask(CrawlTask):
    date_to_crawl = models.DateField()
    instrumentId = models.CharField(max_length=30)

    @staticmethod
    def __parse_url__(url):
        pass

    @staticmethod
    def __insert_data_to_database__(json_data):
        argument_dict = {
            'instrumentId': json_data["instrumentId"],
            'date': json_data["date"]
        }
        start_true_dict = {"isStart": True}
        # django_logger.info("creating models for id " + json_data["instrumentId"] + " date " + json_data["date"])
        yesterday_share_holders = create_entity_list(json_data["ShareHolderYesterdayData"],
                                                     {**argument_dict, **start_true_dict}, ShareHolderData.__name__)
        share_holders = create_entity_list(json_data["ShareHolderData"], argument_dict, ShareHolderData.__name__)
        trades = create_entity_list(json_data["IntraTradeData"], argument_dict, IntraTradeData.__name__)
        client_type = ClientTypeData(**json_data["ClientTypeData"])
        staticTreshholdData = StaticTreshholdData(**json_data["StaticTreshholdData"])
        price_data_list = create_entity_list(json_data["InstrumentPriceData"], InstrumentPriceData.__name__)
        buy_best_limits = create_historical_buy_best_limits_list(json_data["BestLimits"], argument_dict)
        sell_best_limits = create_historical_sell_best_limits_list(json_data["BestLimits"], argument_dict)
        insert_list_to_database(yesterday_share_holders)
        insert_list_to_database(share_holders)
        insert_list_to_database(trades)
        client_type.save()
        staticTreshholdData.save()
        insert_list_to_database(price_data_list)
        insert_list_to_database(buy_best_limits)
        insert_list_to_database(sell_best_limits)
        return 1
