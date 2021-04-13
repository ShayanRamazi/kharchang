from django.core.validators import URLValidator
from rest_framework import serializers

# class TSETMCOneTimeTaskAPIValidator(forms.Form):
#     url = forms.CharField(validators=URLValidator)
#     max_retry = forms.IntegerField(min_value=1)
#     start_time = forms.DateTimeField()
from core.models import CrawlTask


class TSETMCOneTimeTaskAPIInSerializer(serializers.Serializer):
    url = serializers.URLField(validators=[URLValidator], required=True)
    max_retry = serializers.IntegerField(min_value=1, required=False)
    start_time = serializers.DateTimeField(required=False)
    description = serializers.CharField(required=False)

    class Meta:
        model = CrawlTask
        fields = ['url', 'max_retry', 'start_time', 'description']
        # extra_kwargs = {"max_retry": {"required": False, "allow_null": True},
        #                 "start_time": {"required": False, "allow_null": True}}

# class TSETMCOneTimeTaskAPIInSerializer(serializers.Serializer):
#     tasks = TSETMCCrawlTaskInSerializer(many=True, required=True)
#
#     def validate(self, data):
#         tasks = data['tasks']
#         if len(tasks) == 0:
#             raise serializers.ValidationError("at least one task required.")
#         return data
