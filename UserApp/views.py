from django.shortcuts import redirect, render
from Booking.models import *
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Create your views here.
@login_required(login_url='user:user_login')
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

    return redirect('user:turf_details', turf_id=turf_id)

def user_signup(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('user:user_signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('user:user_signup')

        if User.objects.filter(username=username).exists():   
            messages.error(request, "Username already taken")
            return redirect('user:user_signup')

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully")
        return redirect('user:user_login')

    return render(request, "user_signup.html")

def user_login(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return redirect('user:user_login')
        user = authenticate(request, username=user.username, password=password)

        if user:
            login(request, user)
            return redirect('user:home')
        messages.error(request, "Invalid email or password")

    return render(request, "user_login.html")
def user_logout(request):
    logout(request)
    return redirect('user:user_login')
def profile(request):
    return render(request,'profile.html')

@login_required(login_url='user:user_login')
def my_bookings(request):

    now = timezone.now()

    bookings = Booking.objects.filter(
        user=request.user,
        payment_status='paid'
    )

    active_bookings = []

    for booking in bookings:
        booking_datetime = datetime.combine(booking.date, booking.end_time)

        if booking_datetime > now.replace(tzinfo=None):
            active_bookings.append(booking)

    return render(request, 'my_bookings.html', {'bookings': active_bookings})



