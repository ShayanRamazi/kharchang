from django.core.validators import MinValueValidator
from django.db import models

from core.models import BaseModel


# A class for saving IntraTradeData
class Trade(BaseModel):
    isin = models.CharField(max_length=20, null=False)
    date = models.DateTimeField(null=False)
    volume = models.PositiveIntegerField(null=False, validators=[MinValueValidator(1)])
    price = models.PositiveIntegerField(null=False, validators=[MinValueValidator(1)])
    canceled = models.BooleanField(default=False)
