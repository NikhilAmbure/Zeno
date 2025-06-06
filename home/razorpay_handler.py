import razorpay
from django.conf import settings
from decimal import Decimal

class RazorPayPayment:

    def __init__(self, currency="INR"):
        # Client initialization with proper settings
        self.client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )
        self.currency = currency 

    def create_order(self, amount_in_inr, receipt):
        """
        Create a Razorpay order
        :param amount_in_inr: Amount in INR (will be converted to paise)
        :param receipt: Receipt number/ID
        :return: Razorpay order object
        """
        try:
            # Convert amount to paise (Razorpay expects amount in smallest currency unit)
            amount_in_paise = int(Decimal(str(amount_in_inr)) * 100)
            
            order_data = {
                "amount": amount_in_paise,
                "currency": self.currency,
                "receipt": receipt,
                "payment_capture": 1  # Auto capture payment
            }
            
            order = self.client.order.create(data=order_data)
            return order
        except Exception as e:
            raise Exception(f"Error creating Razorpay order: {str(e)}")

    def verify_payment_signature(self, payment_data):
        """
        Verify the payment signature
        :param payment_data: Dictionary containing razorpay_payment_id, razorpay_order_id, and razorpay_signature
        :return: Boolean indicating if signature is valid
        """
        try:
            return self.client.utility.verify_payment_signature(payment_data)
        except Exception as e:
            raise Exception(f"Error verifying payment signature: {str(e)}")


if __name__ == "__main__":
    payment = RazorPayPayment("INR")
    payment.process_payment(100, "test_receipt_001")





