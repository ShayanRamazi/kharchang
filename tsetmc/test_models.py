from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from tsetmc.models import Trade


class TradeTest(TestCase):

    def test_valid_create_trade(self):
        valid_trade = Trade(
            isin=2400322364771558,
            date=timezone.now(),
            volume=100,
            price=100
        )
        valid_trade.full_clean()
        valid_trade.save()
        self.assertIs(valid_trade.canceled, False)

    def test_invalid_create_trade(self):
        invalid_trade = Trade(
            isin=2400322364771558,
            date=timezone.now(),
            volume=-10,
            price=100
        )
        # invalid_trade.save()
        self.assertRaises(ValidationError, invalid_trade.full_clean)
