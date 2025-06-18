from django.shortcuts import render,HttpResponse, redirect, get_object_or_404
from django.core.cache import cache
from django.contrib import messages
from .emailer import sendOTPToEmail, send_order_receipt, send_order_cancellation_email
import random
from django.contrib.auth import get_user_model, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Product, CartItem, OrderItem, Order, WishlistItem
from django.contrib.postgres.search import (SearchQuery, SearchVector, SearchRank, TrigramSimilarity)
from django.db.models import Q
from decimal import Decimal
from django.utils import timezone
from django.conf import settings
from home.razorpay_handler import RazorPayPayment

# Gets the custom user model
User = get_user_model()


# Create your views here.

def index(request):

    new_arrivals = Product.objects.filter(is_new=True)[:6]
    trending = Product.objects.filter(is_trending=True)[:6]
    top_rated = Product.objects.filter(is_top_rated=True)[:6]
    dotd = Product.objects.filter(dotd=True)[:2]
    new_products = Product.objects.filter(new_prod=True)[:12]
    best_sellers = Product.objects.filter(best_sellers=True)[:6]
    dress_frock = Product.objects.filter(category__name='Dress').count()
    winter_wear = Product.objects.filter(category__name='Winter').count()
    glasses_lens = Product.objects.filter(category__name='Glasses').count()
    shorts_jeans = Product.objects.filter(category__name='Shorts & Jeans').count()
    t_shirts = Product.objects.filter(category__name='T-shirts').count()
    jackets = Product.objects.filter(category__name='Jackets').count()
    hats = Product.objects.filter(category__name='Hats').count()

    return render(request, 'index.html', {
        'new_arrivals': new_arrivals,
        'trending': trending,
        'top_rated': top_rated,
        'deal_of_the_day': dotd,
        'new_products': new_products,
        'best_sellers': best_sellers,
        'dress_frock': dress_frock,
        'winter_wear': winter_wear,
        'glasses_lens': glasses_lens,
        'shorts_jeans': shorts_jeans,
        't_shirts': t_shirts,
        'jackets': jackets,
        'hats': hats
    })


# Fulltext search
def search_results(request):
    search = request.GET.get('search', '').strip()
    results = []
    section = request.GET.get('section', '')

    if section:
        if section == 'new_arrivals':
            results = Product.objects.filter(is_new=True)
        elif section == 'trending':
            results = Product.objects.filter(is_trending=True)
        elif section == 'top_rated':
            results = Product.objects.filter(is_top_rated=True)
        elif section == 'new_products':
            results = Product.objects.filter(new_prod=True)
    elif search:
        vector = SearchVector('name', weight='A') + SearchVector('description', weight='B') + SearchVector('category__name', weight='C')
        query = SearchQuery(search)
        results = Product.objects.annotate(search=vector).filter(search=query)

    section_names = {
        'new_arrivals': 'New Arrivals',
        'trending': 'Trending Products',
        'top_rated': 'Top Rated Products',
        'new_products': 'New Products'
    }

    section_name = section_names.get(section, 'Search Results')

    return render(request, 'search_results.html', {
        'results': results,
        'search': search,
        'section': section,
        'section_name': section_name
    })


def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(email=email)
            if user.check_password(password):
                login(request, user)
                return redirect('/')
            else:
                messages.error(request, "Invalid password")
        except CustomUser.DoesNotExist:
            messages.error(request, "User does not exist")
        
        return redirect('/login/')

    return render(request, 'login.html')

def logout(request):
    auth_logout(request)
    return redirect('index')


def register_page(request):
    if request.method == 'POST':
        # Check if this is an OTP verification submission
        if 'otp' in request.POST:
            entered_otp = request.POST.get('otp')
            stored_otp = request.session.get('registration_otp')
            registration_data = request.session.get('registration_data')

            if not stored_otp or not registration_data:
                messages.error(request, "Registration session expired. Please try again.")
                return render(request, 'register.html')

            if int(entered_otp) == stored_otp:
                # Create the user
                user = CustomUser(
                    username=registration_data['username'],
                    email=registration_data['email']
                )
                user.set_password(registration_data['password'])
                user.save()

                # Clear session data
                del request.session['registration_data']
                del request.session['registration_otp']

                messages.success(request, "Account created successfully. Please login.")
                return redirect('login')
            else:
                messages.error(request, "Invalid OTP")
                return render(request, 'register.html')

        # This is the initial registration form submission
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

        # Store registration data in session
        request.session['registration_data'] = {
            'username': username,
            'email': email,
            'password': pass1
        }

        # Generate and send OTP
        otp = random.randint(1000, 9999)
        request.session['registration_otp'] = otp
        subject = "OTP for Registration"
        message = f'Your OTP for registration is {otp}'
        sendOTPToEmail(email, subject, message)

        messages.success(request, "Please enter the OTP sent to your email.")
        return render(request, 'register.html', {'show_otp': True})

    return render(request, 'register.html', {'show_otp': False})

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
    messages.success(request, f"{product.name} added to wishlist!")
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required(login_url='/login/')
def remove_from_wishlist(request, item_id):
    WishlistItem.objects.filter(id=item_id, user=request.user).delete()
    messages.success(request, "Item removed from wishlist!")
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
    messages.success(request, f"{product.name} moved to cart!")
    return redirect('wishlist')

