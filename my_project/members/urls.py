# members/urls.py
# from django.urls import path
from django.urls import path # <-- TYPO
from . import views

urlpatterns = [
    # homepage
    path('', views.index, name='index'),

    # listings
    path('listings/', views.listing_list, name='listing_list'),
    path('listing/<int:listing_id>/', views.listing_detail, name='listing_detail'),

    # REMOVED the old booking_list URL to avoid confusion
    # path('bookings/', views.booking_list, name='booking_list'), 
    
    # bookings (detail page is still useful)
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),

    # reservations
    path('listing/<int:listing_id>/reserve/', views.reserve_listing, name='reserve_listing'),
    path('my-bookings/', views.my_bookings, name='my_bookings'), # This is the only booking list we need
    path('booking/<int:booking_id>/modify/', views.modify_booking, name='modify_booking'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    
    # hosting
    path('create-listing/', views.create_listing, name='create_listing'),
]