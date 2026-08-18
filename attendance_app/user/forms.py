from django import forms
from django.contrib.auth.hashers import make_password

from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput()
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput()
    )
    class Meta:
        model = User
        fields = [
            "employee_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "department",
            "designation",
            "gender",
            "joining_date",
            "password"
        ]

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password != confirm:
            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data

    def save(self, commit=True):

        user = super().save(commit=False)

        user.password = make_password(
            self.cleaned_data["password"]
        )

        if commit:
            user.save()

        return user

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(
        widget=forms.PasswordInput()
    )