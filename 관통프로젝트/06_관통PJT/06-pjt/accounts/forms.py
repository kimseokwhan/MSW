from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'last_name', 'first_name', 'gender', 'age', 'weekly_reading_time', 'yearly_reading_amount', 'profile_image', 'favorite_categories')
        widgets = {
            'favorite_categories': forms.CheckboxSelectMultiple(),
        }

class CustomUserChangeForm(UserChangeForm):
    password = None
    class Meta:
        model = User
        fields = ('email', 'last_name', 'first_name', 'gender', 'age', 'weekly_reading_time', 'yearly_reading_amount', 'profile_image', 'favorite_categories')
        widgets = {
            'favorite_categories': forms.CheckboxSelectMultiple(),
        }