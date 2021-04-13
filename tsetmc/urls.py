from django.urls import path

from tsetmc import views

urlpatterns = [
    path('api/add_one_time_task', views.TSETMCOneTimeTaskAPI.as_view(), name='tsetmc_add_one_time_tasks')
]
