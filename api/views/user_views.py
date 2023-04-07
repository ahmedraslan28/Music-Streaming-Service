from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

import stripe

from ..serializers import UserSerializer
from ..models import (SubscriptionPlan, User_SubscriptionPlan)

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY


# add permissions
class UsersList(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_artist=False, is_active=True)\
        .only('profile_image', 'first_name', 'last_name', 'username', 'followers_count',
              'email', 'is_premium', 'is_male', 'birth_date')
    # permission_classes = [IsAdminUser]


class UsersDetail(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_artist=False, is_active=True)\
        .only('first_name', 'last_name', 'username', 'followers_count',
              'email', 'is_premium', 'is_male', 'birth_date', 'profile_image')
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]


class UserProfile(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = UserSerializer

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        self.queryset = self.request.user
        return self.queryset

    def get(self, request):
        obj = self.get_queryset()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def patch(self, request):
        obj = self.get_queryset()
        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def checkout(request, plan_id):
    if request.user.is_premium:
        return Response({"message": "your are already a premium user"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    try:
        plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(plan.price * 100),
                        'product_data': {
                            'name': plan.name + " plan"
                        }
                    },
                    'quantity': 1
                }
            ],
            metadata={
                "user": request.user.id,
                "plan": plan.id
            },
            mode='payment',
            success_url='http://127.0.0.1:8000/api/users/upgrade/success/',
            cancel_url='http://127.0.0.1:8000/api/users/upgrade/cancel/',
        )
    except Exception as e:
        return Response({"message": f"{str(e)}"}, status=400)

    return redirect(checkout_session.url)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def success(request):
    return Response({"message": "congratulations your account upgraded successfuly"}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cancel(request):
    return Response({"message": "the payment canceled successfuly"}, status=200)


@csrf_exempt
@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_KEY
        )
    except ValueError as e:
        # Invalid payload
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return Response(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user']
        plan_id = session['metadata']['plan']
        user = User.objects.get(pk=user_id)
        user.is_premium = True
        user.save()

        end_date = timezone.now() + timezone.timedelta(days=30)
        User_SubscriptionPlan.objects.create(
            user_id=user_id, plan_id=plan_id, end_date=end_date)

    return Response(status=200)
