from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.utils import timezone
from datetime import datetime
from datetime import timedelta

import dateparser

from collections import defaultdict

from .models import Activity 
# from .service import get_reward
from . import service

# Create your views here.


def get_timeseries(start_date: datetime, end_date: datetime) -> list:
    pass


def get_reward(activities: list, start_date: datetime, end_date: datetime):
    pass


def _get_date_range(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    today = timezone.now().date()

    start_date = dateparser.parse(start_date).date() if start_date else today - timedelta(days=10)
    end_date = dateparser.parse(end_date).date() if end_date else today
    return start_date, end_date


@login_required
def get_activities(request, *args, **kwargs):
    start_date, end_date = _get_date_range(request)

    activities = Activity.objects.filter(start_date__gte=start_date, start_date__lte=end_date) \
                                 .select_related('user__username') \
                                 .values('user__username', 'start_date', 'distance') \
                                 .order_by('-start_date')

    user_activities = defaultdict(list)
    for activity in activities:
        username = activity['user__username']
        user_activities[username].append(activity)

    timeseries = service.get_timeseries(start_date, end_date)

    infos = []
    for user, acts in user_activities.items():
        user_infos = {
            'username': user,
            'reward': service.get_reward(acts),
            'distance_per_day': service.get_distance_per_day(acts, timeseries)
        }
        infos.append(user_infos)
    context = {
        'timeseries': timeseries,
        'user_activities': infos
    }

    return render(request, template_name='activities.html', context=context)
