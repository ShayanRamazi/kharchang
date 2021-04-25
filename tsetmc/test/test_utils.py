import datetime
from unittest import TestCase
import kharchang.settings

from tsetmc.utils import get_instrument_id_list_from_tsetmc, get_instrument_dates_to_crawl

kharchang.settings.configure()

class TseListsTest(TestCase):

    def test_get_instrument_id_list_from_tsetmc(self):
        ids = get_instrument_id_list_from_tsetmc()
        foolad_id = "46348559193224090"
        self.assertIn(foolad_id, ids)

    def test_get_instrument_dates_to_crawl(self):
        foolad_id = "46348559193224090"
        dates = get_instrument_dates_to_crawl(foolad_id)
        self.assertGreater(len(dates), 3103)
        self.assertGreater(dates[0], dates[1])
        self.assertGreater(dates[0], dates[-1])
        self.assertGreater(dates[-2], dates[-1])
