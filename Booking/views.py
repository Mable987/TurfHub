from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Booking, Turf


@login_required
def book_turf(request, turf_id):

    turf = get_object_or_404(Turf, id=turf_id)

    if request.method == "POST":

        selected_date = request.POST.get("date")
        start_time_str = request.POST.get("start_time")
        sport_id = request.POST.get("sport")
        duration = int(request.POST.get("duration", 1))

        # prevent empty time submission
        if not start_time_str:
            messages.error(request, "Please select a start time.")
            return redirect("book_turf", turf_id=turf.id)

        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        start_datetime = datetime.combine(datetime.today(), start_time)

        end_datetime = start_datetime + timedelta(hours=duration)
        end_time = end_datetime.time()

        # ✅ check turf opening hours safely
        if turf.opening_time and turf.closing_time:
            if start_time < turf.opening_time or end_time > turf.closing_time:
                messages.error(request, "Selected time is outside turf operating hours.")
                return redirect("book_turf", turf_id=turf.id)

        # ✅ prevent overlapping bookings
        existing_booking = Booking.objects.filter(
            turf=turf,
            date=selected_date,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if existing_booking:
            messages.error(request, "This time slot is already booked.")
            return redirect("book_turf", turf_id=turf.id)

        try:
            Booking.objects.create(
                turf=turf,
                sport_id=sport_id,
                date=selected_date,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                user=request.user
            )

            messages.success(request, "Slot added to cart.")

        except ValidationError as e:
            messages.error(request, e.message_dict.get("__all__", ["Slot booking failed"])[0])

    # get all cart items
    cart_items = Booking.objects.filter(user=request.user, turf=turf)

    # calculate total price
    cart_total = 0
    for item in cart_items:
        cart_total += item.turf.price_per_hour * item.duration

    context = {
        "turf": turf,
        "cart_items": cart_items,
        "cart_total": cart_total
    }

    return render(request, "book_turf.html", context)

def clear_cart(request, turf_id):
    Booking.objects.filter(user=request.user, turf_id=turf_id).delete()
    messages.info(request, "Cart cleared")
    return redirect("book_turf", turf_id=turf_id)
def remove_cart_item(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    turf_id = booking.turf.id

    booking.delete()

    return redirect("book_turf", turf_id=turf_id)
@login_required
def booking_summary(request):

   
    cart_items = Booking.objects.filter(
        user=request.user,
        payment_status='pending'
    )

    total_amount = 0
    for item in cart_items:
        total_amount += item.turf.price_per_hour * item.duration

    context = {
        "cart_items": cart_items,
        "total_amount": total_amount
    }

    return render(request, "booking_summary.html", context)
@login_required
def confirm_booking(request):

    if request.method == "POST":

        cart_items = Booking.objects.filter(
            user=request.user,
            payment_status='pending'
        )

        total_amount = sum(
            item.turf.price_per_hour * item.duration
            for item in cart_items
        )

        # 👉 next step: redirect to payment page
        return render(request, "payment.html", {
            "amount": total_amount
        })

    return redirect("booking_summary")