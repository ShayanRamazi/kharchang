from django.core.validators import MinValueValidator
from django.db import models, transaction, IntegrityError
from core.models import BaseModel, CrawlTask, DatabaseLock
from core.utils import insert_list_to_database, get_georgian_date_as_string_without_separator
import logging
import datetime
import tsetmc.utils as utils
from django_mysql.models import ListTextField
from ifb.utils import get_url_parse_BS, get_table_data_by_keys, add_key_values_to_dict, get_table_data_by_ids, \
    get_fbid_from_url, \
    post_by_payload
from django_mysql.models import ListTextField

django_logger = logging.getLogger(__name__)
LOCK_STATE_INSERTION_STARTED = "INS_START"
LOCK_STATE_INSERTION_ENDED = "INS_END"


class ShareHolderData(BaseModel):
    idShareHolder=models.IntegerField(default=-1)
    date = models.DateField()
    instrumentId = models.CharField(max_length=30)
    isinShareHolder = models.CharField(max_length=20, null=False)
    name = models.CharField(max_length=150)
    percentage = models.FloatField(default=0.0, validators=[MinValueValidator(1.0)])
    amountOfShares = models.BigIntegerField()
    isStart = models.BooleanField(null=True, blank=True)


class IntraTradeData(BaseModel):
    date = models.DateField(null=True)
    instrumentId = models.CharField(null=True,max_length=30)
    time = models.TimeField(null=True)
    amount = models.PositiveIntegerField(null=False, validators=[MinValueValidator(1)])
    price = models.IntegerField(null=False, validators=[MinValueValidator(0)])
    canceled = models.BooleanField(default=False)


class ClientTypeData(BaseModel):
    date = models.DateField()
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
    instrumentId = models.CharField(max_length=30, unique=True)
    isin_12 = models.CharField(max_length=12)
    isin_5 = models.CharField(max_length=5)
    companyEn = models.CharField(max_length=50)
    isin_company_4 = models.CharField(max_length=4)
    companyFa = models.CharField(max_length=100)
    symbolFa = models.CharField(max_length=50)
    symbolFa_30 = models.CharField(max_length=30)
    isin_company_12 = models.CharField(max_length=12)
    market = models.CharField(max_length=50, null=True, blank=True)
    Board_code = models.CharField(max_length=2)
    industry_code = models.CharField(max_length=4)
    industry = models.CharField(max_length=50)
    subIndustry_code = models.CharField(max_length=10)
    subIndustry = models.CharField(max_length=50)


class TseTmcIdentityCertificateCrawlTask(CrawlTask):
    instrumentId = models.CharField(max_length=30)

    @staticmethod
    def __parse_url__(url):
        soup = get_url_parse_BS(url)
        identity_certificate = utils.find_rows(soup)
        symbol_Identity_Certificate_keys = ["isin_12", "isin_5", "companyEn", "isin_company_4", "companyFa", "symbolFa",
                                            "symbolFa_30", "isin_company_12", "market", "Board_code", "industry_code",
                                            'industry', "subIndustry_code", "subIndustry"]
        dict_Identity_Certificate_tsetmc = dict()
        n = 0
        for i in identity_certificate:
            dict_Identity_Certificate_tsetmc[symbol_Identity_Certificate_keys[n]] = i[1]
            n += 1
        dict_Identity_Certificate_tsetmc['instrumentId'] = utils.get_id_from_url(url)
        return dict_Identity_Certificate_tsetmc, 1

    @staticmethod
    def __insert_data_to_database__(json_data):
        instrument = TseTmcInstrument(**json_data)
        instrument.full_clean()
        django_logger.info("saving to database:", instrument.instrumentId)
        instrument.save()
        return 1

# from tsetmc.models import TseTmcIdentityCertificateCrawlTask
# mytask = TseTmcIdentityCertificateCrawlTask(url="http://www.tsetmc.com/Loader.aspx?Partree=15131M&i=2400322364771558" , instrumentId="2400322364771558")
