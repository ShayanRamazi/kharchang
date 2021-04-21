from django.core.validators import MinValueValidator
from django.db import models
from core.models import BaseModel


class ShareHolderDataYesterday(BaseModel):
    isin=models.CharField(max_length=20,null=False)
    name=models.CharField(max_length=150)
    percentage=models.FloatField(default=0.0,validators=[MinValueValidator(1.0)])
    amountOfShares=models.BigIntegerField(null=False)

class ShareHolderData(BaseModel):
    isin=models.CharField(max_length=20,null=False)
    name=models.CharField(max_length=150)
    percentage=models.FloatField(default=0.0,validators=[MinValueValidator(1.0)])
    amountOfShares=models.BigIntegerField(null=False)

class IntraTradeData(BaseModel):
    time=models.TimeField(null=False)
    amount=models.PositiveIntegerField(null=False,validators=[MinValueValidator(1)])
    price=models.FloatField(null=False,validators=[MinValueValidator(0.0)])
    canceled=models.BooleanField(default=False)

class IntraDayPriceData(BaseModel):
    time=models.TimeField(null=False)
    highPrice=models.FloatField(null=False,validators=[MinValueValidator(0.0)])
    lowPrice=models.FloatField(null=False,validators=[MinValueValidator(0.0)])
    openPrice=models.FloatField(null=False,validators=[MinValueValidator(0.0)])
    closePrice=models.FloatField(null=False,validators=[MinValueValidator(0.0)])

# class ClientTypeData(BaseModel):
#     numberBuyReal=
#     volumeBuyReal
#     valueBuyReal
#     priceBuyReal
#     numberBuyLegal
#     volumeBuyLegal
#     valueBuyLegal
#     priceBuyLegal
#     numberSellReal
#     volumeSellReal
#     valueSellReal
#     priceSellReal
#     numberSellRegal
#     volumeSellLegal
#     valueSellLegal
    priceSellLegal
    changeLegalToReal