@login_required(login_url='/login/')
def clear_wishlist(request):
    WishlistItem.objects.filter(user=request.user).delete()
    messages.success(request, "Wishlist cleared!")
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

    messages.success(request, f"{product.name} added to cart!")

    return redirect('product_detail', pk=product.id)


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "Item removed from cart!")

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
        quantity = int(cart[str(product.id)])
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
        # Create order directly from session cart
        order = Order.objects.create(
            user=request.user,
            total_price=total_with_gst,
            payment_method='COD',  # Default to COD, will update in payment method selection
            is_paid=False,
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            status='pending'
        )

        # Create order items directly without using CartItem model
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )

        # Clear the cart after successful order creation
        request.session['cart'] = {}
        request.session['order_id'] = str(order.id)
        request.session.modified = True

        messages.success(request, f'Order #{order.id} created successfully!')
        return redirect('select_payment_method')

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'gst_amount': gst_amount,
        'total_with_gst': total_with_gst,
        'user_profile': request.user
    })


# In your views.py
@login_required
def select_payment_method(request):
    order_id = request.session.get('order_id')
    if not order_id:
        messages.error(request, 'No order found. Please start checkout again.')
        return redirect('cart')

    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Invalid order. Please start checkout again.')
        return redirect('cart')

    return render(request, 'select_payment_method.html')


def razorpay_payment(request):
    order_id = request.session.get('order_id')
    if not order_id:
        messages.error(request, 'No order found. Please start checkout again.')
        return redirect('cart')

    try:
        order = Order.objects.get(id=order_id, user=request.user)

        # Calculate total amount with GST
        gst_rate = Decimal('0.18')
        gst_amount = (order.total_price * gst_rate).quantize(Decimal('0.01'))
        total_with_gst = order.total_price + gst_amount

        try:
            # Initialize RazorPay client
            razorpay_handler = RazorPayPayment()

            # Create Razorpay order with proper amount formatting
            razorpay_order = razorpay_handler.create_order(
                amount_in_inr=float(total_with_gst),
                receipt=f"order_{order.id}"
            )

            # Validate Razorpay response
            if not razorpay_order.get('id'):
                raise ValueError('Invalid response from Razorpay')

            # Save Razorpay order ID to session for verification later
            request.session['razorpay_order_id'] = razorpay_order['id']

            context = {
                'order': order,
                'total_amount': total_with_gst,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
                'razorpay_amount': razorpay_order['amount'],
                'currency': 'INR',
                'callback_url': request.build_absolute_uri('/handle-payment/'),
                'gst_amount': gst_amount
            }

            return render(request, 'razorpay.html', context)

        except (ValueError, KeyError) as e:
            messages.error(request, f'Invalid response from payment gateway: {str(e)}')
            return redirect('select_payment_method')
        except Exception as e:
            messages.error(request, f'Error initializing payment: {str(e)}')
            return redirect('select_payment_method')

    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('cart')
    except Exception as e:
        messages.error(request, f'Error retrieving order: {str(e)}')
        return redirect('cart')

