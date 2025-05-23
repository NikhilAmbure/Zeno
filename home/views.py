from django.shortcuts import render,HttpResponse, redirect, get_object_or_404
from django.core.cache import cache
from django.contrib import messages
from .emailer import sendOTPToEmail
import random
from django.contrib.auth import get_user_model, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Product, CartItem

# Gets the custom user model
User = get_user_model()


# Create your views here.

@login_required(login_url='/login/')
def index(request):

    # print("Current session user:", request.user.email) #debug (ignore for now)

    new_arrivals = Product.objects.filter(is_new=True)[:4]
    trending = Product.objects.filter(is_trending=True)[:4]
    top_rated = Product.objects.filter(is_top_rated=True)[:4]
    dotd = Product.objects.filter(dotd=True)[:2]
    new_products = Product.objects.filter(new_prod=True)[:12]
    
    return render(request, 'index.html', {
        'new_arrivals': new_arrivals,
        'trending': trending,
        'top_rated': top_rated,
        'deal_of_the_day': dotd,
        'new_products': new_products,
    })


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



# To show the cart items

def cart_view(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())

    cart_items = []
    total_price = 0
    for product in products:
        quantity = cart[str(product.id)]
        total_price += product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': product.price * quantity
        })

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'cart.html', context)


def wishlist_view(request):
    return render(request, 'wishlist.html')


@login_required(login_url='/login/')
def edit_profile_view(request):

    user = request.user

    if request.method == "POST":

        if request.FILES.get('profile'):
            user.profile_picture = request.FILES['profile']
        print("Logged in user:", request.user.email)
        user.username = request.POST.get('username')
        user.phone = request.POST.get('phone')
        user.location = request.POST.get('location')
        user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('edit-profile')

    return render(request, 'edit_profile.html', {'user': user})



def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})


# To add the items into cart
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get cart session , or initialize empty dict
    cart = request.session.get('cart', {})

    # Add product to cart
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    # Save cart back to session
    request.session['cart'] = cart 
    request.session.modified = True

    messages.success(request, f"Added to cart!")

    return redirect('product_detail', pk=product.id)


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart')



# Increase or decrease the quantity
def update_cart_quantity(request, product_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        cart = request.session.get('cart', {})

        product_id_str = str(product_id)
        if product_id_str in cart:
            if action == 'increase':
                cart[product_id_str] += 1
            elif action == 'decrease':
                if cart[product_id_str] > 1:
                    cart[product_id_str] -= 1
                else:
                    del cart[product_id_str]

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart')
