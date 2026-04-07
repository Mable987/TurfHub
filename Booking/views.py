from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from Booking.models import Booking, Turf
import razorpay, json, qrcode, tempfile
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from razorpay.errors import SignatureVerificationError
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet
from django.core.mail import send_mail
from reportlab.lib import colors
from django.utils import timezone




@login_required
def book_turf(request, turf_id):

    turf = get_object_or_404(Turf, id=turf_id)

    if request.method == "POST":

        selected_date = request.POST.get("date")
        start_time_str = request.POST.get("start_time")
        sport_id = request.POST.get("sport")
        duration = int(request.POST.get("duration", 1))

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
        bookings = Booking.objects.filter(
            user=request.user,
            payment_status='pending'
        )
        for booking in bookings:
             if booking.payment_status != 'paid':
                booking.payment_status = 'paid'
                booking.status = 'confirmed'
                booking.razorpay_payment_id = data['razorpay_payment_id']
                booking.razorpay_order_id = data['razorpay_order_id']
                booking.razorpay_signature = data['razorpay_signature']
                booking.save()
                send_booking_email(request.user, booking)

        return JsonResponse({'status': 'success'})

    except SignatureVerificationError:
        return JsonResponse({'status': 'failure'})
def generate_qr(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    qr_data = {
        "booking_id": booking.booking_id,
        "user": booking.user.username,
        "date": str(booking.date),
        "start_time": str(booking.start_time)
    }

    img = qrcode.make(json.dumps(qr_data))
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response
def download_ticket(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{booking.id}.pdf"'
    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph("🎟️ TurfHub Ticket", styles['Title']))
    elements.append(Spacer(1, 20))
    qr_data = {
        "booking_id": booking.booking_id,
        "user": booking.user.username,
        "date": str(booking.date),
        "start_time": str(booking.start_time)
    }
    qr = qrcode.make(json.dumps(qr_data))

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    qr.save(temp_file.name)

    qr_image = Image(temp_file.name, width=120, height=120)
    qr_inner = Table([
        [qr_image],
        [Paragraph("<font color='white'>Scan at entry</font>", styles['Normal'])]
    ])

    qr_inner.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    details = [
        Paragraph(f"<b>Name:</b> {booking.user.username}", styles['Normal']),
        Paragraph(f"<b>{booking.turf.turf_name}</b>", styles['Heading3']),
        Paragraph(f"{booking.turf.location}", styles['Normal']),
        Spacer(1, 5),
        Paragraph(f"🏟 {booking.sport.name}", styles['Normal']),
        Paragraph(f"📅 {booking.date}", styles['Normal']),
        Paragraph(f"⏰ {booking.start_time} - {booking.end_time}", styles['Normal']),
        Paragraph(f"💰 ₹{booking.total_price}", styles['Normal']),
        Spacer(1, 5),
        Paragraph(f"<b>Booking ID:</b> {booking.booking_id}", styles['Normal']),
    ]
    table = Table(
        [[qr_inner,"", details]],
        colWidths=[160,20, 300]
    )
    table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, colors.black),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#12b76a")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
        ('TOPPADDING', (0,0), (-1,-1), 20),
        ('BOTTOMPADDING', (0,0), (-1,-1), 20),
    ]))

    elements.append(table)

    doc.build(elements)

    return response
def send_booking_email(user, booking):
    subject = "🎟️ Turf Booking Confirmed"

    message = f"""
Hi {user.username},

Your booking is confirmed!

Turf: {booking.turf.turf_name}
Date: {booking.date}
Time: {booking.start_time} - {booking.end_time}
Booking ID: {booking.booking_id}

Thank you for using TurfHub!
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
@csrf_exempt
def validate_qr(request):
    if request.method == "POST":
        data = json.loads(request.body)

        booking_id = data.get("booking_id")

        try:
            booking = Booking.objects.get(booking_id=booking_id)          
            if booking.payment_status != "paid":
                return JsonResponse({"status": "invalid", "message": "Payment not completed"})
            
            if booking.is_used:
                return JsonResponse({"status": "used", "message": "Ticket already used"})

            now = timezone.now()
            booking_datetime = datetime.combine(booking.date, booking.end_time)

            if now > booking_datetime:
                return JsonResponse({"status": "expired", "message": "Booking expired"})
            booking.is_used = True
            booking.save()

            return JsonResponse({
                "status": "valid",
                "message": "Entry allowed",
                "user": booking.user.username,
                "turf": booking.turf.turf_name,
                "time": f"{booking.start_time} - {booking.end_time}"
            })

        except Booking.DoesNotExist:
            return JsonResponse({"status": "invalid", "message": "Invalid QR"}) 
def scan_qr_page(request):
    return render(request, "scan_qr.html")           