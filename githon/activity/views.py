from django.shortcuts import render
from django.utils import timezone

from .models import Activity 
from .service import get_reward

# Create your views here.

def get_activities(request):
    start_date = request.GET.get('start_date') or timezone.now()
    end_date = request.GET.get('end_date') or timezone.now()

    activities = Activity.objects.filter(start_date__gte=start_date, start_date__lte=end_date) \
                                 .select_related('user__username') \
                                 .values_list('user__username', 'start_date', 'distance') \
                                 .order_by('-start_date')
