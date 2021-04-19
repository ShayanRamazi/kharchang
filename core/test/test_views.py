import datetime
from time import sleep

from django.test import TestCase
from rest_framework import status

from core.models import CrawlTask
from core.views import one_time_task


class OneTimeTaskTest(TestCase):

    def test_single_task(self):
        data = {'tasks':
                    [{'url': 'https://google.com',
                      'max_retry': 3,
                      'start_time': datetime.datetime.now(),
                      'description': "test description",
                      }, ]}
        response = one_time_task(data, CrawlTask.__name__)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = CrawlTask.objects.get(id=response.data[0])
        self.assertEqual(task.state, task.STATE_ERROR)
        self.assertEqual(task.retried, 3)
        self.assertEqual(task.max_retry, 3)

    def test_multiple_tasks(self):
        data = {'tasks':
                    [{'url': 'https://google.com', 'max_retry': 3},
                     {'url': 'https://google.com'}]}
        response = one_time_task(data, CrawlTask.__name__)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = CrawlTask.objects.get(id=response.data[1])
        self.assertEqual(task.state, task.STATE_ERROR)
        self.assertEqual(task.retried, 2)
        self.assertEqual(task.max_retry, 2)

    def test_empty_task_list(self):
        data = {'tasks': []}
        response = one_time_task(data, CrawlTask.__name__)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_without_url(self):
        data = {'tasks':
                    [{'url2': 'https://google.com', 'max_retry': 3}, ]}
        response = one_time_task(data, CrawlTask.__name__)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bad_url(self):
        data = {'tasks':
                    [{'url': 'https://google@com', 'max_retry': 3}, ]}
        response = one_time_task(data, CrawlTask.__name__)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bad_max_retry(self):
        data = {'tasks':
                    [{'url': 'https://google.com', 'max_retry': 0}, ]}
        response = one_time_task(data, CrawlTask.__name__)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_string_max_retry(self):
        data = {'tasks':
                    [{'url': 'https://google.com', 'max_retry': '3'}, ]}
        response = one_time_task(data, CrawlTask.__name__)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = CrawlTask.objects.get(id=response.data[0])
        self.assertEqual(task.state, task.STATE_ERROR)
        self.assertEqual(task.retried, 3)
        self.assertEqual(task.max_retry, 3)

    def test_string_start_at_future(self):
        d = datetime.datetime.now() + datetime.timedelta(seconds=10)
        data = {'tasks':
            [{
                'url': 'https://google.com',
                'start_time': d,
                'max_retry': 1},
            ]}
        response = one_time_task(data, CrawlTask.__name__)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = CrawlTask.objects.get(id=response.data[0])
        self.assertEqual(task.state, task.STATE_WAITING)
        sleep(1)
        task.refresh_from_db()
        self.assertEqual(task.state, task.STATE_WAITING)
        self.assertEqual(task.retried, 0)

    def test_string_start_at_passed(self):
        d = datetime.datetime.now()
        data = {'tasks':
            [{
                'url': 'https://google.com',
                'start_time': d,
                'max_retry': 1},
            ]}
        response = one_time_task(data, CrawlTask.__name__)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = CrawlTask.objects.get(id=response.data[0])
        self.assertEqual(task.state, task.STATE_ERROR)
        self.assertEqual(task.retried, 1)
