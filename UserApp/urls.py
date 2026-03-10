from django.urls import path
from UserApp import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('turf_list/', views.turf_list, name='turf_list'),
    path('turf_details/<int:turf_id>/', views.turf_details, name='turf_details'),
    path('add_review/<int:turf_id>/', views.add_review, name='add_review'),
]