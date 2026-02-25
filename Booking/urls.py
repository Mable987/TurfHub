from django.urls import path
from Booking import views     

urlpatterns = [
    path('turfs/', views.turf_list, name='turf_list'),
]