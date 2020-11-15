from django.urls import path

from .views import get_activities


urlpatterns = [
    path('', get_activities, name='activities'),
]
