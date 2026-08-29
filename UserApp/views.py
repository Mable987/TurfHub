from django.shortcuts import redirect, render
from Booking.models import *
from UserApp.models import Contact
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

# Create your views here.

def home(request):
    turfs = Turf.objects.filter(is_active=True)[:6]
    sports = Sport.objects.all()

    cities = (
        Turf.objects.filter(is_active=True)
        .values('city')
        .annotate(count=Count('id'))
        .order_by('-count')[:6]
    )

    context = {
        'turfs': turfs,
        'sports': sports,
        'cities': cities
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

    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    total_reviews = reviews.count()

    user_reviewed = False
    if request.user.is_authenticated:
        user_reviewed = reviews.filter(user=request.user).exists()

    context = {
        'turf': turf,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'user_reviewed': user_reviewed
    }

    return render(request, 'turf_details.html', context)

@login_required
def add_review(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)

    if request.method != "POST":
        return redirect('user:turf_details', turf_id=turf_id)

    if Review.objects.filter(user=request.user, turf=turf).exists():
        messages.error(request, "You already reviewed this turf.")
        return redirect('user:turf_details', turf_id=turf_id)

    rating = request.POST.get("rating")
    comment = request.POST.get("comment")

    if not rating or not comment:
        messages.error(request, "All fields are required.")
        return redirect('user:turf_details', turf_id=turf_id)

    Review.objects.create(
        user=request.user,
        turf=turf,
        rating=int(rating),
        comment=comment,
    )
    messages.success(request, "Review added successfully!")
    return redirect('user:turf_details', turf_id=turf_id)

def user_signup(request):

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        selected_avatar = request.POST.get("avatar_preset")

        from UserApp.models import UserProfile
        form_data = {"username": username, "email": email}
        ctx = {"form_data": form_data, "avatar_presets": UserProfile.AVATAR_PRESETS, "selected_avatar": selected_avatar}

        if not username or not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, "user_signup.html", ctx)

        if "@" not in email or "." not in email.split("@")[-1]:
            messages.error(request, "Enter a valid email address.")
            return render(request, "user_signup.html", ctx)

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, "user_signup.html", ctx)

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "user_signup.html", ctx)

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, "user_signup.html", ctx)

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "That username is taken. Try another.")
            return render(request, "user_signup.html", ctx)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            avatar_preset=selected_avatar if selected_avatar in UserProfile.AVATAR_PRESETS else "avatar1.svg",
        )

        login(request, user)
        messages.success(request, "Welcome! Your account has been created.")
        return redirect('user:home')

    from UserApp.models import UserProfile
    return render(request, "user_signup.html", {"avatar_presets": UserProfile.AVATAR_PRESETS})

def user_login(request):

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not email or not password:
            messages.error(request, "Enter both email and password.")
            return render(request, "user_login.html", {"email": email})

        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, "user_login.html", {"email": email})
        except User.MultipleObjectsReturned:
            user_obj = User.objects.filter(email__iexact=email).first()

        user = authenticate(request, username=user_obj.username, password=password)

        if user:
            login(request, user)
            next_url = request.POST.get("next") or request.GET.get("next")
            return redirect(next_url or 'user:home')
        messages.error(request, "Invalid email or password.")
        return render(request, "user_login.html", {"email": email})

    return render(request, "user_login.html")
def user_logout(request):
    logout(request)
    messages.success(request, "You've been logged out.")
    return redirect('user:user_login')
@login_required(login_url='user:user_login')
def profile(request):
    from UserApp.models import UserProfile
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        request.user.first_name = first_name
        request.user.save(update_fields=["first_name"])

        preset = request.POST.get("avatar_preset")
        if request.FILES.get("avatar"):
            user_profile.avatar = request.FILES["avatar"]
            user_profile.avatar_preset = None
            user_profile.save(update_fields=["avatar", "avatar_preset"])
        elif preset in UserProfile.AVATAR_PRESETS:
            user_profile.avatar = None
            user_profile.avatar_preset = preset
            user_profile.save(update_fields=["avatar", "avatar_preset"])

        messages.success(request, "Profile updated.")
        return redirect('user:profile')

    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'avatar_presets': UserProfile.AVATAR_PRESETS,
    })

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

def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        if not all([name, email, subject, message]):
            messages.error(request, "Please fill in all the fields.")
            return redirect("user:contact")

        # Save message
        Contact.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        # Send email notification
        try:
            send_mail(
                subject=f"New Contact Message - {subject}",
                message=f"""
A new contact form has been submitted.

Name: {name}
Email: {email}

Subject:
{subject}

Message:
{message}
""",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
        except Exception:
            messages.warning(
                request,
                "Your message was saved, but email notification could not be sent."
            )
            return redirect("user:contact")

        messages.success(
            request,
            "Thank you! Your message has been sent successfully."
        )

        return redirect("user:contact")

    return render(request, "contacts.html")

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not email:
            messages.error(request, "Enter your email address.")
            return render(request, "forgot_password.html")

        user = User.objects.filter(email__iexact=email).first()

        # Always show the same message whether or not the account exists,
        # so this form can't be used to check which emails are registered.
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(
                f"/reset-password/{uid}/{token}/"
            )
            try:
                send_mail(
                    subject="Reset your TurfHub password",
                    message=(
                        f"Hi {user.username},\n\n"
                        f"Click the link below to reset your TurfHub password. "
                        f"This link expires soon and can only be used once.\n\n"
                        f"{reset_link}\n\n"
                        f"If you didn't request this, you can safely ignore this email."
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception:
                pass  # Don't leak SMTP errors; show the generic message regardless.

        messages.success(
            request,
            "If an account exists with that email, a reset link has been sent."
        )
        return redirect("user:forgot_password")

    return render(request, "forgot_password.html")


def reset_password_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    valid_link = user is not None and default_token_generator.check_token(user, token)

    if not valid_link:
        return render(request, "reset_password_confirm.html", {"valid_link": False})

    if request.method == "POST":
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, "reset_password_confirm.html", {"valid_link": True})

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "reset_password_confirm.html", {"valid_link": True})

        user.set_password(password)
        user.save()
        messages.success(request, "Your password has been reset. You can log in now.")
        return redirect("user:user_login")

    return render(request, "reset_password_confirm.html", {"valid_link": True})
