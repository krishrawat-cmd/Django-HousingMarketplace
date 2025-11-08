# members/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, date

from .models import User, Listing, Booking, ListingImage
from .forms import RegisterForm, ListingForm

# ==============================================================================
# PUBLIC VIEWS (Accessible to anyone)
# ==============================================================================
   
@login_required
def index(request):
    """
    Renders the homepage with the 6 most recent listings.
    """
    print(">>> THE INDEX VIEW IS BEING CALLED! <<<")
    print(f">>> Is the user authenticated? {request.user.is_authenticated} <<<") # <-- ADD THIS LINE
    print(f">>> Who is the user? {request.user} <<<") # <-- AND THIS LINE
    listings = Listing.objects.all().order_by('-id')[:6]
    return render(request, 'index.html', {'listings': listings})


# @login_required  # <-- ADDED: This line protects the homepage
# def index(request):
#     """
#     Renders the homepage with the 6 most recent listings.
#     """
#     listings = Listing.objects.all().order_by('-id')[:6]
#     return render(request, 'index.html', {'listings': listings})

def listing_list(request):
    """
    Renders a paginated page of all property listings.
    """
    listings_qs = Listing.objects.all().order_by('-id')
    paginator = Paginator(listings_qs, 9)
    page_number = request.GET.get('page')
    listings = paginator.get_page(page_number)
    return render(request, 'members/listing_list.html', {'listings': listings})

def listing_detail(request, listing_id):
    """
    Renders the detail page for a single property listing.
    """
    listing = get_object_or_404(Listing, id=listing_id)
    return render(request, 'members/listing_detail.html', {'listing': listing})

def booking_list(request):
    """
    Renders a list of all bookings. (Admin-style page)
    """
    bookings = Booking.objects.all().order_by('-id')
    return render(request, 'members/booking_list.html', {'bookings': bookings})

def booking_detail(request, booking_id):
    """
    Renders the detail page for a single booking.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'members/booking_detail.html', {'booking': booking})


# ==============================================================================
# USER AUTHENTICATION VIEWS
# ==============================================================================

def register_user(request):
    """
    Handles user registration. Creates a new User and redirects to login.
    """
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. You can now log in.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_user(request):
    """
    Handles user login using EMAIL instead of username.
    """
    if request.method == "POST":
        # Get email from either 'email' or 'username' field
        email = request.POST.get('email') or request.POST.get('username')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, 'login.html')
            
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            return redirect('index')
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, 'login.html')

def logout_user(request):
    """
    Handles user logout.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


# ==============================================================================
# BOOKING & USER-SPECIFIC VIEWS (Require Login)
# ==============================================================================

@login_required
def create_listing(request):
    """
    Handles the creation of a new listing by a host.
    """
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.status = "Available"
            listing.created_at = timezone.now().strftime("%Y-%m-%d")
            listing.save()
            
            # Handle image upload if provided
            image = form.cleaned_data.get('image')
            if image:
                ListingImage.objects.create(listing=listing, image=image)
                
            messages.success(request, "Your property has been listed successfully!")
            return redirect('listing_detail', listing_id=listing.id)
    else:
        form = ListingForm()
    
    return render(request, 'members/create_listing.html', {'form': form})

@login_required
def reserve_listing(request, listing_id):
    """
    Handles the reservation process via AJAX.
    Creates a booking for the logged-in user.
    Prevents duplicate bookings by checking for existing bookings with the same details.
    """
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        listing = get_object_or_404(Listing, id=listing_id)

        check_in_str = request.POST.get("check_in")
        check_out_str = request.POST.get("check_out")
        guests_str = request.POST.get("guests")

        if not all([check_in_str, check_out_str, guests_str]):
            return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)

        try:
            check_in_date = datetime.strptime(check_in_str, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(check_out_str, "%Y-%m-%d").date()
            guests = int(guests_str)

            if check_out_date <= check_in_date:
                return JsonResponse({'success': False, 'error': 'Check-out date must be after check-in date.'}, status=400)
            
            if check_in_date < timezone.now().date():
                return JsonResponse({'success': False, 'error': 'Check-in date cannot be in the past.'}, status=400)

            nights = (check_out_date - check_in_date).days
            total_price = nights * listing.price if listing.price else 0
            
            # Check for existing booking conflicts to prevent duplicates and overlaps
            # 1. Check for exact duplicate booking
            exact_duplicate = Booking.objects.filter(
                user=request.user,
                listing=listing,
                check_in=check_in_date,
                check_out=check_out_date,
                guests=guests
            ).exists()
            
            if exact_duplicate:
                return JsonResponse({'success': True, 'message': 'Booking already exists'})
            
            # 2. Check for date overlaps with existing bookings for the same listing
            # This prevents double booking the same room for overlapping dates
            overlapping_booking = Booking.objects.filter(
                listing=listing,
                check_in__lt=check_out_date,  # New booking ends after existing booking starts
                check_out__gt=check_in_date    # New booking starts before existing booking ends
            ).exists()
            
            if overlapping_booking:
                return JsonResponse({'success': False, 'error': 'This room is already booked for the selected dates. Please choose different dates.'}, status=400)
            
            # Create new booking only if it doesn't exist
            Booking.objects.create(
                user=request.user,
                listing=listing,
                check_in=check_in_date,
                check_out=check_out_date,
                guests=guests,
                total_price=total_price,
                status="Reserved",
            )

            return JsonResponse({'success': True})

        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid data format. Please check your inputs.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'An unexpected error occurred. Please try again.'}, status=500)

    return redirect("listing_detail", listing_id=listing_id)


