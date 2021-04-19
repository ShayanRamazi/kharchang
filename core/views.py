from core.serializers import SimpleCrawlTaskListSerializer
from django.contrib.contenttypes.models import ContentType
from core.tasks import run_single_time_task
from django.apps import apps
from rest_framework.response import Response
from rest_framework import status


def one_time_task(tasks_dict, task_class_name):
    z = ContentType.objects.get(model=task_class_name.lower())
    TaskClass = apps.get_model(z.app_label, task_class_name)
    in_serial = SimpleCrawlTaskListSerializer(data=tasks_dict)
    if in_serial.is_valid():
        tasks = in_serial.data['tasks']
        task_ids = []
        for task in tasks:
            task = TaskClass(**task)
            task.save()
            run_single_time_task.delay(task.id, task.get_class_name())
            task_ids.append(task.id)
        response = Response(task_ids, status=status.HTTP_200_OK)
    else:
        response = Response(in_serial.errors, status=status.HTTP_400_BAD_REQUEST)
    return response