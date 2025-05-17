from django.shortcuts import render,HttpResponse, redirect
from django.core.cache import cache
from django.contrib import messages
from .emailer import sendOTPToEmail
import random
from django.contrib.auth import get_user_model, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser


# Gets the custom user model
User = get_user_model()


# Create your views here.

@login_required(login_url='/login/')
def index(request):
    return render(request, 'index.html')


def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')


        # Rate Limiting
        if cache.get(email):
            data = cache.get(email)
            data['count'] += 1

            if data['count'] >= 3:
                cache.set(email, data, 60 * 5)
                messages.error(request, 'You can request OTP after 5min')
                return redirect('/login/')
            
            cache.set(email, data, 60 * 1)
        
        if not cache.get(email):
            data = {
                'email': email,
                'count': 1
            }
            cache.set(email, data, 60 * 1)

        
        
        user_obj = User.objects.filter(email = email)
        if not user_obj.exists():
            return redirect('/login/')
        
        email = user_obj[0].email
        otp = random.randint(0000, 9999)
        user_obj.update(otp = otp)
        subject = "OTP for login"
        message = f'Your OTP is {otp}'
        sendOTPToEmail(email, subject, message)

        return redirect(f'/enter_otp/{user_obj[0].id}/')

    return render(request, 'login.html')

def logout(request):
    auth_logout(request)
    return redirect('/login/')


def register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if pass1 != pass2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'register.html')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return render(request, 'register.html')


        user = CustomUser(username=username, email=email)
        user.set_password(pass1)  # Hash the password!
        user.save()

        messages.success(request, "Account created successfully. Please login.")
        return redirect('/login/')
        
    return render(request, 'register.html')


def enter_otp_page(request, user_id):

    if request.method == 'POST':
        user_obj = User.objects.get(id = user_id)

        # To protect the routes from hackers
        if cache.get(user_obj.username):
            data = cache.get(user_obj.username)

            if data['count'] >= 3:
                messages.error(request, "You can request OTP after 5min.")
                redirect('/login/')

        otp = request.POST.get('otp')

        if int(otp) == user_obj.otp:
            login(request, user_obj)
            return redirect('/')

        # Message error for wrong otp
        messages.error(request, "Invalid OTP")
        
        return redirect(f'/enter_otp/{user_obj.id}/')
    

    return render(request, 'enter_otp.html')