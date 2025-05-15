from django.shortcuts import render,HttpResponse

# Create your views here.


def index(request):
    return render(request, 'index.html')


def login(request):
    return render(request, 'login.html')

def logout(request):
    return HttpResponse("logged out")


def register_page(request):
    return render(request, 'register.html')


def enter_otp_page(request):
    return render(request, 'enter_otp')