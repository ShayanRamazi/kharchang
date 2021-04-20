from celery.schedules import crontab
from ifb.models import IFBInstrument, IFBCrawlTask
from ifb.utils import get_akhza_list_from_ifb_site, get_arad_list_from_ifb_site
from kharchang.celery import app as celery
from core.tasks import run_single_time_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@celery.task(name="ifb_daily_crawl_task")
def ifb_daily_crawl():
    logger.info("Query database")
    db_fb_instruments = list(IFBInstrument.objects.all())
    logger.info("Get akhza list")
    akhza_instruments = get_akhza_list_from_ifb_site()
    # akhza_instruments = []
    logger.info("Get arad list")
    arad_instruments = get_arad_list_from_ifb_site()
    # logger.info("Got arad list of length: " + str(len(arad_instruments)))
    # logger.info(arad_instruments[1]["url"])
    # logger.info(arad_instruments[1]["fbid"])
    logger.info("Computing non existing tasks")
    for inst in (akhza_instruments + arad_instruments):
        flag = 1
        for saved_inst in db_fb_instruments:
            if inst['fbid'] == saved_inst.fbid:
                flag = 0
                break
        if flag:
            logger.info("***************: " + inst["url"])
            ifb_crawl_task = IFBCrawlTask(
                url=inst["url"],
                max_retry=3,
                description=IFBCrawlTask.__name__ + "Automatic crawl fbid:" + inst['fbid']
            )
            ifb_crawl_task.save()
            logger.info("Adding job for fbid: " + inst['fbid'])
            run_single_time_task.delay(ifb_crawl_task.id, ifb_crawl_task.get_class_name())


celery.conf.beat_schedule = {
    'IFB daily crawl akhzas and arads': {
        'task': 'ifb_daily_crawl_task',
        # 'schedule': crontab(hour='7, 8, 9, 12, 23', minute='0,30')
        'schedule': crontab(hour='13', minute='18')
    }
}
