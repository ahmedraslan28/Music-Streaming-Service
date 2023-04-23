from django.urls import path

from .consumers import NotificationConsumer


websocket_urlpatterns = [
    path('notification/<int:id>/<int:reciever_id>/',
         NotificationConsumer.as_asgi()),
]
