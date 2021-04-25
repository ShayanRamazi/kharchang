from celery.schedules import crontab

from core.utils import get_georgian_date_as_string_without_separator
from kharchang.celery import app as celery
from core.tasks import run_single_time_task
from celery.utils.log import get_task_logger

from tsetmc.models import TseTmcCrawlTask
from tsetmc.utils import get_instrument_id_list_from_tsetmc, get_instrument_dates_to_crawl

logger = get_task_logger(__name__)
base_url = 'http://cdn.tsetmc.com/Loader.aspx?ParTree=15131P&i=%s&d=%s'


@celery.task(name="tsetmc_daily_crawl_task")
def ifb_daily_crawl():
    logger.info("Get Instruments list")
    # get tse instruments list
    tse_instrument_id_list = get_instrument_id_list_from_tsetmc()
    for instrument_id in tse_instrument_id_list:
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
                    add_tsetmc_task(instrument_id, temp_date)
                dates_list_index += 1
                if dates_list_index >= len(dates_list):
                    break
                temp_date = dates_list[dates_list_index]

        for i in range(dates_list_index, len(dates_list)):
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
                    + "date: " + get_georgian_date_as_string_without_separator(date)
    )
    new_task.save()
    logger.info("Adding job for tsetmc_id: " + instrument_id
                + "date: " + get_georgian_date_as_string_without_separator(date))
    run_single_time_task.delay(new_task.id, new_task.get_class_name())


celery.conf.beat_schedule = {
    'TSE daily crawl akhzas and arads': {
        'task': 'tsetmc_daily_crawl_task',
        'schedule': crontab(hour='13', minute='00')
    }
}
