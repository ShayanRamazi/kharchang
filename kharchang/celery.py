import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kharchang.settings')

QUEUES_HIGH_PRIORITY = 'high_priority'
QUEUES_LOW_PRIORITY = 'low_priority'

app = Celery('kharchang')

# Using a string here meapip install django-celery-resultsns the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
app.conf.task_create_missing_queues = True

app.conf.update(
    result_expires=60,
    task_acks_late=True,
)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


@app.task(name='celery.ping')
def ping():
    # type: () -> str
    """Simple task that just returns 'pong'."""
    return 'pong'


app.conf.beat_schedule = {
    'IFB daily crawl akhzas and arads': {
        'task': 'ifb_daily_crawl_task',
        'schedule': crontab(hour='8', minute='30'),
        'options': {'queue': QUEUES_LOW_PRIORITY},
    },
    'TSE daily crawl instruments': {
        'task': 'tsetmc_daily_crawl_task',
        'schedule': crontab(hour='9,20', minute='0')
    },
    'TSE client type data': {
        'task': 'tsetmc_client_type_task',
        'schedule': crontab(day_of_week='0,1,2,3,6', hour='4,5', minute='20'),
        'options': {'queue': QUEUES_HIGH_PRIORITY},
    }
}
