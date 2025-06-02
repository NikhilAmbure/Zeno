from django.shortcuts import render,HttpResponse, redirect, get_object_or_404
from django.core.cache import cache
from django.contrib import messages
from .emailer import sendOTPToEmail
import random
from django.contrib.auth import get_user_model, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Product, CartItem, Order, WishlistItem
from django.contrib.postgres.search import (SearchQuery, SearchVector, SearchRank, TrigramSimilarity)
from django.db.models import Q
from decimal import Decimal

# Gets the custom user model
User = get_user_model()


# Create your views here.

@login_required(login_url='/login/')
def index(request):

    new_arrivals = Product.objects.filter(is_new=True)[:4]
    trending = Product.objects.filter(is_trending=True)[:4]
    top_rated = Product.objects.filter(is_top_rated=True)[:4]
    dotd = Product.objects.filter(dotd=True)[:2]
    new_products = Product.objects.filter(new_prod=True)[:12]
    best_sellers = Product.objects.filter(best_sellers=True)[:6]
    
    return render(request, 'index.html', {
        'new_arrivals': new_arrivals,
        'trending': trending,
        'top_rated': top_rated,
        'deal_of_the_day': dotd,
        'new_products': new_products,
        'best_sellers': best_sellers
    })


# Fulltext search
@login_required(login_url='/login/')
def search_results(request):
    search = request.GET.get('search', '').strip()
    results = []

    if search:
        vector = SearchVector('name', weight='A') + SearchVector('description', weight='B') + SearchVector('category__name', weight='C')
        query = SearchQuery(search)

        results = Product.objects.annotate(search=vector).filter(search=query)

    return render(request, 'search_results.html', {
        'results': results,
        'search': search,
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
        otp = random.randint(1000, 9999)
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
    cart_items = []
    total_price = 0

    # Always use session-based cart
    cart = request.session.get('cart', {})
    print("Session cart content:", cart)

    product_ids = [int(pid) for pid in cart.keys() if pid.isdigit()]
    products = Product.objects.filter(id__in=product_ids)

    for product in products:
        quantity = cart.get(str(product.id), 0)
        subtotal = product.price * quantity
        total_price += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }

    return render(request, 'cart.html', context)

# WishList Logic
@login_required(login_url='/login/')
def wishlist_view(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {
        'wishlist_items': wishlist_items
    })

@login_required(login_url='/login/')
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    WishlistItem.objects.get_or_create(user=request.user, product=product)
    messages.success(request, "Added to wishlist.")
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required(login_url='/login/')
def remove_from_wishlist(request, item_id):
    WishlistItem.objects.filter(id=item_id, user=request.user).delete()
    messages.success(request, "Removed from wishlist.")
    return redirect('wishlist')

@login_required(login_url='/login/')
def move_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Remove from wishlist
    WishlistItem.objects.filter(product=product, user=request.user).delete()
    # Add to cart
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, "Moved to cart.")
    return redirect('wishlist')

@login_required(login_url='/login/')
def clear_wishlist(request):
    WishlistItem.objects.filter(user=request.user).delete()
    messages.success(request, "Wishlist cleared.")
    return redirect('wishlist')

def wishlist_count(request):
    count = WishlistItem.get_count(request.user)
    return {'wishlist_count': count}


@login_required(login_url='/login/')
def edit_profile_view(request):

    user = request.user

    if request.method == "POST":

        if request.FILES.get('profile'):
            user.profile_picture = request.FILES['profile']
        print("Logged in user:", request.user.email)
        user.name = request.POST.get('name')
        user.username = request.POST.get('username')
        user.phone = request.POST.get('phone')
        user.location = request.POST.get('location')
        user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('edit-profile')

    user = User.objects.get(pk=request.user.pk)
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
                    cart[str(product_id)] = max(cart[str(product_id)] - 1, 1)

        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "Cart updated!")
        return redirect('cart')


# 1st
@login_required(login_url='/login/')
def checkout_page(request):
    cart = request.session.get('cart', {})
    # print("Checkout cart content:", cart)
    # print("Cart keys:", list(cart.keys()))

    if not cart:
        messages.error(request, 'Your cart is empty. Please add items to proceed to checkout.')
        return redirect('cart')

    products = Product.objects.filter(id__in = cart.keys())

    total_price = Decimal('0.00')
    cart_items = []

    for product in products:
        quantity = cart[str(product.id)]
        subtotal = product.price * quantity
        total_price += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    # Add GST (18%)
    gst_rate = Decimal('0.18')
    gst_amount = (total_price * gst_rate).quantize(Decimal('0.01'))  # round to 2 decimal places
    total_with_gst = total_price + gst_amount

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # Clearing old CartItems for this user
        CartItem.objects.filter(user=request.user).delete()

        # Save cart items into database as CartItem objects
        saved_items = []
        for item in cart_items:
            cart_item = CartItem.objects.create(
                user = request.user,
                product = item['product'],
                quantity = item['quantity']
            )
            saved_items.append(cart_item)

        # Create order
        order = Order.objects.create(
            user = request.user,
            total_price = total_with_gst,
            payment_method = 'COD', #Temporary is COD
            is_paid = False,
            name = name,
            email = email,
            phone = phone,
            address = address
        )

        order.items.set(saved_items)
        order.save()


        # Clearing the cart after order creation
        request.session['cart'] = {}
        request.session.modified = True

        # Redirect to payment selection page
        request.session['order_id'] = order.id # Save order id for payment  # For generating the receipt later
        return redirect('select_payment_method')
    

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'gst_amount': gst_amount,
        'total_with_gst': total_with_gst,
        'user_profile': request.user # To prefill the user details in form
    })



def select_payment_method(request):
    return render(request, 'select_payment_method.html')


def razorpay_payment(request):
    return render(request, 'razorpay.html')

def place_order_cod(request):
    return redirect('index')