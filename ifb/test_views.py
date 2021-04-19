import datetime
import json
from time import sleep

from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse

from core.models import CrawlTask

# initialize the APIClient app
from ifb.models import IFBCrawlTask

client = Client()


class IFBOneTimeTaskAPITest(TestCase):

    def test_task_added(self):
        response = client.post(reverse('ifb_add_one_time_tasks'),
                               data={"tasks": [{'url': 'https://google.com', 'max_retry': 3}]}
                               , content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # get data from db
        task = IFBCrawlTask.objects.get(id=response.data[0])
        self.assertEqual(task.state, task.STATE_ERROR)
        self.assertEqual(task.retried, 3)
        self.assertEqual(task.max_retry, 3)