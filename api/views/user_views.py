from django.contrib.auth.decorators import login_required
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.urls import reverse

import stripe

from ..serializers import UserSerializer
from ..models import SubscriptionPlan

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY


# add permissions
class UsersList(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_artist=False)
    # permission_classes = [IsAdminUser]


class UsersDetail(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_artist=False)
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]


class UserProfile(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = UserSerializer

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        self.queryset = get_object_or_404(User, pk=self.request.user.id)
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


# class checkout(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, plan_id):
#         stripe.api_key = settings.STRIPE_SECRET_KEY
#         try:
#             plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
#             product_id = settings.PRODUCT_KEY
#             price = stripe.Price.create(
#                 unit_amount=int(plan.price * 100),
#                 currency='usd',
#                 product=product_id,
#                 recurring=None,
#             )
#             checkout_session = stripe.checkout.Session.create(
#                 line_items=[
#                     {
#                         'price': price.id,
#                         'quantity': 1,
#                     },
#                 ],
#                 mode='payment',
#                 success_url='http://127.0.0.1:8000/admin',
#                 cancel_url='http://127.0.0.1:8000/admin',
#             )
#         except Exception as e:
#             return Response({"message": f"{str(e)}"}, status=400)
#         return redirect(checkout_session.url)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def checkout(request, plan_id):
    try:
        plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=request.user.id if request.user.is_authenticated else None,
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
            mode='payment',
            success_url='http://127.0.0.1:8000/admin',
            cancel_url='http://127.0.0.1:8000/admin',
        )
    except Exception as e:
        return Response({"message": f"{str(e)}"}, status=400)

    return redirect(checkout_session.url)


def success(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
    message = {
        "message": "congratulations your account upgraded successfuly",
        "plan name": f"{plan.name}",
        "features": f"{plan.description}"
    }

    return Response(message, status=200)


def failed(request, plan_id):
    message = {
        "message": "the payment failed please try again",
    }

    return Response(message, status=status.HTTP_400_BAD_REQUEST)
