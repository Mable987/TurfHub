from django.shortcuts import render
from Booking.models import *

# Create your views here.
def home(request):
    turfs = Turf.objects.all()
    return render(request, 'home.html', {'turfs': turfs})

def turf_list(request):

    sports = Sport.objects.all()
    selected_sport = request.GET.get('sport')

    turfs = Turf.objects.filter(is_active=True)

    if selected_sport:
        turfs = turfs.filter(sports__id=selected_sport)

    context = {
        'turfs': turfs,
        'sports': sports,
        'selected_sport': selected_sport
    }

    return render(request, 'turf_list.html', context)
