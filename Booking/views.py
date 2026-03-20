from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from Booking.models import Booking, Turf
import razorpay, json, qrcode
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from razorpay.errors import SignatureVerificationError



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
            return redirect("booking:book_turf", turf_id=turf.id)

        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        start_datetime = datetime.combine(datetime.today(), start_time)

        end_datetime = start_datetime + timedelta(hours=duration)
        end_time = end_datetime.time()

        if turf.opening_time and turf.closing_time:
            if start_time < turf.opening_time or end_time > turf.closing_time:
                messages.error(request, "Selected time is outside turf operating hours.")
                return redirect("booking:book_turf", turf_id=turf.id)

        existing_booking = Booking.objects.filter(
            turf=turf,
            date=selected_date,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if existing_booking:
            messages.error(request, "This time slot is already booked.")
            return redirect("booking:book_turf", turf_id=turf.id)

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
   
    cart_items = Booking.objects.filter(user=request.user, turf=turf)

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
    return redirect("booking:book_turf", turf_id=turf_id)
def remove_cart_item(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    turf_id = booking.turf.id

    booking.delete()

    return redirect("booking:book_turf", turf_id=turf_id)
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

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    cart_items = Booking.objects.filter(
        user=request.user,
        payment_status='pending'
    )

    total_amount = sum(
        item.turf.price_per_hour * item.duration
        for item in cart_items
    )

    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))

    order = client.order.create({
        "amount": int(total_amount * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    return JsonResponse({
        "order_id": order["id"],
        "amount": order["amount"]
    })
@login_required
def booking_success(request):

    bookings = Booking.objects.filter(
        user=request.user,
        payment_status='paid'
    ).order_by('-created_at')

    return render(request, "booking_success.html", {"bookings": bookings})
@csrf_exempt
@login_required
def verify_payment(request):

    data = json.loads(request.body)

    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))

    params_dict = {
        'razorpay_order_id': data['razorpay_order_id'],
        'razorpay_payment_id': data['razorpay_payment_id'],
        'razorpay_signature': data['razorpay_signature']
    }

    try:
        
        client.utility.verify_payment_signature(params_dict)

        
        Booking.objects.filter(
            user=request.user,
            payment_status='pending'
        ).update(
            payment_status='paid',
            status='confirmed',   
            razorpay_payment_id=data['razorpay_payment_id'],
            razorpay_order_id=data['razorpay_order_id'],
            razorpay_signature=data['razorpay_signature']
        )

        return JsonResponse({'status': 'success'})

    except SignatureVerificationError:
        return JsonResponse({'status': 'failure'})
def generate_qr(request, booking_id):
    img = qrcode.make(f"Booking ID: {booking_id}")
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response    
    