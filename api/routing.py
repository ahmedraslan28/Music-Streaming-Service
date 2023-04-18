from django.urls import path

from .consumers import NotificationConsumer


websocket_urlpatterns = [
    path('test/', NotificationConsumer.as_asgi()),
]
