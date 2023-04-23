from channels.generic.websocket import AsyncWebsocketConsumer
import json


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.id = self.scope['url_route']['kwargs']['id']
        self.reciever_id = self.scope['url_route']['kwargs']['reciever_id']
        self.group_name = f"{self.reciever_id}"
        await self.channel_layer.group_add(
            self.group_name, self.channel_name
        )
        await self.accept()
        await self.send("succeffuly connected")

    async def send_follow_notification(self, event):
        data = json.dumps(event)
        await self.send(text_data=data)
