import uuid
from datetime import datetime

import dateutil.parser
from django.core.validators import URLValidator
from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def get_class_name(self):
        return self.__class__.__name__


class BaseTask(BaseModel):
    class Meta:
        abstract = True

    STATE_WAITING = "W"
    STATE_QUEUED = "Q"
    STATE_RUNNING = "R"
    STATE_ERROR = "E"
    STATE_DONE = "D"
    TASK_STATES = [
        (STATE_WAITING, "Waiting"),
        (STATE_QUEUED, "Queued"),
        (STATE_RUNNING, "Running"),
        (STATE_ERROR, "Exited with error"),
        (STATE_DONE, "Done, completed"),
    ]

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    start_time = models.DateTimeField(null=True, blank=True, default=None)
    started_at = models.DateTimeField(null=True, blank=True, default=None)
    end_at = models.DateTimeField(null=True, blank=True, default=None)
    state = models.CharField(max_length=2, null=False, blank=False, default=None)
    description = models.CharField(max_length=200, null=True, blank=True, default=None)
    retried = models.SmallIntegerField(null=True, blank=True, default=0)
    max_retry = models.SmallIntegerField(default=2, null=False, blank=False)

    def run(self):
        """
        return 1 if successful and 0 otherwise
        returns -1 if task has state DONE or ERROR
        """
        if self.state == self.STATE_DONE or self.state == self.STATE_ERROR:
            return -1
        self.started_at = datetime.today()
        self.state = self.STATE_RUNNING
        self.retried += 1
        self.save()
        try:
            flag = self.__run__()
        except Exception as e:
            flag = 0
        # if flag != 0 and flag != 1:
        #     raise ValueError("__run__ method should just return 0 or 1 values")
        self.end_at = datetime.today()
        if flag == 1:
            self.state = self.STATE_DONE
        else:
            if self.retried < self.max_retry:
                self.state = self.STATE_QUEUED
            else:
                self.state = self.STATE_ERROR
        self.save()
        return flag

    def __run__(self):
        """
        Should return 1 if successful and 0 otherwise
        """
        pass

    def save(self, *args, **kwargs):
        if self.state is None:
            if self.start_time is not None:
                if isinstance(self.start_time, str):
                    self.start_time = dateutil.parser.isoparse(self.start_time)
                if self.start_time > datetime.today():
                    self.state = self.STATE_WAITING
                else:
                    self.state = self.STATE_QUEUED
            else:
                self.state = self.STATE_QUEUED
        return super(BaseTask, self).save(*args, **kwargs)


class CrawlTask(BaseTask):
    url = models.URLField(max_length=200, validators=[URLValidator], default=None)

    @staticmethod
    def __parse_url__(url):
        """
        returning data in self.url as a json
        if error occurred return 0
        """
        pass

    @staticmethod
    def __insert_data_to_database__(json_data):
        """
        Using json returned by parse_url method to insert useful data into app models
        if error occurred return 0 else return 1
        """
        pass

    def __run__(self):
        """
        Here we have to use two functions
        1- parse url which parses the url and returns a json of data
        2- a function which imports returned json to the database using django model
        """
        try:
            parsed_data = self.__parse_url__(self.url)
        except Exception as e:
            print(e)
            parsed_data = 0
        if parsed_data != 1:
            flag = 0
        else:
            try:
                insertion_result = self.__insert_data_to_database__(parsed_data)
            except Exception as e:
                print(e)
                insertion_result = 0
            if insertion_result != 0 and insertion_result != 1:
                flag = 0
            else:
                flag = insertion_result
        return flag


#################################################
#########        TEST CLASSES        ############
#################################################

# TODO: Using mongo db I was able to embed most of these models into the test case itself
#  and the models were declared inside functions testing them. There were some models which we
#  wanted to query on them, so we've had created a model named testhelper to declare these models
#  in that project and do not include it in installed app in main settings. None of these techniques
#  works with postgresql!!! How to make these models more testy!?!


class TestBaseClass(BaseModel):
    name = models.CharField(max_length=10)


class TestBaseTask(BaseTask):
    name = models.CharField(max_length=10)


class TestSuccessBaseCase(TestBaseTask):
    def __run__(self):
        return 1

    class Meta:
        proxy = True


class TestErrorBaseTask(TestBaseTask):
    def __run__(self):
        return 0

    class Meta:
        proxy = True


class TestBadValueBaseTask(TestSuccessBaseCase):
    def __run__(self):
        return -1

    class Meta:
        proxy = True


class TestIOErrorBaseTask(TestSuccessBaseCase):
    def __run__(self):
        raise IOError("test error")

    class Meta:
        proxy = True


class TestCrawlTask(CrawlTask):
    name = models.CharField(max_length=10, null=True, blank=True)


class TestSuccessCrawlTask(TestCrawlTask):

    @staticmethod
    def __parse_url__(url):
        return 1

    @staticmethod
    def __insert_data_to_database__(json_data):
        return 1

    class Meta:
        proxy = True


class TestParseFailInsertSuccessCrawlTask(TestCrawlTask):

    @staticmethod
    def __parse_url__(url):
        return 0

    @staticmethod
    def __insert_data_to_database__(json_data):
        return 1

    class Meta:
        proxy = True


class TestParseSuccessInsertFailCrawlTask(TestCrawlTask):

    @staticmethod
    def __parse_url__(url):
        return 1

    @staticmethod
    def __insert_data_to_database__(json_data):
        return 0

    class Meta:
        proxy = True


class TestParseSuccessInsertBadValueCrawlTask(TestCrawlTask):

    @staticmethod
    def __parse_url__(url):
        return 1

    @staticmethod
    def __insert_data_to_database__(json_data):
        return 2

    class Meta:
        proxy = True


class TestParseSuccessInsertRaiseErrorCrawlTask(TestCrawlTask):

    @staticmethod
    def __parse_url__(url):
        return 1

    @staticmethod
    def __insert_data_to_database__(json_data):
        raise ConnectionError("connection error")

    class Meta:
        proxy = True


class TestParseRaiseErrorInsertSuccessCrawlTask(TestCrawlTask):

    @staticmethod
    def __parse_url__(url):
        raise TimeoutError("timeout error")

    @staticmethod
    def __insert_data_to_database__(json_data):
        raise 1

    class Meta:
        proxy = True
