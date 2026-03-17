from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test ,login_required
from Booking.models import *
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages




# Create your views here.
def owner_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and u.is_staff and not u.is_superuser,
        login_url='owner_login'
    )(view_func)

@owner_required
def owner_dashboard(request):

    total_turfs = Turf.objects.filter(owner=request.user).count()

    total_bookings = Booking.objects.filter(
        turf__owner=request.user
    ).count()

    total_earnings = Booking.objects.filter(
        turf__owner=request.user,
        payment_status='paid'
    ).aggregate(Sum('owner_amount'))['owner_amount__sum'] or 0

    context = {
        'total_turfs': total_turfs,
        'total_bookings': total_bookings,
        'total_earnings': total_earnings
    }

    return render(request, 'owner/dashboard.html', context)  

def owner_login(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password")

        elif not user.is_staff:
            messages.error(request, "You are not registered as an owner")

        else:
            login(request, user)
            return redirect('owner:owner_dashboard')

    return render(request, "owner/owner_login.html")
def owner_logout(request):
    logout(request)
    return redirect('owner:owner_login')        
     
def owner_signup(request):

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('owner_signup')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.is_staff = True
        user.save()

        messages.success(request, "Account created successfully")
        return redirect('owner:owner_login')

    return render(request, 'owner/owner_signup.html')
@owner_required
def owner_add_turf(request):

    sports = Sport.objects.all()

    if request.method == "POST":

        turf = Turf.objects.create(
            owner=request.user,
            turf_name=request.POST.get('turf_name'),
            location=request.POST.get('location'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            price_per_hour=request.POST.get('price'),
            opening_time=request.POST.get('opening_time'),
            closing_time=request.POST.get('closing_time'),
            description=request.POST.get('description'),
            turf_image=request.FILES.get('turf_image')
)

        selected_sports = request.POST.getlist('sports')
        turf.sports.set(selected_sports)

        return redirect('owner:owner_add_turf')

    return render(request, 'owner/add_turf.html', {'sports': sports})
@owner_required
def owner_view_turfs(request):

    turfs = Turf.objects.filter(owner=request.user)

    context = {
        "turfs": turfs
    }

    return render(request, "owner/view_turfs.html", context)

@login_required(login_url='owner_login')
def owner_edit_turf(request, turf_id):

    turf = get_object_or_404(Turf, id=turf_id, owner=request.user)

    if request.method == "POST":

        turf.turf_name = request.POST.get('turf_name')
        turf.location = request.POST.get('location')
        turf.price_per_hour = request.POST.get('price')
        turf.description = request.POST.get('description')

        if request.FILES.get('turf_image'):
            turf.turf_image = request.FILES.get('turf_image')

        turf.save()

        return redirect('owner:owner_view_turfs')
    sports = Sport.objects.all()

    return render(request, "owner/edit_turf.html", {"turf": turf, "sports": sports})
def owner_update_turf(request, turf_id):

    turf = get_object_or_404(Turf, id=turf_id)

    if request.method == "POST":

        turf.turf_name = request.POST.get("turf_name")
        turf.location = request.POST.get("location")
        turf.price_per_hour = request.POST.get("price")
        turf.description = request.POST.get("description")

        if request.FILES.get("turf_image"):
            turf.turf_image = request.FILES.get("turf_image")

        turf.save()

        # update sports
        selected_sports = request.POST.getlist("sports")
        turf.sports.set(selected_sports)

        return redirect('owner:owner_view_turfs')
@login_required(login_url='owner_login')
def owner_delete_turf(request, turf_id):

    turf = get_object_or_404(Turf, id=turf_id, owner=request.user)

    turf.delete()

    return redirect('owner:owner_view_turfs')  
 
@owner_required
def owner_view_bookings(request):

    bookings = Booking.objects.filter(
        turf__owner=request.user
    ).select_related('user', 'turf').order_by('-created_at')

    context = {
        "bookings": bookings
    }

    return render(request, "owner/view_bookings.html", context)