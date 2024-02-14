from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

class SignInForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", min_length=8, max_length=25, widget=forms.PasswordInput)


# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("users:login"))
    else:
        return HttpResponseRedirect(reverse("portfolio:index"))

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("portfolio:index"))
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)      
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("users:index"))
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
        print("email: ", email)
        password = request.POST["password"]  
        User = get_user_model()
        user = User.objects.create_user(email=email, password=password)
        user.save()
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("portfolio:index"))
        else:
            return render(request, "users/signup.html", {
                "message": "Unable to sign up user",
                "form": SignInForm()
            })

    return render(request, "users/signup.html", {
        "form": SignInForm()
    })