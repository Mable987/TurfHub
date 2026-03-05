from django.urls import path
from OwnerApp import views

urlpatterns = [

    path('dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('login/', views.owner_login, name='owner_login'),
    path('signup/', views.owner_signup, name='owner_signup'),
    path('logout/', views.owner_logout, name='owner_logout'),
    path('add_turf/', views.owner_add_turf, name='owner_add_turf'),
    path('view_turfs/', views.owner_view_turfs, name='owner_view_turfs'),
    path('edit_turf/<int:turf_id>/', views.owner_edit_turf, name='owner_edit_turf'),
    path('update_turf/<int:turf_id>/', views.owner_update_turf, name='owner_update_turf'),
    path('delete_turf/<int:turf_id>/', views.owner_delete_turf, name='owner_delete_turf'),
    
]