from django.urls import path
from Booking import views     

urlpatterns = [
    path('book_turf/<int:turf_id>/', views.book_turf, name='book_turf'),
    path('clear_cart/<int:turf_id>/', views.clear_cart, name='clear_cart'),
    path("remove-cart-item/<int:booking_id>/", views.remove_cart_item, name="remove_cart_item"),
    path('confirm_booking/', views.confirm_booking, name='confirm_booking'),

]