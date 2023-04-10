from django.urls import path
from ..views.category_views import *
urlpatterns = [
    path('', CategoryList.as_view(), name='category_list_create'),
    path('<int:id>/', CategoryDetails.as_view(), name='category_details'),
]
