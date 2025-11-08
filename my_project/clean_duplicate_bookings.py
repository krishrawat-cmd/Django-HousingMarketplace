import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')
django.setup()

from members.models import Booking
from django.db.models import Count
from django.db import transaction

def find_duplicate_bookings():
    """
    Find bookings that have the same user, listing, check_in, and check_out dates
    """
    # Group by user, listing, check_in, check_out and count
    duplicates = Booking.objects.values('user', 'listing', 'check_in', 'check_out').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    print(f"Found {len(duplicates)} groups of duplicate bookings")
    return duplicates

def clean_duplicate_bookings():
    """
    Keep only one booking from each group of duplicates
    """
    duplicates = find_duplicate_bookings()
    
    if not duplicates:
        print("No duplicate bookings found. No cleanup needed.")
        return
    
    with transaction.atomic():
        for dup in duplicates:
            # Get all bookings matching these criteria
            bookings = Booking.objects.filter(
                user=dup['user'],
                listing=dup['listing'],
                check_in=dup['check_in'],
                check_out=dup['check_out']
            ).order_by('id')
            
            # Keep the first one, delete the rest
            first_booking = bookings.first()
            print(f"Keeping booking ID {first_booking.id} for user {dup['user']}, listing {dup['listing']}")
            
            # Delete all except the first one
            to_delete = bookings.exclude(id=first_booking.id)
            delete_count = to_delete.count()
            to_delete.delete()
            
            print(f"Deleted {delete_count} duplicate bookings")

if __name__ == "__main__":
    print("Starting duplicate booking cleanup...")
    clean_duplicate_bookings()
    print("Cleanup complete!")