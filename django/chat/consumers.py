# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import ClickTracker
from django.db.models import F
from channels.db import database_sync_to_async
from django.db.models import Sum


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        self.model = await self.create_player()

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        total = await self.count_total()

        await self.send(text_data=json.dumps({"message": total}))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, bytes_data):
        # print(text_data)
        print(json.loads(bytes_data.decode("utf8")))

        await self.add_click()
        total = await self.count_total()


        await self.send(text_data=json.dumps({"message": total}))


        # text_data_json = json.loads(text_data)
        # message = text_data_json['message']

        # # Send message to room group
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'chat_message',
        #         'message': message
        #     }
        # )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    @database_sync_to_async
    def create_player(self):
        return ClickTracker.objects.create(click_count=0)

    @database_sync_to_async
    def add_click(self):
        # self.model = F('click_count') + 1
        self.model.click_count += 1
        self.model.save()

    @database_sync_to_async
    def count_total(self):
        return ClickTracker.objects.aggregate(Sum("click_count"))
