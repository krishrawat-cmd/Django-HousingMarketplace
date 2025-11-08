from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError

# ==============================================================================
# CUSTOM USER MANAGER
# ==============================================================================
# This manager knows how to create users and superusers using email instead of username.
class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


# ==============================================================================
# CORRECTED USER MODEL
# ==============================================================================
class User(AbstractUser):
    # --- Your Custom Fields ---
    name = models.CharField(max_length=50)
    phone = models.BigIntegerField(null=True, blank=True)
    user_type = models.CharField(max_length=50, null=True, blank=True)
    profile_picture = models.CharField(max_length=500, null=True, blank=True)
    
    # --- Django Auth Configuration ---
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    # --- Tell the model to use our custom manager ---
    objects = CustomUserManager()

    def __str__(self):
        return self.email

# ==============================================================================
# ALL OTHER MODELS (NO CHANGES NEEDED)
# ==============================================================================
class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=50, null=True, blank=True)
    price = models.BigIntegerField(null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    zipcode = models.BigIntegerField(null=True, blank=True)
    latitude = models.BigIntegerField(null=True, blank=True)
    longitude = models.BigIntegerField(null=True, blank=True)
    room_type = models.CharField(max_length=50, null=True, blank=True)
    available_from = models.DateField(null=True, blank=True)
    available_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return self.title or f"Listing {self.id}"

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image_url = models.CharField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to='listing_images/', null=True, blank=True)
    
    def __str__(self):
        return f"Image for {self.listing}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    check_in = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)
    guests = models.IntegerField(null=True, blank=True)
    total_price = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateField(null=True, blank=True, default=timezone.now)
    
    class Meta:
        # Prevent duplicate bookings at database level
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'listing', 'check_in', 'check_out'],
                name='unique_booking_per_user_listing_dates'
            )
        ]
    
    def __str__(self):
        return f"{self.user} booked {self.listing}"
    
    def clean(self):
        # Validate that check_out is after check_in
        if self.check_in and self.check_out and self.check_out <= self.check_in:
            raise ValidationError('Check-out date must be after check-in date.')
        
        # Validate no overlapping bookings for the same listing
        if self.check_in and self.check_out and self.listing:
            overlapping = Booking.objects.filter(
                listing=self.listing,
                check_in__lt=self.check_out,
                check_out__gt=self.check_in
            ).exclude(pk=self.pk)
            
            if overlapping.exists():
                raise ValidationError('This room is already booked for the selected dates.')
        
        super().clean()

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    created_at = models.DateField(null=True, blank=True, default=timezone.now)
    
    def __str__(self):
        return f"{self.user} favorited {self.listing}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(null=True, blank=True)
    created_at = models.DateField(null=True, blank=True, default=timezone.now)
    
    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.BigIntegerField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateField(null=True, blank=True, default=timezone.now)
    
    def __str__(self):
        return f"Payment for {self.booking}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateField(null=True, blank=True, default=timezone.now)
    
    def __str__(self):
        return f"Review by {self.user} for {self.listing}"
