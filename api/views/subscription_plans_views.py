from rest_framework import generics, permissions

from ..models import SubscriptionPlan
from ..serializers import SubscriptionPlanSerializer
from ..permissions import *


class SubscriptionPlanList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser | IsReadyOnlyRequest]
    serializer_class = SubscriptionPlanSerializer
    queryset = SubscriptionPlan.objects.all()


class SubscriptionPlanDetails(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ['get', 'head', 'options', 'patch', 'delete']

    permission_classes = [permissions.IsAdminUser | IsReadyOnlyRequest]
    serializer_class = SubscriptionPlanSerializer
    queryset = SubscriptionPlan.objects.all()
    lookup_field = 'id'
