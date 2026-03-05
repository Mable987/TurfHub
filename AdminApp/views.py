from django.shortcuts import render, redirect
from Booking.models import Turf,Booking
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum


# Create your views here.
def superuser_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='admin_login'
    )(view_func)

@superuser_required
def admin_dashboard(request):
    total_turfs = Turf.objects.count()
    total_bookings = Booking.objects.count()
    total_users = User.objects.count()

    context = {
        'total_turfs': total_turfs,
        'total_bookings': total_bookings,
        'total_users': total_users
    }
    return render(request, 'dashboard.html', context)
 
@superuser_required
def add_turf(request):

    if request.method == "POST":
        turf_name = request.POST.get('turf_name')
        location = request.POST.get('location')
        price = request.POST.get('price')
        description = request.POST.get('description')
        turf_image = request.FILES.get('turf_image')

        sports_ids = request.POST.getlist('sports')   

        turf = Turf.objects.create(                   
            turf_name=turf_name,
            location=location,
            price_per_hour=price,
            description=description,
            turf_image=turf_image
        )

        turf.sports.set(sports_ids)                   

        messages.success(request, "Turf added successfully!")
        return redirect('add_turf')

    return render(request, 'add_turf.html')
@superuser_required
def view_turfs(request):
    turfs = Turf.objects.all().order_by('-id')

    context = {
        'turfs': turfs
    }

    return render(request, 'view_turfs.html', context)

@superuser_required
def edit_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)

    if request.method == "POST":
        turf.turf_name = request.POST.get('turf_name')
        turf.location = request.POST.get('location')
        turf.price_per_hour = request.POST.get('price')
        turf.description = request.POST.get('description')

        if request.FILES.get('turf_image'):
            turf.turf_image = request.FILES.get('turf_image')

        turf.save()

        messages.success(request, "Turf updated successfully!")
        return redirect('view_turfs')

    context = {
        'turf': turf
    }

    return render(request, 'edit_turf.html', context)

@superuser_required
def delete_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)

    turf.delete()
    messages.success(request, "Turf deleted successfully!")

    return redirect('view_turfs')

def admin_login(request):

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password.")
        elif not user.is_superuser:
            messages.error(request, "You are not authorized to access admin panel.")
        else:
            login(request, user)
            return redirect('admin_dashboard')

    return render(request, 'admin_login.html')

def admin_logout(request):
    logout(request)
    return redirect('admin_login')


@superuser_required
def admin_view_bookings(request):
    bookings = Booking.objects.select_related('user', 'turf').order_by('-created_at')

    context = {
        'bookings': bookings
    }

    return render(request, 'admin_view_bookings.html', context)
@superuser_required
def toggle_turf_status(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    turf.is_active = not turf.is_active
    turf.save()
    return redirect('view_turfs')