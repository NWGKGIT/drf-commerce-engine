import hashlib
import hmac
import json

import requests
from django.conf import settings
from django.db import transaction

from apps.inventory.services import deduct_order_stock
from apps.orders.models import OrderStatus

from .models import Payment

CHAPA_API_URL = "https://api.chapa.co/v1"

class ChapaService:
    @staticmethod
    def get_headers():
        return {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json"
        }

    @staticmethod
    def initiate_payment(payment_instance, return_url):
        """
        Sends the initialization request to Chapa.
        Returns the checkout_url.
        """
        if not settings.CHAPA_SECRET_KEY:
            raise ValueError("Chapa secret key is not configured.")
        if not settings.BACKEND_URL:
            raise ValueError("Backend URL is not configured.")

        payload = {
            "amount": str(payment_instance.amount),
            "currency": payment_instance.currency,
            "email": payment_instance.order.user.email,
            "first_name": payment_instance.order.user.first_name or "User",
            "last_name": payment_instance.order.user.last_name or "Customer",
            "tx_ref": payment_instance.reference,
            "callback_url": f"{settings.BACKEND_URL}/api/payments/webhook/", # The webhook URL
            "return_url": return_url, # Where user goes after success
            "customization[title]": f"Order {payment_instance.order.order_number}",
            "customization[description]": "Payment for goods"
        }

        try:
            response = requests.post(
                f"{CHAPA_API_URL}/transaction/initialize",
                headers=ChapaService.get_headers(),
                json=payload,
                timeout=settings.CHAPA_REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                checkout_url = data.get('data', {}).get('checkout_url')
                if checkout_url:
                    return checkout_url
                raise ValueError("Chapa response did not include a checkout URL.")
            else:
                raise ValueError(f"Chapa Error: {data.get('message', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Connection Error: {str(e)}")
        except ValueError:
            raise
        except (KeyError, TypeError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid Chapa response: {str(e)}")

    @staticmethod
    def verify_payment(tx_ref):
        """
        Manually verify transaction status with Chapa
        """
        url = f"{CHAPA_API_URL}/transaction/verify/{tx_ref}"
        if not settings.CHAPA_SECRET_KEY:
            raise ValueError("Chapa secret key is not configured.")

        try:
            response = requests.get(
                url,
                headers=ChapaService.get_headers(),
                timeout=settings.CHAPA_REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Connection Error: {str(e)}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid Chapa response: {str(e)}")

    @staticmethod
    def verify_webhook_signature(request):
        """
        Verify the HMAC SHA256 signature from Chapa.
        """
        secret = settings.CHAPA_WEBHOOK_SECRET

        if not secret or secret == "placeholder-for-build":
            return False

        signature = request.headers.get('Chapa-Signature') or request.headers.get(
            'x-chapa-signature'
        )
        if not signature:
            return False

        body = request.body
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)


@transaction.atomic
def finalize_order(payment_reference, gateway_response=None):
    """
    Called by Webhook or Manual Verification when payment is SUCCESS.
    1. Updates Payment status
    2. Updates Order status
    """
    try:
        payment = Payment.objects.select_for_update().get(reference=payment_reference)
    except Payment.DoesNotExist:
        # Log error if needed
        return False

    if payment.status == Payment.PaymentStatus.SUCCESS:
        return True 
    order = payment.order
    if payment.status == Payment.PaymentStatus.CANCELLED or order.status == OrderStatus.CANCELLED:
        if gateway_response:
            payment.raw_response = gateway_response
        payment.save()
        return False

    if order.status not in [OrderStatus.PENDING_PAYMENT, OrderStatus.PAYMENT_FAILED]:
        if gateway_response:
            payment.raw_response = gateway_response
            payment.save(update_fields=["raw_response", "updated_at"])
        return True

    try:
        deduct_order_stock(order)
    except ValueError:
        payment.status = Payment.PaymentStatus.FAILED
        if gateway_response:
            payment.raw_response = gateway_response
        payment.save()
        order.status = OrderStatus.PAYMENT_FAILED
        order.save(update_fields=["status", "updated_at"])
        return False

    # Update Payment
    payment.status = Payment.PaymentStatus.SUCCESS
    if gateway_response:
        payment.raw_response = gateway_response
    payment.save()

    order.status = OrderStatus.PROCESSING
    order.save()

    return True
