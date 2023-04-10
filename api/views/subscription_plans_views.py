from rest_framework import generics

from ..models import SubscriptionPlan
from ..serializers import SubscriptionPlanSerializer


class SubscriptionPlanList(generics.ListCreateAPIView):
    serializer_class = SubscriptionPlanSerializer
    queryset = SubscriptionPlan.objects.all()


class SubscriptionPlanDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubscriptionPlanSerializer
    queryset = SubscriptionPlan.objects.all()
    lookup_field = 'id'
