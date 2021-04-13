import datetime
from time import sleep

from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse

from core.models import CrawlTask

# initialize the APIClient app
client = Client()


class TSETMCOneTimeTaskAPITest(TestCase):
    """ Test module for GET all puppies API """

    def setUp(self):
        pass

    def test_successful_post_1(self):
        # get API response
        response = client.post(reverse('tsetmc_add_one_time_tasks'),
                               {'url': 'https://google.com', 'max_retry': 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # get data from db
        task = CrawlTask.objects.get(id=response.data)
        self.assertEqual(task.state, task.STATE_ERROR)
        self.assertEqual(task.retried, 3)
        self.assertEqual(task.max_retry, 3)

    # def test_successful_post_2(self):
    #     # get API response
    #     response = client.post(reverse('tsetmc_add_one_time_tasks'),
    #                            {'tasks': [{'url': 'https://google.com', 'max_retry': 3},
    #                                       {'url': 'https://google.com'}
    #                                       ]})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     # get data from db
    #     task = CrawlTask.objects.get(id=response.data[1])
    #     self.assertEqual(task.state, task.STATE_ERROR)
    #     self.assertEqual(task.retried, 2)
    #     self.assertEqual(task.max_retry, 2)

    # def test_error_without_list(self):
    #     # get API response
    #     response = client.post(reverse('tsetmc_add_one_time_tasks'), {'url': 'https://google.com'})
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_empty_json(self):
        # get API response
        response = client.post(reverse('tsetmc_add_one_time_tasks'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_without_url_entry(self):
        # get API response
        response = client.post(reverse('tsetmc_add_one_time_tasks'),
                               {'url2': 'https://google.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        i = CrawlTask.objects.count()
        self.assertEqual(i, 0)

    def test_error_bad_url(self):
        # get API response
        response = client.post(reverse('tsetmc_add_one_time_tasks'),
                               {'url': 'google@com.'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        i = CrawlTask.objects.count()
        self.assertEqual(i, 0)

    def test_error_bad_max_retry(self):
        # get API response
        response = client.post(reverse('tsetmc_add_one_time_tasks'),
                               {'url': 'https://google.com', 'max_retry': 0})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_bad_max_retry_2(self):
        # get API response
        response = client.post(reverse('tsetmc_add_one_time_tasks'),
                               {'url': 'https://google.com', 'max_retry': 12.5})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_string_max_retry(self):
        # get API response
        response = client.post(reverse('tsetmc_add_one_time_tasks'), {'url': 'https://google.com', 'max_retry': "3"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_string_start_at_future(self):
        # get API response
        d = datetime.datetime.now() + datetime.timedelta(seconds=10)
        response = client.post(reverse('tsetmc_add_one_time_tasks'),
                               {'url': 'https://google.com',
                                'start_time': d,
                                'max_retry': 1
                                })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = CrawlTask.objects.get(id=response.data)
        self.assertEqual(task.state, task.STATE_WAITING)
        sleep(2)
        task.refresh_from_db()
        self.assertEqual(task.state, task.STATE_WAITING)
        self.assertEqual(task.retried, 0)

    def test_string_start_at_passed(self):
        # get API response
        d = datetime.datetime.today()
        response = client.post(reverse('tsetmc_add_one_time_tasks'),
                               {'url': 'https://google.com', 'start_time': d.isoformat(), 'max_retry': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = CrawlTask.objects.get(id=response.data)
        self.assertEqual(task.state, task.STATE_ERROR)
        self.assertEqual(task.retried, 1)

    def test_just_input_validation(self):
        # get API response
        response = client.post(reverse('tsetmc_add_one_time_tasks'),
                               {'url': 'https://google.com',
                                'max_retry': 1,
                                'start_time': datetime.datetime.now(),
                                'description': "test description",
                                })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    # def test_temp_1(self):
    #     # get API response
    #     response = client.post(reverse('tsetmc_add_one_time_tasks'),
    #                            {'url': 'google.com', 'max_retry': 0})
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_temp_2(self):
    #     # get API response
    #     response = client.post(reverse('tsetmc_add_one_time_tasks'),
    #                            {'url2': 'https://google.com', 'max_retry': 1})
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
