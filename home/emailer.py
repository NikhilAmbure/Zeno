from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from decimal import Decimal

def sendOTPToEmail(email, subject, message):
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

def send_order_receipt(order):
    subject = f'Order Confirmation - Order #{order.id}'
    from_email = settings.EMAIL_HOST_USER
    to_email = [order.email]

    # Calculate GST and total with GST
    gst_rate = Decimal('0.18')
    gst_amount = (order.total_price * gst_rate).quantize(Decimal('0.01'))
    total_with_gst = order.total_price + gst_amount

    # Prepare context for email template
    context = {
        'order': order,
        'gst_amount': gst_amount,
        'total_with_gst': total_with_gst,
    }

    # Render HTML content
    html_content = render_to_string('email_receipt.html', context)
    text_content = strip_tags(html_content)  # Plain text version of email

    # Create email
    email = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        to_email
    )
    
    # Attach HTML content
    email.attach_alternative(html_content, "text/html")
    
    # Send email
    email.send()

def send_order_cancellation_email(order, cancellation_date):
    subject = f'Order Cancellation Confirmation - Order #{order.id}'
    from_email = settings.EMAIL_HOST_USER
    to_email = [order.email]

    # Prepare context for email template
    context = {
        'order': order,
        'cancellation_date': cancellation_date,
    }

    # Render HTML content
    html_content = render_to_string('email_order_cancelled.html', context)
    text_content = strip_tags(html_content)  # Plain text version of email

    # Create email
    email = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        to_email
    )
    
    # Attach HTML content
    email.attach_alternative(html_content, "text/html")
    
    # Send email
    email.send()