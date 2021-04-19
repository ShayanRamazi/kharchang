from django.core.validators import URLValidator
from rest_framework import serializers

# class TSETMCOneTimeTaskAPIValidator(forms.Form):
#     url = forms.CharField(validators=URLValidator)
#     max_retry = forms.IntegerField(min_value=1)
#     start_time = forms.DateTimeField()
from core.models import CrawlTask


class SimpleCrawlTaskSerializer(serializers.Serializer):
    url = serializers.URLField(validators=[URLValidator], required=True)
    max_retry = serializers.IntegerField(min_value=1, required=False)
    start_time = serializers.DateTimeField(required=False)
    description = serializers.CharField(required=False)


class SimpleCrawlTaskListSerializer(serializers.Serializer):
    tasks = SimpleCrawlTaskSerializer(many=True, allow_empty=False)
    # tasks = serializers.CharField(required=True)
