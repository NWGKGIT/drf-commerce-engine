from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import logging
from drf_spectacular.utils import extend_schema
from .models import Payment
from orders.models import Order
from .serializers import PaymentSerializer, PaymentInitiateSerializer
from .services import ChapaService, finalize_order
from django.http import HttpResponse, HttpResponseRedirect 
logger = logging.getLogger(__name__)
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class PaymentViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializer

    @action(detail=False, methods=["post"])
    def initiate(self, request):
        serializer = PaymentInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data["order_id"]
        return_url = serializer.validated_data["return_url"]
        order = Order.objects.get(id=order_id)

        # Create Local Payment Record
        payment = Payment.objects.create(
            order=order, amount=order.total_amount, currency=order.currency or "ETB"
        )

        # Call Chapa
        try:
            checkout_url = ChapaService.initiate_payment(payment, return_url)
            return Response(
                {
                    "payment_id": payment.id,
                    "tx_ref": payment.reference,
                    "checkout_url": checkout_url,
                }
            )
        except ValueError as e:
            payment.status = Payment.PaymentStatus.FAILED
            payment.save()
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def verify(self, request):
        """
        Frontend calls this after returning from Chapa to confirm status
        """
        tx_ref = request.query_params.get("tx_ref")
        if not tx_ref:
            return Response({"detail": "tx_ref required"}, status=400)

        # Check local DB first
        payment = get_object_or_404(Payment, reference=tx_ref)

        if payment.status == Payment.PaymentStatus.SUCCESS:
            return Response({"status": "success"})

        # If not successful locally, ask Chapa
        try:
            data = ChapaService.verify_payment(tx_ref)
            if (
                data.get("status") == "success"
                and data.get("data", {}).get("status") == "success"
            ):
                finalize_order(tx_ref, gateway_response=data)
                return Response({"status": "success"})
            else:
                return Response({"status": "pending_or_failed"})
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    @action(detail=False, methods=["post"])
    def cancel(self, request):
        """
        Cancel a pending payment intent manually.
        POST /api/payments/cancel/ body={"tx_ref": "..."}
        """
        tx_ref = request.data.get("tx_ref")
        if not tx_ref:
            return Response({"detail": "tx_ref required"}, status=400)

        payment = get_object_or_404(Payment, reference=tx_ref)

        # User must own the order attached to the payment
        if payment.order.user != request.user and not request.user.is_staff:
            return Response({"detail": "Not authorized."}, status=403)

        if payment.status == Payment.PaymentStatus.SUCCESS:
            return Response(
                {"detail": "Cannot cancel a successful payment."}, status=400
            )

        payment.status = Payment.PaymentStatus.CANCELLED
        payment.save()

        return Response({"status": "Payment cancelled"})

@method_decorator(csrf_exempt, name='dispatch')
class ChapaWebhookView(APIView):
    """
    Receives events from Chapa server-to-server.
    No authentication required (Public), but verified via Signature.
    """

    permission_classes = []
    authentication_classes=[]
    @extend_schema(
        responses={200: None},  # Tells Swagger it returns an empty success response
        description="Endpoint for Chapa payment webhooks",
    )
    def post(self, request):
        logger.info(f"HEADERS: {request.headers}")
        logger.info(f"BODY: {request.body.decode('utf-8')}")
        # Verify Signature
        if not ChapaService.verify_webhook_signature(request):
            logger.error("WEBHOOK ERROR: Signature Mismatch")
            return Response(status=status.HTTP_403_FORBIDDEN)
        # Parse Payload
        try:
            data = request.data
            tx_ref = data.get("tx_ref")
            if not tx_ref:
                tx_ref = data.get("data", {}).get("tx_ref")
                
            if tx_ref:
                # We double check with verify API to be absolutely sure before releasing goods
                verification = ChapaService.verify_payment(tx_ref)
                if verification.get("status") == "success":
                    finalize_order(tx_ref, gateway_response=data)
                    logger.info(f"WEBHOOK SUCCESS: Order {tx_ref} completed.")
                    return Response(status=status.HTTP_200_OK)

            return Response(status=status.HTTP_200_OK)  # Ack even if ignored

        except Exception as e:
            logger.error(f"Webhook Error: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get(self, request):
        """
        Handles the user redirecting back to the site.
        """
        tx_ref = request.query_params.get("trx_ref") or request.query_params.get("tx_ref")
        status = request.query_params.get("status")

        if status == "success" and tx_ref:
            # Sync the order immediately so the user sees "Completed" on their screen
            finalize_order(tx_ref)
            return HttpResponse(f"<h1>Payment Successful!</h1><p>Order {tx_ref} is being processed.</p>")
        
        return HttpResponse("<h1>Payment Pending</h1><p>We are verifying your payment.</p>")