from django.urls import path
from ..views.subscription_plans_views import *
urlpatterns = [
    path('', SubscriptionPlanList.as_view(), name='subscription_plans_list'),
    path('<int:id>/', SubscriptionPlanDetails.as_view(),
         name='subscription_plans_list'),
]
