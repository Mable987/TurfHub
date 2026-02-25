from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

from django.db import models

class Turf(models.Model):
    turf_name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    turf_image = models.ImageField(upload_to='turf_images/', null=True, blank=True)

    def __str__(self):
        return self.turf_name

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.turf.turf_name}"