@login_required
def handle_payment(request):
    if request.method != "POST":
        messages.error(request, 'Invalid request method')
        return redirect('cart')

    try:
        # Get the payment details from POST data
        payment_data = {
            'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
            'razorpay_order_id': request.POST.get('razorpay_order_id'),
            'razorpay_signature': request.POST.get('razorpay_signature')
        }

        # Validate required parameters
        if not all(payment_data.values()):
            messages.error(request, 'Missing payment parameters')
            return redirect('select_payment_method')

        # Get the order from session
        session_order_id = request.session.get('order_id')
        if not session_order_id:
            messages.error(request, 'No order found in session')
            return redirect('cart')

        # Verify session razorpay_order_id matches the one from callback
        session_razorpay_order_id = request.session.get('razorpay_order_id')
        if session_razorpay_order_id != payment_data['razorpay_order_id']:
            messages.error(request, 'Order ID mismatch')
            return redirect('cart')

        try:
            order = Order.objects.get(id=session_order_id, user=request.user)
        except Order.DoesNotExist:
            messages.error(request, 'Order not found')
            return redirect('cart')

        # Initialize Razorpay client and verify payment
        try:
            razorpay_handler = RazorPayPayment()
            razorpay_handler.verify_payment_signature(payment_data)
        except Exception as e:
            messages.error(request, f'Payment verification failed: {str(e)}')
            return redirect('select_payment_method')

        # Update order status
        order.payment_method = 'RAZORPAY'
        order.is_paid = True
        order.status = 'confirmed'
        order.save()

        try:
            # Send order confirmation email
            send_order_receipt(order)
        except Exception as e:
            # Log the error but don't stop the process
            print(f"Error sending order receipt: {str(e)}")

        # Clear all relevant session data
        session_keys = ['order_id', 'razorpay_order_id', 'cart']
        for key in session_keys:
            request.session.pop(key, None)
        request.session.modified = True

        messages.success(request, 'Payment successful! Your order has been confirmed.')
        return redirect('my-orders')

    except Exception as e:
        messages.error(request, f'Error processing payment: {str(e)}')
        return redirect('select_payment_method')

@login_required
def place_order_cod(request):
    if request.method == 'POST':
        order_id = request.session.get('order_id')
        if not order_id:
            messages.error(request, 'No order found in session')
            return redirect('cart')

        try:
            order = Order.objects.get(id=order_id, user=request.user)
            order.status = 'confirmed'
            order.payment_method = 'COD'
            order.save()

            # Send order receipt email
            try:
                send_order_receipt(order)
                messages.success(request, 'Order confirmation email sent!')
            except Exception as e:
                messages.warning(request, 'Order placed but email could not be sent.')

            # Clear session
            if 'order_id' in request.session:
                del request.session['order_id']
            if 'cart' in request.session:
                del request.session['cart']
            request.session.modified = True

            messages.success(request, f'Order #{order.id} placed successfully!')
            return redirect('my-orders')

        except Order.DoesNotExist:
            messages.error(request, 'Order not found in database')
            return redirect('cart')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('cart')

    return redirect('select_payment_method')

def blog_view(request):
    return render(request, 'blog.html')



@login_required(login_url='/login/')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')

    total_orders = orders.count()
    total_spent = sum(order.total_price for order in orders)

    orders_data = []

    for order in orders:
        order_items = order.order_items.all()

        items_data = []
        total_items = 0

        for item in order_items:
            items_data.append({
                'product': item.product,
                'quantity': item.quantity,
                'price': item.price,
                'subtotal': item.subtotal,
            })
            total_items += item.quantity

        order_data = {
            'order_id': order.id,
            'status': order.status.title(),
            'ordered_at': order.ordered_at,
            'items': items_data,
            'total_items': total_items,
            'payment_method': dict(Order.PAYMENT_CHOICES).get(order.payment_method, order.payment_method),
            'is_paid': order.is_paid,
            'total_price': order.total_price,
            'shipping_address': order.address,
            'name': order.name,
            'email': order.email,
            'phone': order.phone,
            'tracking_number': order.tracking_number,
        }

        orders_data.append(order_data)

    context = {
        'orders_data': orders_data,
        'total_orders': total_orders,
        'total_spent': total_spent,
    }

    return render(request, 'my_orders.html', context)


# Invoice
@login_required(login_url='/login/')
def generate_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Calculate GST and total with GST
    gst_rate = Decimal('0.18')
    gst_amount = (order.total_price * gst_rate).quantize(Decimal('0.01'))
    total_with_gst = order.total_price + gst_amount

    context = {
        'order': order,
        'gst_amount': gst_amount,
        'total_with_gst': total_with_gst,
    }

    return render(request, 'receipt.html', context)

@login_required(login_url='/login/')
def cancel_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Check if order can be cancelled
        if order.status not in ['pending', 'confirmed']:
            messages.error(request, 'This order cannot be cancelled.')
            return redirect('my-orders')

        try:
            # Update order status
            order.status = 'cancelled'
            order.save()

            # Send cancellation email
            cancellation_date = timezone.now()
            send_order_cancellation_email(order, cancellation_date)

            messages.success(request, f'Order #{order.id} has been cancelled successfully. A confirmation email has been sent.')

        except Exception as e:
            messages.error(request, f'Error cancelling order: {str(e)}')

        return redirect('my-orders')

    # If GET request, show confirmation page
    order = get_object_or_404(Order, id=order_id, user=request.user)