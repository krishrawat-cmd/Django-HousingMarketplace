from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Listing

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "name", "password1", "password2"]
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Set username to email to satisfy the unique constraint
        if commit:
            user.save()
        return user

class ListingForm(forms.ModelForm):
    image = forms.ImageField(required=False, help_text="Upload an image of your property")
    
    class Meta:
        model = Listing
        fields = ['title', 'description', 'price', 'address', 'city', 'state', 'zipcode', 
                 'room_type', 'available_from', 'available_to']
        widgets = {
            'available_from': forms.DateInput(attrs={'type': 'date'}),
            'available_to': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required except for image
        for field_name, field in self.fields.items():
            if field_name != 'image':
                field.required = True