from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from decimal import Decimal
from django.core.exceptions import ValidationError


class Turf(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    turf_name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    turf_image = models.ImageField(upload_to='turf_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.turf_name


class Booking(models.Model):

    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')

    platform_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    owner_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.turf.turf_name}"

    def clean(self):
        overlapping_bookings = Booking.objects.filter(
            turf=self.turf,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
            status__in=['pending', 'confirmed']
        )

        if self.pk:
            overlapping_bookings = overlapping_bookings.exclude(pk=self.pk)

        if overlapping_bookings.exists():
            raise ValidationError("This time slot is already booked.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Important: run clean()

        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)

        duration = end - start
        hours = duration.total_seconds() / 3600

        self.total_price = Decimal(hours) * self.turf.price_per_hour

        commission_rate = Decimal('0.10')
        self.platform_commission = self.total_price * commission_rate
        self.owner_amount = self.total_price - self.platform_commission

        super().save(*args, **kwargs)