@login_required
def my_bookings(request):
    """
    Renders a list of bookings for the currently logged-in user.
    Ensures no duplicate bookings are displayed by using distinct().
    """
    bookings = Booking.objects.filter(user=request.user).select_related("listing").order_by("-id").distinct()
    return render(request, "members/booking_list.html", {"bookings": bookings})

@login_required
def modify_booking(request, booking_id):
    """
    Allows a user to modify their booking dates and guest count.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == "POST":
        try:
            # Handle both AJAX and regular form submissions
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                check_in_date = datetime.strptime(request.POST.get('check_in'), '%Y-%m-%d').date()
                check_out_date = datetime.strptime(request.POST.get('check_out'), '%Y-%m-%d').date()
            else:
                check_in_date = datetime.strptime(request.POST.get('check_in'), '%Y-%m-%d').date()
                check_out_date = datetime.strptime(request.POST.get('check_out'), '%Y-%m-%d').date()
                
            guests = int(request.POST.get('guests', 1))
            
            # Validate dates
            if check_in_date >= check_out_date:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Check-out date must be after check-in date.'}, status=400)
                messages.error(request, 'Check-out date must be after check-in date.')
                return render(request, "members/modify_booking.html", {"booking": booking})
            
            # Calculate new price
            listing = booking.listing
            days = (check_out_date - check_in_date).days
            total_price = listing.price * days
            
            # Check for overlapping bookings (excluding this booking)
            overlapping_booking = Booking.objects.filter(
                listing=listing,
                check_in__lt=check_out_date,  # Existing booking starts before new booking ends
                check_out__gt=check_in_date   # Existing booking ends after new booking starts
            ).exclude(id=booking_id).exists()
            
            if overlapping_booking:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'These dates conflict with another booking. Please choose different dates.'}, status=400)
                messages.error(request, 'These dates conflict with another booking. Please choose different dates.')
                return render(request, "members/modify_booking.html", {"booking": booking})
            
            # Update booking
            booking.check_in = check_in_date
            booking.check_out = check_out_date
            booking.guests = guests
            booking.total_price = total_price
            booking.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            messages.success(request, 'Your booking has been updated successfully.')
            return redirect('my_bookings')
            
        except ValueError:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Invalid data format. Please check your inputs.'}, status=400)
            messages.error(request, 'Invalid data format. Please check your inputs.')
            return render(request, "members/modify_booking.html", {"booking": booking})
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': f'An unexpected error occurred: {str(e)}'}, status=500)
            messages.error(request, f'An unexpected error occurred: {str(e)}')
            return render(request, "members/modify_booking.html", {"booking": booking})
    
    # For GET requests, render the form
    return render(request, "members/modify_booking.html", {"booking": booking})

@login_required
def cancel_booking(request, booking_id):
    """
    Allows a user to cancel their booking.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == "POST":
        try:
            # Update booking status to Cancelled
            booking.status = "Cancelled"
            booking.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            messages.success(request, 'Your booking has been cancelled successfully.')
            return redirect('my_bookings')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': f'An unexpected error occurred: {str(e)}'}, status=500)
            messages.error(request, f'An unexpected error occurred: {str(e)}')
            return render(request, "members/cancel_booking.html", {"booking": booking})
    
    # For GET requests, confirm cancellation
    return render(request, "members/cancel_booking.html", {"booking": booking})
