# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
#
# from core.models import CrawlTask
# from core.tasks import run_single_time_task
# from tsetmc.serializers import TSETMCOneTimeTaskAPIInSerializer
#
#
# class TSETMCOneTimeTaskAPI(APIView):
#
#     @staticmethod
#     def post(request, *args, **kw):
#         in_serial = TSETMCOneTimeTaskAPIInSerializer(data=request.data)
#         if in_serial.is_valid():
#             task = CrawlTask(**in_serial.data)
#             task.save()
#             run_single_time_task.delay(task.id, task.get_class_name())
#             response = Response(task.id, status=status.HTTP_200_OK)
#         else:
#             response = Response(in_serial.errors, status=status.HTTP_400_BAD_REQUEST)
#         return response
#
#     # @staticmethod
#     # def get(request, *args, **kw):
#     #     # get_arg1 = request.GET.get('arg1', None)
#     #     # get_arg2 = request.GET.get('arg2', None)
#     #
#     #     # Any URL parameters get passed in **kw
#     #     sample_task = CrawlTask(
#     #         url="goolge.com",
#     #         max_retry=2
#     #     )
#     #     sample_task.save()
#     #     run_single_time_task.delay(sample_task.id, "CrawlTask")
#     #     response = Response(sample_task.id, status=status.HTTP_200_OK)
#     #     return response
