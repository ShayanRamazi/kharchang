import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.models import CrawlTask
from core.serializers import SimpleCrawlTaskSerializer, SimpleCrawlTaskListSerializer
from core.tasks import run_single_time_task
from core.views import one_time_task
from ifb.models import IFBCrawlTask


class IFBOneTimeTaskAPI(APIView):

    @staticmethod
    def post(request, *args, **kw):
        return one_time_task(request.data, IFBCrawlTask.__name__)
        # in_serial = SimpleCrawlTaskListSerializer(data=request.data)
        # if in_serial.is_valid():
        #     tasks = in_serial.data['tasks']
        #     task_ids = []
        #     for task in tasks:
        #         task = IFBCrawlTask(**task)
        #         task.save()
        #         run_single_time_task.delay(task.id, task.get_class_name())
        #         task_ids.append(task.id)
        #     response = Response(task_ids, status=status.HTTP_200_OK)
        # else:
        #     response = Response(in_serial.errors, status=status.HTTP_400_BAD_REQUEST)
        # return response
