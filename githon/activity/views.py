from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.utils import timezone
from datetime import datetime
from datetime import timedelta

import dateparser
import csv

from collections import defaultdict

from .models import Activity 
# from .service import get_reward
from . import service

# Create your views here.


def _get_date_range(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    today = timezone.now().date()

    start_date = dateparser.parse(start_date).date() if start_date else today - timedelta(days=10)
    end_date = dateparser.parse(end_date).date() if end_date else today
    return start_date, end_date


def _get_user_activities(start_date, end_date) -> dict:
    # query activitity from db
    activities = Activity.objects.filter(start_date__gte=start_date, start_date__lte=end_date) \
                                 .select_related('user__username') \
                                 .values('user__username', 'start_date', 'distance') \
                                 .order_by('-start_date')

    # group activities for each user
    user_activities = defaultdict(list)
    for activity in activities:
        username = activity['user__username']
        user_activities[username].append(activity)
    return user_activities


@login_required
def get_activities(request, *args, **kwargs):
    start_date, end_date = _get_date_range(request)
    user_activities = _get_user_activities(start_date, end_date)
    timeseries = service.get_timeseries(start_date, end_date)

    infos = []
    for user, acts in user_activities.items():
        distance_per_day = service.get_distance_per_day(acts, timeseries)
        reward = service.get_reward(distance_per_day)
        user_infos = {
            'username': user,
            'distance_per_day': distance_per_day,
            'reward': reward
        }
        infos.append(user_infos)
    context = {
        'timeseries': timeseries,
        'user_activities': infos,
        'fee': service.get_fee(),
    }

    return render(request, template_name='activities.html', context=context)


@login_required
def export_csv(request, *args, **kwargs):
    pass