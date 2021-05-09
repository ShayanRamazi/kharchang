import time

from django.core.validators import MinValueValidator
from django.db import models, transaction, IntegrityError
from core.models import BaseModel, CrawlTask, DatabaseLock
from core.utils import insert_list_to_database, get_georgian_date_as_string_without_separator
import logging
import datetime
import tsetmc.utils as utils

django_logger = logging.getLogger(__name__)
LOCK_STATE_INSERTION_STARTED = "INS_START"
LOCK_STATE_INSERTION_ENDED = "INS_END"


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
    # time = models.TimeField()
    instrumentId = models.CharField(max_length=30)
    numberBuyReal = models.BigIntegerField()
    volumeBuyReal = models.BigIntegerField()
    valueBuyReal = models.BigIntegerField()
    priceBuyReal = models.FloatField()
    numberBuyLegal = models.BigIntegerField()
    volumeBuyLegal = models.BigIntegerField()
    valueBuyLegal = models.BigIntegerField()
    priceBuyLegal = models.FloatField()
    numberSellReal = models.BigIntegerField()
    volumeSellReal = models.BigIntegerField()
    valueSellReal = models.BigIntegerField()
    priceSellReal = models.FloatField()
    numberSellLegal = models.BigIntegerField()
    volumeSellLegal = models.BigIntegerField()
    valueSellLegal = models.BigIntegerField()
    priceSellLegal = models.FloatField()
    changeLegalToReal = models.BigIntegerField()


class MiddleDayClientTypeData(BaseModel):
    date = models.DateField()
    time = models.TimeField()
    instrumentId = models.CharField(max_length=30)
    numberBuyReal = models.BigIntegerField()
    volumeBuyReal = models.BigIntegerField()
    numberBuyLegal = models.BigIntegerField()
    volumeBuyLegal = models.BigIntegerField()
    numberSellReal = models.BigIntegerField()
    volumeSellReal = models.BigIntegerField()
    numberSellLegal = models.BigIntegerField()
    volumeSellLegal = models.BigIntegerField()


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
    turnover = models.BigIntegerField()
    valueOfTransactions = models.BigIntegerField()
    status = models.BooleanField(default=True)


class BestLimitBuyData(BaseModel):
    date = models.DateField()
    instrumentId = models.CharField(max_length=30)
    time = models.TimeField()
    row = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    amount = models.IntegerField()
    volume = models.IntegerField()
    price = models.IntegerField()


class BestLimitSellData(BaseModel):
    date = models.DateField()
    instrumentId = models.CharField(max_length=30)
    time = models.TimeField()
    row = models.PositiveIntegerField(validators=[MinValueValidator(1)])
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


class InstrumentStateData(BaseModel):
    STATUS_ID = [
        ('I', 'ممنوع'),
        ('A', 'مجاز'),
        ('AG', 'مجاز-مسدود'),
        ('AS', 'مجاز-متوقف'),
        ('AR', 'مجاز-محفوظ'),
        ('IG', 'ممنوع-مسدود'),
        ('IS', 'ممنوع-متوقف'),
        ('IR', 'ممنوع-محفوظ'),
    ]
    date = models.DateField()
    instrumentId = models.CharField(max_length=30)
    time = models.TimeField()
    status = models.CharField(
        max_length=2,
        choices=STATUS_ID
    )


class TseTmcCrawlTask(CrawlTask):
    dateToCrawl = models.DateField()
    instrumentId = models.CharField(max_length=30)

    @staticmethod
    def __parse_url__(url):
        return utils.getJson(url), 1

    @staticmethod
    @transaction.atomic
    def __insert_data_to_database__(json_data):
        lock_key = json_data["instrumentId"] + "__" + get_georgian_date_as_string_without_separator(json_data["date"])
        lock = DatabaseLock.lock_database_if_not_locked(lock_key, LOCK_STATE_INSERTION_STARTED)
        if lock is None:
            raise IntegrityError("data insertion for this pair of instrument and date is locked!(" + json_data[
                "instrumentId"] + "," + get_georgian_date_as_string_without_separator(json_data["date"]) + ")")
        argument_dict = {
            'instrumentId': json_data["instrumentId"],
            'date': json_data["date"]
        }
        # client_type_time_dict = {
        #     'time': datetime.time(15, 0, 0)
        # }
        start_true_dict = {"isStart": True}
        # django_logger.info("creating models for id " + json_data["instrumentId"] + " date " + json_data["date"])
        yesterday_share_holders = utils.create_entity_list(json_data["ShareHolderYesterdayData"],
                                                           {**argument_dict, **start_true_dict},
                                                           ShareHolderData.__name__)
        instrument_state_data = utils.create_entity_list(json_data["InstrumentStateData"], argument_dict,
                                                         InstrumentStateData.__name__)
        share_holders = utils.create_entity_list(json_data["ShareHolderData"], argument_dict, ShareHolderData.__name__)
        trades = utils.create_entity_list(json_data["IntraTradeData"], argument_dict, IntraTradeData.__name__)
        # client_type = ClientTypeData(**json_data["ClientTypeData"], **argument_dict, **client_type_time_dict)
        staticTreshholdData = StaticTreshholdData(**json_data["StaticTreshholdData"], **argument_dict)
        price_data_list = utils.create_entity_list(json_data["InstrumentPriceData"], argument_dict,
                                                   InstrumentPriceData.__name__)
        client_type_list = utils.create_entity_list(json_data["ClientTypeData"],
                                                    argument_dict,
                                                    ClientTypeData.__name__)
        buy_best_limits = utils.create_historical_buy_best_limits_list(json_data["BestLimits"], argument_dict)
        sell_best_limits = utils.create_historical_sell_best_limits_list(json_data["BestLimits"], argument_dict)
        insert_list_to_database(yesterday_share_holders)
        insert_list_to_database(share_holders)
        IntraTradeData.objects.bulk_create(trades)
        InstrumentPriceData.objects.bulk_create(price_data_list)
        ClientTypeData.objects.bulk_create(client_type_list)
        BestLimitBuyData.objects.bulk_create(buy_best_limits)
        BestLimitSellData.objects.bulk_create(sell_best_limits)
        InstrumentStateData.objects.bulk_create(instrument_state_data)
        staticTreshholdData.save()
        lock.state = LOCK_STATE_INSERTION_ENDED
        lock.save()
        return 1


class TseTmcInstrument(BaseModel):
    FLOWS = [
        (0, "عمومی، مشترک بین بورس و فرابورس"),
        (1, "بورس",),
        (2, "فرابورس"),
        (3, "آتی"),
        (4, "پایه فرابورس"),
        (5, "پایه فرابورس(منتشر نمی شود)"),
        (6, "بورس انرژی"),
        (7, "بورس کالا")
    ]
    instrumentId = models.CharField(max_length=30)
    isin = models.CharField(max_length=20)
    symbolFa = models.CharField(max_length=20)
    industry = models.CharField(max_length=50)
    flow = models.SmallIntegerField(choices=FLOWS)
    baseVolume = models.BigIntegerField()
    eps = models.IntegerField()
    pe = models.FloatField()
    pe_group = models.FloatField()
    totalShares = models.BigIntegerField()
    cisin = models.CharField(max_length=20)
