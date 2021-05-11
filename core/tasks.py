from datetime import datetime

from django.contrib.contenttypes.models import ContentType

from core.models import BaseTask
from kharchang.celery import app as celery
from celery.utils.log import get_task_logger
from celery.schedules import crontab
from django.apps import apps

logger = get_task_logger(__name__)


@celery.task(name="simple_task")
def run_single_time_task(task_id, task_class_name, queue_name="celery"):
    logger.info(task_id)
    z = ContentType.objects.get(model=task_class_name.lower())
    TaskClass = apps.get_model(z.app_label, task_class_name)
    task = TaskClass.objects.get(id=task_id)
    if task.state == BaseTask.STATE_ERROR or task.state == BaseTask.STATE_DONE:
        return -1
    if task.state == BaseTask.STATE_RUNNING:
        return -1
    if task.state == BaseTask.STATE_WAITING and task.start_time > datetime.now():
        return -1
    if task.state == BaseTask.STATE_WAITING and task.start_time <= datetime.now():
        task.state = BaseTask.STATE_QUEUED
    task.save()
    res = task.run()
    if res == 1:
        return 1
    elif res == 0 and task.retried < task.max_retry:
        run_single_time_task.apply_async(queue=queue_name, args=(task.id, task_class_name, queue_name))
        return 0
    elif res == 0 or -1:
        return 0
    else:
        raise ValueError("Task run should return -1,0 or 1")

# @celery.task(name="check_task")
# def check():
#     print('I am checking your stuff')
#
#
# celery.conf.beat_schedule = {
#     'run-me-every-ten-seconds': {
#         'task': 'check_task',
#         'schedule': 10.0
#     }
# }
