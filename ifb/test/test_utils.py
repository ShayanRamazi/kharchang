from unittest import TestCase

from ifb.utils import get_fbid_from_url


class UrlHandlerTest(TestCase):

    def test_get_id_from_url(self):
        url = "hasdfsdf?id=2314315315masdf"
        id = "2314315315"
        self.assertEqual(get_fbid_from_url(url), id)
        url_2 = "sdjfbashkdfvbiuio2jr2314jbsf"
        self.assertEqual(get_fbid_from_url(url_2), None)
