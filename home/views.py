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
                return redirect('/login/')
            
            data['count'] += 1
            cache.set(user_obj.username, data, 60 * 5)
        else:
            data = {'count': 1}
            cache.set(user_obj.username, data, 60 * 5)

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
    total_price = Decimal('0.00')

    # Always use session-based cart
    cart = request.session.get('cart', {})

    # Convert string keys to integers for product lookup
    product_ids = [int(pid) for pid in cart.keys() if pid.isdigit()]
    products = Product.objects.filter(id__in=product_ids)

    for product in products:
        quantity = int(cart.get(str(product.id), 0))  # Ensure quantity is an integer
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
    if not request.user.is_authenticated:
        return {'wishlist_count': 0}
    count = WishlistItem.get_count(request.user)
    return {'wishlist_count': count}


@login_required(login_url='/login/')
def edit_profile_view(request):

    user = request.user

    if request.method == "POST":
        # Validate username uniqueness if changed
        new_username = request.POST.get('username', '').strip()
        if new_username != user.username:
            if User.objects.filter(username=new_username).exists():
                messages.error(request, 'This username is already taken.')
                return redirect('edit-profile')

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
            current_quantity = int(cart[product_id_str])
            if action == 'increase':
                cart[product_id_str] = current_quantity + 1
            elif action == 'decrease':
                if current_quantity > 1:
                    cart[product_id_str] = current_quantity - 1
                else:
                    del cart[product_id_str]  # Remove item if quantity would be 0

        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "Cart updated!")
        return redirect('cart')
    return redirect('cart')  # Handle non-POST requests


# 1st
# Fixed checkout_page view in views.py

@login_required(login_url='/login/')
def checkout_page(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.error(request, 'Your cart is empty. Please add items to proceed to checkout.')
        return redirect('cart')

    # Convert string keys to integers for proper filtering
    product_ids = [int(pid) for pid in cart.keys() if pid.isdigit()]
    products = Product.objects.filter(id__in=product_ids)

    total_price = Decimal('0.00')
    cart_items = []

    for product in products:
        quantity = int(cart[str(product.id)])  # Ensure quantity is integer
        subtotal = product.price * quantity
        total_price += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    # Add GST (18%)
    gst_rate = Decimal('0.18')
    gst_amount = (total_price * gst_rate).quantize(Decimal('0.01'))
    total_with_gst = total_price + gst_amount

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # Create order FIRST
        order = Order.objects.create(
            user=request.user,
            total_price=total_with_gst,
            payment_method='COD',  # Temporary is COD
            is_paid=False,
            name=name,
            email=email,
            phone=phone,
            address=address
        )

        # Clear old CartItems for this user 
        CartItem.objects.filter(user=request.user).delete()

        # Create CartItem objects and associate with order
        saved_items = []
        for item in cart_items:
            cart_item = CartItem.objects.create(
                user=request.user,
                product=item['product'],
                quantity=item['quantity']
            )
            saved_items.append(cart_item)

        # Associate CartItems with the order AFTER both are saved
        order.items.set(saved_items)

        # Clear the cart after successful order creation
        request.session['cart'] = {}
        request.session.modified = True

        # Save order id for payment processing
        request.session['order_id'] = order.id
        
        messages.success(request, f'Order #{order.id} created successfully!')
        
        return redirect('select_payment_method')

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'gst_amount': gst_amount,
        'total_with_gst': total_with_gst,
        'user_profile': request.user
    })



def select_payment_method(request):
    return render(request, 'select_payment_method.html')


def razorpay_payment(request):
    return render(request, 'razorpay.html')

@login_required(login_url='/login/')
def place_order_cod(request):
    if request.method != 'POST':
        messages.error(request, 'Invalid request method')
        return redirect('select_payment_method')

    order_id = request.session.get('order_id')
    if not order_id:
        messages.error(request, 'No order found')
        return redirect('cart')

    try:
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Update order status and payment method
        order.status = 'confirmed'
        order.payment_method = 'COD'
        order.save()

        # Clear session data
        if 'order_id' in request.session:
            del request.session['order_id']
        request.session.modified = True

        messages.success(request, 'Your order has been placed successfully! You can track it in My Orders.')
        return redirect('my-orders')

    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('cart')
    except Exception as e:
        messages.error(request, f'Error processing order: {str(e)}')
        return redirect('cart')

def blog_view(request):
    return render(request, 'blog.html')



@login_required(login_url='/login/')
def my_orders(request):
    """View to display user's orders with all required data for template"""
    
    # Get all orders for the current user
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    
    # Calculate totals for hero section
    total_orders = orders.count()
    total_spent = sum(order.total_price for order in orders)
    
    # Prepare orders data for template
    orders_data = []
    
    for order in orders:
        # Get all cart items for this order
        cart_items = order.items.all()
        
        # Prepare items data
        items_data = []
        total_items = 0
        
        for item in cart_items:
            items_data.append({
                'product': item.product,
                'quantity': item.quantity,
                'price': item.product.price,
                'subtotal': item.total_price,  # This uses the property from CartItem model
            })
            total_items += item.quantity
        
        # Prepare order data
        order_data = {
            'order_id': order.id,
            'status': order.status.title(),  
            'ordered_at': order.ordered_at,
            'items': items_data,
            'total_items': total_items,
            'payment_method': dict(Order.PAYMENT_CHOICES).get(order.payment_method, order.payment_method),
            'is_paid': order.is_paid,
            'total_price': order.total_price,
            'shipping_address': order.address,  # Using the address field from Order model
            'name': order.name,
            'email': order.email,
            'phone': order.phone,
            'tracking_number': getattr(order, 'tracking_number', None),
        }
        
        orders_data.append(order_data)
    
    context = {
        'orders_data': orders_data,
        'total_orders': total_orders,
        'total_spent': total_spent,
    }
    
    return render(request, 'my_orders.html', context)