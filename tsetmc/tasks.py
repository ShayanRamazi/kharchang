from celery.schedules import crontab

from core.utils import get_georgian_date_as_string_without_separator
from ifb.models import IFBInstrument, IFBCrawlTask
from ifb.utils import get_akhza_list_from_ifb_site, get_arad_list_from_ifb_site
from kharchang.celery import app as celery
from core.tasks import run_single_time_task
from celery.utils.log import get_task_logger

from tsetmc.models import TseTmcCrawlTask
from tsetmc.utils import get_instrument_list_from_tsetmc, get_instrument_dates_to_crawl

logger = get_task_logger(__name__)
base_url = 'http://cdn.tsetmc.com/Loader.aspx?ParTree=15131P&i=%s&d=%s'


@celery.task(name="tsetmc_daily_crawl_task")
def ifb_daily_crawl():
    logger.info("Query database")
    # get tse instruments list
    tse_instrument_list = get_instrument_list_from_tsetmc()
    for instrument in tse_instrument_list:
        # get dates to crawl for each instrument in descending order
        dates_list = get_instrument_dates_to_crawl(instrument['instrumentId'])
        if len(dates_list) == 0:
            logger.info("empty dates list to crawl for id:", instrument['instrumentId'])
            continue
        # get all tsetmc_crawl_tasks for this instrument with state D and Q ordered by date descending
        all_d_q_tse_tasks_for_instrument = TseTmcCrawlTask.objects.filter(
            id=instrument['instrumentId'],
            state_in=['Q', 'D']) \
            .order_by('-date_to_crawl')

        dates_list_index = 0
        for task in all_d_q_tse_tasks_for_instrument:
            temp_date = dates_list[dates_list_index]
            while temp_date >= task.date_to_crawl:
                if temp_date != task.date_to_crawl:
                    add_tsetmc_task(instrument['instrumentId'], temp_date)
                dates_list_index += 1
                temp_date = dates_list[dates_list_index]

        for i in range(dates_list_index, len(dates_list)):
            add_tsetmc_task(instrument['instrumentId'], dates_list[i])


def add_tsetmc_task(instrument_id, date):
    new_task = TseTmcCrawlTask(
        instrumentId=instrument_id,
        date=date,
        max_retry=3,
        url=base_url % (
            instrument_id, get_georgian_date_as_string_without_separator(temp_date)),
        description=IFBCrawlTask.__name__ +
                    "Automatic crawl tse id:" + instrument_id
                    + "date: " + get_georgian_date_as_string_without_separator(date)
    )
    new_task.save()
    logger.info("Adding job for tsetmc_id: " + instrument_id
                + "date: " + get_georgian_date_as_string_without_separator(date))
    run_single_time_task.delay(new_task.id, new_task.get_class_name())


celery.conf.beat_schedule = {
    'IFB daily crawl akhzas and arads': {
        'task': 'tse_daily_crawl_task',
        'schedule': crontab(hour='19', minute='0')
    }
}
