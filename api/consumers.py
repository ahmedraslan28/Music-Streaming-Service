from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json


class NotificationConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()
        self.username = "Raslan"
        self.send(text_data="[Welcome %s!]" % self.username)

    def receive(self, *, text_data):
        print(text_data)
        # self.send(text_data=self.username + ": " + text_data)

    def disconnect(self, message):
        print('closed')
