from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Sport(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Turf(models.Model):

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="owned_turfs"
    )

    turf_name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)

    sports = models.ManyToManyField(Sport, blank=True)

    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2)

    description = models.TextField()

    turf_image = models.ImageField(upload_to='turf_images/', null=True, blank=True)

    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

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
    class Meta:
        indexes = [
            models.Index(fields=['turf', 'date']),
        ]

    def clean(self):

        if not self.turf.is_active:
            raise ValidationError("This turf is currently unavailable.")

    # Prevent past date booking
        if self.date < timezone.now().date():
            raise ValidationError("You cannot book a past date.")

    # Prevent past time today
        if self.date == timezone.now().date() and self.start_time <= timezone.now().time():
            raise ValidationError("Cannot book a past time today.")

    # Prevent invalid time range
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")

    # Opening time check
        if self.turf.opening_time and self.start_time < self.turf.opening_time:
            raise ValidationError("Booking before opening time.")

    # Closing time check
        if self.turf.closing_time and self.end_time > self.turf.closing_time:
            raise ValidationError("Booking after closing time.")

    # Overlap check
        overlapping_bookings = Booking.objects.filter(
            turf=self.turf,
            date=self.date,
            status__in=['pending', 'confirmed']
        ).filter(
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )

        if self.pk:
            overlapping_bookings = overlapping_bookings.exclude(pk=self.pk)

        if overlapping_bookings.exists():
            raise ValidationError("This time slot is already booked.")

    def save(self, *args, **kwargs):
        self.full_clean() 

        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)

        duration = end - start
        hours = Decimal(duration.total_seconds()) / Decimal(3600)
        self.total_price = hours * self.turf.price_per_hour

        commission_rate = Decimal('0.10')
        self.platform_commission = self.total_price * commission_rate
        self.owner_amount = self.total_price - self.platform_commission

        super().save(*args, **kwargs)
        
class Review(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    turf = models.ForeignKey(
        Turf,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.IntegerField(
    validators=[MinValueValidator(1), MaxValueValidator(5)]
)

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.turf.turf_name}" 
     
    class Meta:
        unique_together = ['user', 'turf']      