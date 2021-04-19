from django.urls import path

from ifb import views

urlpatterns = [
    path('api/add_one_time_task', views.IFBOneTimeTaskAPI.as_view(), name='ifb_add_one_time_tasks')
]
