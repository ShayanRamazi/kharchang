import datetime
import requests
import redis
import dateutil.parser
from django.db import transaction

from core.utils import get_georgian_date_as_string_without_separator
from kharchang import settings
from kharchang.celery import app as celery
from core.tasks import run_single_time_task
from celery.utils.log import get_task_logger

from tsetmc.models import TseTmcCrawlTask, MiddleDayClientTypeData
from tsetmc.utils import get_instrument_id_list_from_tsetmc, get_instrument_dates_to_crawl

logger = get_task_logger(__name__)
base_url = 'http://cdn.tsetmc.com/Loader.aspx?ParTree=15131P&i=%s&d=%s'
client_type_url = "http://www.tsetmc.com/tsev2/data/ClientTypeAll.aspx"

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                   port=settings.REDIS_PORT, db=0)
CLIENT_TYPE_REDIS_PREFIX = "ctd__"


@celery.task(name="tsetmc_daily_crawl_task")
def tsetmc_daily_crawl():
    task_counter = 0
    logger.info("Get Instruments list")
    # get tse instruments list
    tse_instrument_id_list = get_instrument_id_list_from_tsetmc()
    for instrument_id in tse_instrument_id_list:
        if task_counter > 20000:
            logger.info("More than 20000 tasks added! I think that's enough for today!")
            return
        logger.info("Get date list for " + str(instrument_id))
        # get dates to crawl for each instrument in descending order
        dates_list = get_instrument_dates_to_crawl(instrument_id)
        if len(dates_list) == 0:
            logger.info("empty dates list to crawl for id:", instrument_id)
            continue
        # get all tsetmc_crawl_tasks for this instrument with state D and Q ordered by date descending
        logger.info("query database for " + str(instrument_id))
        all_d_q_tse_tasks_for_instrument = TseTmcCrawlTask.objects.filter(
            instrumentId=instrument_id,
            state__in=['Q', 'D']) \
            .order_by('-dateToCrawl')

        dates_list_index = 0
        logger.info("adding tasks")
        for task in all_d_q_tse_tasks_for_instrument:
            temp_date = dates_list[dates_list_index]
            while temp_date >= task.dateToCrawl:
                if temp_date != task.dateToCrawl:
                    task_counter += 1
                    add_tsetmc_task(instrument_id, temp_date)
                dates_list_index += 1
                if dates_list_index >= len(dates_list):
                    break
                temp_date = dates_list[dates_list_index]

        for i in range(dates_list_index, len(dates_list)):
            task_counter += 1
            add_tsetmc_task(instrument_id, dates_list[i])


def add_tsetmc_task(instrument_id, date):
    new_task = TseTmcCrawlTask(
        instrumentId=instrument_id,
        dateToCrawl=date,
        max_retry=3,
        url=base_url % (
            instrument_id, get_georgian_date_as_string_without_separator(date)),
        description=TseTmcCrawlTask.__name__ +
                    "Automatic crawl tse id:" + instrument_id
                    + " date: " + get_georgian_date_as_string_without_separator(date)
    )
    new_task.save()
    logger.info("Adding job for tsetmc_id: " + instrument_id
                + "date: " + get_georgian_date_as_string_without_separator(date))
    run_single_time_task.delay(new_task.id, new_task.get_class_name())


@celery.task(name="tsetmc_client_type_task")
def tsetmc_client_type_crawl():
    now = datetime.datetime.now()
    #  TODO: check this condition
    # logger.inf(str(now.hour)+":"+str(now.minute)+":"+str(now.seconds))
    if now.hour > 14 or now.hour < 8:
        return
    resp = requests.get(client_type_url)
    now_iso_format = now.isoformat()
    for client_type_string in resp.text.split(";"):
        parts = client_type_string.split(",")
        if len(parts) != 9:
            continue
        temp_value = redis_instance.get(CLIENT_TYPE_REDIS_PREFIX + parts[0])
        temp_value = temp_value if temp_value else b""
        last_5_values = temp_value.decode().split(";")
        if client_type_string in last_5_values:
            continue
        last_5_values.append(client_type_string)
        if len(last_5_values) > 5:
            last_5_values = last_5_values[1:6]
        last_5_values_string = ";".join(last_5_values)
        redis_instance.set(CLIENT_TYPE_REDIS_PREFIX + parts[0], last_5_values_string)
        add_single_client_type_data.delay(client_type_string, now_iso_format)


@celery.task(name="tsetmc_add_single_client_type_task")
def add_single_client_type_data(client_type_string, time_iso_format):
    parts = client_type_string.split(",")
    date_time = dateutil.parser.parse(time_iso_format)
    client_type_data = MiddleDayClientTypeData()
    client_type_data.date = date_time.date()
    client_type_data.time = date_time.time()
    client_type_data.instrumentId = parts[0]
    client_type_data.numberBuyReal = parts[1]
    client_type_data.numberBuyLegal = parts[2]
    client_type_data.volumeBuyReal = parts[3]
    client_type_data.volumeBuyLegal = parts[4]
    client_type_data.numberSellReal = parts[5]
    client_type_data.numberSellLegal = parts[6]
    client_type_data.volumeSellReal = parts[7]
    client_type_data.volumeSellLegal = parts[8]
    client_type_data.save()
