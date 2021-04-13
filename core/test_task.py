from datetime import datetime
from django.test import TestCase

from core.models import CrawlTask, TestSuccessCrawlTask
from .tasks import run_single_time_task


class SimpleTaskTest(TestCase):

    # DONE: TODO: test celery workers: tests are run with celery eager option

    # def test_default_crawl_task_with_inner_delay(self):
    #     crawl_task = CrawlTask(
    #         url="google.com",
    #         max_retry=2
    #     )
    #     crawl_task.save()
    #     run_single_time_task(crawl_task.id, "CrawlTask")
    #     crawl_task.refresh_from_db()
    #     # crawl_task = CrawlTask.objects.get(id=crawl_task.id)
    #     # self.assertEqual(crawl_task.state, CrawlTask.STATE_ERROR)
    #     self.assertEqual(crawl_task.retried, 1)
    #     self.assertEqual(crawl_task.state, crawl_task.STATE_QUEUED)

    def test_default_crawl_task(self):
        crawl_task = CrawlTask(
            url="google.com",
            max_retry=2
        )
        crawl_task.save()
        run_single_time_task(crawl_task.id, "CrawlTask")
        crawl_task.refresh_from_db()
        # crawl_task = CrawlTask.objects.get(id=crawl_task.id)
        # self.assertEqual(crawl_task.state, CrawlTask.STATE_ERROR)
        self.assertEqual(crawl_task.state, crawl_task.STATE_ERROR)
        self.assertEqual(crawl_task.retried, 2)

    def test_success(self):
        crawl_task = TestSuccessCrawlTask(
            url="google.com",
            max_retry=2
        )
        crawl_task.save()
        run_single_time_task(crawl_task.id, crawl_task.get_class_name())
        crawl_task.refresh_from_db()
        # crawl_task = CrawlTask.objects.get(id=crawl_task.id)
        # self.assertEqual(crawl_task.state, CrawlTask.STATE_ERROR)
        self.assertEqual(crawl_task.retried, 1)
        self.assertEqual(crawl_task.state, crawl_task.STATE_DONE)

    def test_future_task(self):
        crawl_task = CrawlTask(
            url="google.com",
            max_retry=2,
            start_time=datetime(3000, 1, 1)
        )
        crawl_task.save()
        run_single_time_task(crawl_task.id, "CrawlTask")
        crawl_task.refresh_from_db()
        # crawl_task = CrawlTask.objects.get(id=crawl_task.id)
        # self.assertEqual(crawl_task.state, CrawlTask.STATE_ERROR)
        self.assertEqual(crawl_task.retried, 0)
        self.assertEqual(crawl_task.state, crawl_task.STATE_WAITING)
