from django.shortcuts import redirect, render
from Booking.models import *
from django.shortcuts import render, get_object_or_404

# Create your views here.
def home(request):

    turfs = Turf.objects.filter(is_active=True)[:6]
    sports = Sport.objects.all()

    context = {
        'turfs': turfs,
        'sports': sports
    }

    return render(request, "home.html", context)

def turf_list(request):

    sports = Sport.objects.all()

    selected_sport = request.GET.get('sport')
    city = request.GET.get('city')
    state = request.GET.get('state')

    turfs = Turf.objects.filter(is_active=True).prefetch_related('sports')

    if city:
        turfs = turfs.filter(city__icontains=city)

    if state:
        turfs = turfs.filter(state__icontains=state)

    if selected_sport:
        turfs = turfs.filter(sports__id=selected_sport)

    context = {
        'turfs': turfs,
        'sports': sports,
        'selected_sport': selected_sport,
        'city': city,
        'state': state
    }

    return render(request, 'turf_list.html', context)
def turf_details(request, turf_id):

    turf = get_object_or_404(Turf, id=turf_id)

    reviews = Review.objects.filter(turf=turf).order_by('-created_at')

    sports = turf.sports.all()

    context = {
        'turf': turf,
        'reviews': reviews,
        'sports': sports
    }

    return render(request, 'turf_details.html', context)
def add_review(request, turf_id):

    if request.method == "POST":

        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        turf = Turf.objects.get(id=turf_id)

        Review.objects.create(
            user=request.user,
            turf=turf,
            rating=rating,
            comment=comment
        )

    return redirect('turf_details', turf_id=turf_id)