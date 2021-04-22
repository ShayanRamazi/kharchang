from celery.schedules import crontab
from ifb.models import IFBInstrument, IFBCrawlTask
from ifb.utils import get_akhza_list_from_ifb_site, get_arad_list_from_ifb_site
from kharchang.celery import app as celery
from core.tasks import run_single_time_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@celery.task(name="tsetmc_daily_crawl_task")
def ifb_daily_crawl():
    logger.info("Query database")
    # get tse instruments list
        # get days to crawl for each instrument
            # for each instrument for each day which is not crawled and is not in the queue add a task
                # check whether there exist a task with state D or Q for this instrument and date combination
                # if not add a task for that
    


celery.conf.beat_schedule = {
    'IFB daily crawl akhzas and arads': {
        'task': 'tse_daily_crawl_task',
        'schedule': crontab(hour='19', minute='0')
    }
}
