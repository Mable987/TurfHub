from django.urls import path
from UserApp import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('turf_list/', views.turf_list, name='turf_list'),
]