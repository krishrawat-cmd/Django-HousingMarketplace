from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Listing, Booking, Review, Message, Payment, Favorite, ListingImage

# ==============================================================================
# CORRECTED USER ADMIN
# ==============================================================================
# We now inherit from BaseUserAdmin to get all the standard user management features.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # The fields to display in the user list view.
    # We replace 'created_at' with 'date_joined' from AbstractUser.
    list_display = ('email', 'name', 'phone', 'user_type', 'is_staff', 'date_joined')
    
    # The fields to filter the user list by.
    # We replace 'created_at' with 'date_joined'.
    list_filter = ('date_joined', 'is_staff', 'is_superuser', 'user_type')
    
    # The fields to search for users by.
    search_fields = ('email', 'name')
    
    # The default ordering.
    ordering = ('email',)
    
    # This configures the layout of the user change form.
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'phone', 'user_type', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # This configures the layout of the "add user" form.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )

# ==============================================================================
# ADMIN FOR OTHER MODELS (NO CHANGES NEEDED)
# ==============================================================================
# These are fine as they are.

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'price', 'city', 'state', 'created_at')
    list_filter = ('city', 'state', 'status')
    search_fields = ('title', 'description', 'address', 'city', 'state')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'listing', 'check_in', 'check_out', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__name', 'listing__title')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'listing', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__name', 'listing__title', 'comment')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('sender__name', 'receiver__name', 'content')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('payment_method', 'status', 'created_at')
    search_fields = ('booking__user__name',)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'listing', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__name', 'listing__title')

@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'image_url')
    search_fields = ('listing__title',)