import logging

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models

from core.models import BaseModel
from core.utils import parse_simple_jalali_date, georgian_to_simple_jalali_string, add_month_to_jalali_string


class IFBInstrument(BaseModel):
    ifb_url = models.URLField(max_length=300, validators=[URLValidator])
    symbolFa = models.CharField(max_length=50)
    companyFA = models.CharField(max_length=100)
    mnemonic = models.CharField(max_length=50)
    companyEN = models.CharField(max_length=100)
    isin = models.CharField(max_length=50)
    market = models.CharField(max_length=50)
    industry = models.CharField(max_length=50, null=True, blank=True)
    subIndustry = models.CharField(max_length=50)
    parValue = models.IntegerField()
    totalCount = models.IntegerField()
    listedCount = models.IntegerField()
    settlement_date = models.DateField()
    publish_date = models.DateField()
    duration = models.SmallIntegerField()
    subject = models.CharField(max_length=100)
    nominalReturnRate = models.SmallIntegerField()
    couponPeriod = models.SmallIntegerField()
    issuer = models.CharField(max_length=200)
    underWriter = models.CharField(max_length=200)
    guarantor = models.CharField(max_length=200)
    profitDistributionAgent = models.CharField(max_length=200)
    saleAgent = models.CharField(max_length=200)
    profitDistributionDates = models.ListCharField(
        base_field=models.CharField(max_length=10),
        size=40,
        max_length=(40 * 11)
    )
    profitDistributionValues = models.ListCharField(
        base_field=models.CharField(max_length=12),
        size=40,
        max_length=(40 * 13)
    )
    paymentDetailsDates = models.ListTextField(
        base_field=models.CharField(max_length=11),
    )
    paymentDetailsValues = models.ListTextField(
        base_field=models.CharField(max_length=14),
    )

    def test_payment_details_start_validity(self):
        start_date = parse_simple_jalali_date(self.paymentDetailsDates[0])
        if start_date == self.publish_date:
            return True
        raise ValidationError("Instrument payment detail start date:" +
                              georgian_to_simple_jalali_string(start_date) +
                              " is not equal to publish date:" +
                              georgian_to_simple_jalali_string(self.publish_date)
                              )

    def test_payment_details_end_validity(self):
        end_date = parse_simple_jalali_date(self.paymentDetailsDates[-1])
        if end_date == self.settlement_date:
            return True
        raise ValidationError("Instrument payment detail end date:" +
                              georgian_to_simple_jalali_string(end_date) +
                              " is not equal to settlement date:" +
                              georgian_to_simple_jalali_string(self.settlement_date)
                              )

    def test_payment_details_date_order(self):
        for i in range(len(self.paymentDetailsDates) - 1):
            date1 = parse_simple_jalali_date(self.paymentDetailsDates[i])
            date2 = parse_simple_jalali_date(self.paymentDetailsDates[i + 1])
            if date1 > date2:
                raise ValidationError("payment details dates should be ordered incrementally")
        return True

    def test_payment_details_length(self):
        if len(self.paymentDetailsDates) == len(self.paymentDetailsValues):
            return True
        raise ValidationError("payment details dates and values must have equal lengths")

    def test_profit_distribution_start_validity(self):
        publish_date_jalali_string = georgian_to_simple_jalali_string(self.publish_date)
        first_coupon_date = parse_simple_jalali_date(
            add_month_to_jalali_string(publish_date_jalali_string, self.couponPeriod))
        start_date = parse_simple_jalali_date(self.profitDistributionDates[0])
        if start_date == first_coupon_date:
            return True
        raise ValidationError("Instrument profit distribution start date:" +
                              georgian_to_simple_jalali_string(start_date) +
                              " is not equal to publish date + coupon period:" +
                              georgian_to_simple_jalali_string(first_coupon_date)
                              )

    def test_profit_distribution_end_validity(self):
        end_date = parse_simple_jalali_date(self.profitDistributionDates[-1])
        if end_date == self.settlement_date:
            return True
        raise ValidationError("Instrument profit distribution end date:" +
                              georgian_to_simple_jalali_string(end_date) +
                              " is not equal to settlement date:" +
                              georgian_to_simple_jalali_string(self.settlement_date)
                              )

    def test_profit_distribution_date_order(self):
        for i in range(len(self.profitDistributionDates) - 1):
            date1 = parse_simple_jalali_date(self.profitDistributionDates[i])
            date2 = parse_simple_jalali_date(self.profitDistributionDates[i + 1])
            if date1 > date2:
                raise ValidationError("profit distribution dates should be ordered incrementally")
        return True

    def test_profit_distribution_length(self):
        if len(self.profitDistributionDates) == len(self.profitDistributionDates):
            return True
        raise ValidationError("profit distribution dates and values must have equal lengths")

    def test_validity(self):
        return self.test_payment_details_start_validity() and \
               self.test_payment_details_end_validity() and \
               self.test_profit_distribution_start_validity() and \
               self.test_profit_distribution_end_validity() and \
               self.test_profit_distribution_date_order() and \
               self.test_payment_details_date_order() and \
               self.test_payment_details_length() and \
               self.test_profit_distribution_length

    def save(self, *args, **kwargs):
        if self.test_validity():
            return super(IFBInstrument, self).save(*args, **kwargs)
        # else:
        #     raise ValidationError("validation error")
