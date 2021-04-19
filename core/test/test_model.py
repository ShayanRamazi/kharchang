from datetime import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from core.models import BaseTask, TestBaseClass, TestBaseTask, TestErrorBaseTask, TestBadValueBaseTask, \
    TestIOErrorBaseTask, CrawlTask, TestSuccessCrawlTask, TestParseFailInsertSuccessCrawlTask, \
    TestParseSuccessInsertFailCrawlTask, TestParseSuccessInsertBadValueCrawlTask, \
    TestParseSuccessInsertRaiseErrorCrawlTask, TestParseRaiseErrorInsertSuccessCrawlTask


class BaseModelTest(TestCase):

    def test_creation_time(self):
        simple = TestBaseClass(name="test")
        time_1 = timezone.now()
        simple.save()
        self.assertGreater(simple.created_at, time_1)
        i = TestBaseClass.objects.filter(name="test").count()
        self.assertEqual(i, 1)


class TaskTest(TestCase):

    def test_create_task(self):
        task = TestBaseTask(name="test")
        task.save()
        i = TestBaseTask.objects.filter(name="test").count()
        self.assertEqual(i, 1)

    def test_save_with_no_start_time(self):
        task_with_no_start_time = TestBaseTask(
            name="test_1",
        )
        task_with_no_start_time.save()
        task_with_no_start_time.full_clean()
        self.assertEqual(task_with_no_start_time.state, BaseTask.STATE_QUEUED)

    def test_save_with_passed_start_time(self):
        task_with_passed_start_time = TestBaseTask(
            start_time=datetime(2000, 1, 1),
            name="test_2",
        )
        task_with_passed_start_time.save()
        task_with_passed_start_time.full_clean()
        self.assertEqual(task_with_passed_start_time.state, BaseTask.STATE_QUEUED)

    def test_save_with_future_start_time(self):
        task_with_future_start_time = TestBaseTask(
            start_time=datetime(3000, 1, 1),
            name="test_3",
        )
        task_with_future_start_time.save()
        task_with_future_start_time.full_clean()
        self.assertEqual(task_with_future_start_time.state, BaseTask.STATE_WAITING)

    def test_error_task(self):
        task = TestErrorBaseTask(max_retry=2)
        self.assertEqual(task.retried, 0)
        self.assertEqual(task.max_retry, 2)
        time_1 = datetime.today()
        task.run()
        time_2 = datetime.today()
        self.assertGreaterEqual(task.started_at, time_1)
        self.assertLessEqual(task.end_at, time_2)
        self.assertEqual(task.state, task.STATE_QUEUED)
        self.assertEqual(task.retried, 1)
        time_3 = datetime.today()
        task.run()
        time_4 = datetime.today()
        task.save()
        self.assertEqual(task.retried, 2)
        self.assertGreaterEqual(task.started_at, time_3)
        self.assertLessEqual(task.end_at, time_4)
        self.assertEqual(task.state, task.STATE_ERROR)

    def test_run_value_error(self):
        task = TestBadValueBaseTask(max_retry=2)
        task.run()
        self.assertEqual(task.state, task.STATE_QUEUED)
        task.run()
        self.assertEqual(task.state, task.STATE_ERROR)

    def test_run_value_exception(self):
        task = TestIOErrorBaseTask(max_retry=2)
        task.run()
        self.assertEqual(task.state, task.STATE_QUEUED)
        task.run()
        self.assertEqual(task.state, task.STATE_ERROR)


class CrawlTaskTest(TestCase):
    def test_save_with_no_url(self):
        task_with_no_url = CrawlTask()
        self.assertRaises(ValidationError, task_with_no_url.full_clean)

    def test_save_with_bad_url(self):
        task_with_bad_url = CrawlTask(
            url="bad_url"
        )
        self.assertRaises(ValidationError, task_with_bad_url.full_clean)

    def test_save_with_good_urls(self):
        task_with_good_url = CrawlTask(
            url="https://google.com"
        )
        task_with_good_url.save()
        task_with_good_url.full_clean()

        task_with_good_url_2 = CrawlTask(
            url="https://docs.djangoproject.com/en/3.1/ref/validators/"
        )
        task_with_good_url_2.save()
        task_with_good_url_2.full_clean()

        task_with_good_url_3 = CrawlTask(
            url="http://cdn.tsetmc.com/Loader.aspx?ParTree=15131P&i=2400322364771558&d=20210404"
        )
        task_with_good_url_3.save()
        task_with_good_url_3.full_clean()

        self.assertEqual(CrawlTask.objects.count(), 3)

    def test_default_run(self):
        task = CrawlTask(
            url="google.com",
            max_retry=2

        )
        task.run()
        self.assertEqual(task.retried, 1)
        self.assertEqual(task.state, task.STATE_QUEUED)
        task.run()
        self.assertEqual(task.retried, 2)
        self.assertEqual(task.state, task.STATE_ERROR)

    def test_run_both_action_complete_successfully(self):
        task = TestSuccessCrawlTask(
            url="google.com",
            max_retry=2
        )
        task.run()
        self.assertEqual(task.state, task.STATE_DONE)
        res = task.run()
        self.assertEqual(task.state, task.STATE_DONE)
        self.assertEqual(res, -1)

    def test_run_parse_fail_insertion_success(self):
        task = TestParseFailInsertSuccessCrawlTask(
            url="google.com",
            max_retry=2
        )
        task.run()
        self.assertEqual(task.state, task.STATE_QUEUED)
        task.run()
        self.assertEqual(task.state, task.STATE_ERROR)
        res = task.run()
        self.assertEqual(res, -1)

    def test_run_parse_success_insertion_fail(self):
        task = TestParseSuccessInsertFailCrawlTask(
            url="google.com",
            max_retry=2
        )
        task.run()
        self.assertEqual(task.state, task.STATE_QUEUED)
        task.run()
        self.assertEqual(task.state, task.STATE_ERROR)
        res = task.run()
        self.assertEqual(res, -1)

    def test_run_parse_success_insertion_bad_value(self):
        task = TestParseSuccessInsertBadValueCrawlTask(
            url="google.com",
            max_retry=2
        )
        task.run()
        self.assertEqual(task.retried, 1)
        self.assertEqual(task.state, task.STATE_QUEUED)
        task.run()
        self.assertEqual(task.retried, 2)
        self.assertEqual(task.state, task.STATE_ERROR)

    def test_run_parse_success_insertion_raise_error(self):
        task = TestParseSuccessInsertRaiseErrorCrawlTask(
            url="google.com",
            max_retry=2
        )
        task.run()
        self.assertEqual(task.retried, 1)
        self.assertEqual(task.state, task.STATE_QUEUED)
        task.run()
        self.assertEqual(task.retried, 2)
        self.assertEqual(task.state, task.STATE_ERROR)

    def test_run_parse_raise_error_insertion_success(self):
        task = TestParseRaiseErrorInsertSuccessCrawlTask(
            url="google.com",
            max_retry=2
        )
        task.run()
        self.assertEqual(task.retried, 1)
        self.assertEqual(task.state, task.STATE_QUEUED)
        task.run()
        self.assertEqual(task.retried, 2)
        self.assertEqual(task.state, task.STATE_ERROR)
