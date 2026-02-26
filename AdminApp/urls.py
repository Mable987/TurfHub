from django.urls import path
from AdminApp import views
urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('add_turf/', views.add_turf, name='add_turf'),
    path('view_turfs/', views.view_turfs, name='view_turfs'),
    path('edit_turf/<int:turf_id>/', views.edit_turf, name='edit_turf'),
    path('delete_turf/<int:turf_id>/', views.delete_turf, name='delete_turf'),

    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('admin_view_bookings/', views.admin_view_bookings, name='admin_view_bookings'),
    path('toggle_turf_status/<int:turf_id>/', views.toggle_turf_status, name='toggle_turf_status'),
]