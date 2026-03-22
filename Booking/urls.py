from django.urls import path
from Booking import views     

app_name = "booking"

urlpatterns = [
    path('book_turf/<int:turf_id>/', views.book_turf, name='book_turf'),
    path('clear_cart/<int:turf_id>/', views.clear_cart, name='clear_cart'),
    path("remove-cart-item/<int:booking_id>/", views.remove_cart_item, name="remove_cart_item"),
    path('booking_summary/', views.booking_summary, name='booking_summary'),
    path('confirm_booking/', views.confirm_booking, name='confirm_booking'),
    path('booking-success/', views.booking_success, name='booking_success'),
    path('verify_payment/', views.verify_payment, name='verify_payment'),
    path('generate_qr/<int:booking_id>/', views.generate_qr, name='generate_qr'),
    path('download_ticket/<int:booking_id>/', views.download_ticket, name='download_ticket'),
    path('validate_qr/', views.validate_qr, name='validate_qr'),
    path('scan/', views.scan_qr_page, name='scan_qr'),

]