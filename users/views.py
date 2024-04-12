from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import EditUserForm, SignInForm

# class SignInForm(forms.Form):
#     email = forms.EmailField(label="Email")
#     password = forms.CharField(label="Password", min_length=8, max_length=25, widget=forms.PasswordInput)

def validate_password(password):
    if len(password) < 8:
        raise ValidationError(gettext_lazy("Password must be at least 8 characters long."), code='password_too_short')
    if not any(char.isdigit() for char in password):
        raise ValidationError(gettext_lazy("Password must contain at least one number."), code='password_no_number')
    if not any(char.isupper() for char in password):
        raise ValidationError(gettext_lazy("Password must contain at least one uppercase letter."), code='password_no_uppercase')

# Create your views here.
@login_required
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("users:login"))
    else:
        user = request.user
        if request.method == 'POST':
            form = EditUserForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                return redirect('home')  # Replace 'home' with the name of your homepage URL pattern
        else:
            form = EditUserForm(instance=user)
        return render(request, 'users/index.html', {'form': form})
        # return render(request, "users/index.html")
        # return HttpResponseRedirect(reverse("users:index"))

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("portfolio:index"))
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)      
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("portfolio:index"))
        else:
            return render(request, "users/login.html", {
                "message": "Invalid credentials.",
                "form": SignInForm()
            })

    return render(request, "users/login.html", {
        "form": SignInForm()
    })

def logout_view(request):
    logout(request)
    return render(request, "users/login.html", {
        "form": SignInForm()
    })

def signup_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("portfolio:index"))
    if request.method == "POST":
        email = request.POST["email"].lower()
        password = request.POST["password"]  

        try:
            validate_password(password)
        except ValidationError as e:
            return render(request, "users/signup.html", {
                "message": e.message,
                "form": SignInForm()
            })
        
        User = get_user_model()
        try:
            user = User.objects.create_user(email=email, password=password)
            login(request, user)
            return HttpResponseRedirect(reverse("portfolio:index"))
        except Exception as e:
            return render(request, "users/signup.html", {
                "message": "Something went wrong",
                "form": SignInForm()
            })

    return render(request, "users/signup.html", {
        "form": SignInForm()
    })