from django.shortcuts import render
from Booking.models import Turf, Booking

# Create your views here.
def turf_list(request):
    turfs = Turf.objects.all()
    return render(request, 'turf_list.html', {'turfs': turfs})