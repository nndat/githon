from django.contrib.auth import get_user_model
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save

from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.models import SocialToken

from datetime import datetime, timedelta
from datetime import date

import requests
import dateparser

from .models import Activity


User = get_user_model()


def update_token() -> None:
    users = User.objects.all()
    for user in users:
        update_token_for(user)


def update_token_for(user: User, user_token=None):
    if not user_token:
        user_token = user.socialaccount_set.first().socialtoken_set.first()

    refresh_token = user_token.token_secret
    strava_info = SocialApp.objects.filter(provider='strava').first()
    params = {
        'client_id': strava_info.client_id,
        'client_secret': strava_info.secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    endpoint = 'https://www.strava.com/oauth/token'
    response = requests.post(endpoint, data=params).json()
    if 'access_token' not in response:
        return None

    user_token.token = response['access_token']
    user_token.token_secret = response['refresh_token']
    user_token.expires_at = datetime.fromtimestamp(response['expires_at']) # TODO: Fix timezone warning
    user_token.save()
    return user_token


def _get_access_token(user):
    try:
        token_info = user.socialaccount_set.first().socialtoken_set.first()
        if token_info.expires_at < timezone.now():
            token_info = update_token_for(user, user_token=token_info)
        return token_info.token
    except AttributeError:
        pass


def update_activities(start_date: date = None, end_date: date = None) -> None:
    users = User.objects.all()
    for u in users:
        activities = get_activities_for(u, start_date=start_date, end_date=end_date)
        insert_activities(activities)


def update_activities_for(user: User, start_date: date = None) -> None:
    activities = get_activities_for(user, start_date=start_date)
    insert_activities(activities)


def insert_activities(activities: list) -> []:
    activities = [Activity(**act) for act in activities]
    Activity.objects.bulk_create(activities, ignore_conflicts=True)


def get_activities_for(user: User, start_date: date = None, end_date: date = None, page: int = 1) -> list:
    access_token = _get_access_token(user)
    start_date = start_date or timezone.now()

    if not access_token:
        return []

    end_point = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {'page': page}
    res = requests.get(end_point, headers=headers, params=params)
    activities = []

    for activity in res.json():
        if activity['flagged']:
            continue
        activities.append({
            'id': activity['id'],
            'name': activity['name'],
            'distance': activity['distance'],
            'moving_time': activity['moving_time'],
            'elapsed_time': activity['elapsed_time'],
            'total_elevation_gain': activity['total_elevation_gain'],
            'activity_type': activity['type'],
            'start_date': dateparser.parse(activity['start_date']).date(),
            'start_date_local': dateparser.parse(activity['start_date_local']),
            'average_speed': activity['average_speed'],
            'max_speed': activity['max_speed'],
            'elev_high': activity['elev_high'],
            'elev_low': activity['elev_low'],
            'user_id': user.id,
        })

    earliest_date = activities[-1]['start_date'] if activities else None
    if earliest_date and start_date <= earliest_date:
        # get more activities from next page
        next_page = page + 1
        next_page_activities = get_activities_for(user, start_date=start_date, end_date=end_date, page=next_page)
        activities.extend(next_page_activities)

    return activities


# def activities_timeline(activities: list, start_date: datetime, end_date: datetime) -> dict:
#     days = (end_date - start_date).days + 1
#     date_ranges  = [start_date + timedelta(days=day) for day in range(days)]
#     timelines = {date: 0 for date in date_ranges}
#     for activity in activities:
#         start_date = activity['start_date'].date()
#         timelines[start_date] = max(activity['distance'], timelines.get(start_date, 0))
#     return timelines


# def get_reward(activities: list, start_date: datetime, end_date: datetime) -> int:
#     # get max distance on each date
#     fee = get_fee()
#     reward_per_km = fee['reward_per_km']
#     lose_per_km = fee['lose_per_km']
#     target_distance = fee['target_distance']

#     timelines = activities_timeline(activities, start_date, end_date)  
#     reward = 0

#     dates = sorted(activities.keys())

#     for index, date in enumerate(dates[::2]):
#         try:
#             day1, day2 = 
#             max_distance = max(distances[day1], distances[day2])
#         except IndexError:
#             date = date_ranges[day]
#             max_distance = distances[date]
        
#         if max_distance < target_distance:
#             reward -= (target_distance - max_distance) * lose_per_km
#         else:
#             reward += max_distance * reward_per_km

#     return reward


def get_fee() -> dict:
    return {
        'reward_per_km': 5000,
        'lose_per_km': 7000,
        'target_distance': 5,
    }


def test_get_reward():
    activities = Activity.objects.values('start_date', 'distance').order_by('-start_date')
    start_date = activities[0]['start_date']
    end_date = timezone.now()
    reward = get_reward(activities, start_date, end_date)
    print(reward)


def get_timeseries(start_date: date, end_date: date) -> list:
    days = (end_date - start_date).days + 1
    dates = [start_date + timedelta(days=day) for day in range(days)]
    return dates


def get_reward(distances: list) -> int:
    total_days = len(distances)
    day = 0
    reward = 0
    fee = get_fee()
    reward_per_km = fee['reward_per_km']
    lose_per_km = fee['lose_per_km']
    target_distance = fee['target_distance']

    while day < total_days:
        next_day = day + 1
        if next_day < total_days:
            max_distance = max(distances[day], distances[next_day])
        else:
            max_distance = distances[day]

        if max_distance >= target_distance:
            reward += max_distance * reward_per_km
        else:
            reward -= (target_distance - max_distance) * lose_per_km
        day += 2
    return reward


def get_distance_per_day(activities: list, timeseries: list) -> list:
    # get max distance on each day
    activities_date = {}
    for activity in activities:
        date = activity['start_date']
        activities_date[date] = int(max(activities_date.get(date, 0), activity['distance']) / 1000)  # convert to km

    return [activities_date.get(date, 0) for date in timeseries]


@receiver(post_save, sender=SocialToken)
def update_activities_for_new_user(sender, instance, **kwargs):
    # update activities for last 30 days
    user = instance.account.user
    start_date = timezone.now().date() - timedelta(days=30)
    update_activities_for(user, start_date=start_date)
