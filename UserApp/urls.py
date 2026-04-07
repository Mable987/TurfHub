from django.urls import path
from UserApp import views

appname = "user"
urlpatterns = [
    path('home/', views.home, name='home'),
    path('turf_list/', views.turf_list, name='turf_list'),
    path('turf_details/<int:turf_id>/', views.turf_details, name='turf_details'),
    path('add_review/<int:turf_id>/', views.add_review, name='add_review'),
    path('login/', views.user_login, name='user_login'),
    path('signup/', views.user_signup, name='user_signup'),
    path('logout/', views.user_logout, name='user_logout'),
    path('profile/', views.profile, name='profile'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path("contact/", views.contact_view, name="contact"),
    

]