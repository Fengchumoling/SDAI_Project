import datetime
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.apps import apps
from django.shortcuts import redirect


@database_sync_to_async
def get_user(user_id):
    User = get_user_model()
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


@database_sync_to_async
def get_group(group_id):
    Group = apps.get_model('app1', 'Group')
    try:
        return Group.objects.get(pk=group_id)
    except Group.DoesNotExist:
        return None


@database_sync_to_async
def check_user(user, group):
    if user in group.members.all():
        return True
    else:
        return False


@database_sync_to_async
def get_group_messages(group):
    messages = group.messages.order_by('-timestamp')[:10]
    msg_list = []
    for message in messages:
        content = message.content
        sender = message.sender
        timestamp_str = message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        msg = f'{timestamp_str}  {sender} : {content}'
        msg_list.append(msg)
    return msg_list


@database_sync_to_async
def create_message(user, group, message):
    Message = apps.get_model('app1', 'Message')
    message = Message.objects.create(sender=user, content=message, group=group)


class CustomAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # 检查用户是否已经通过认证
        if scope.get("user"):
            scope["user"] = await self.sync_to_async(get_user)(scope["user_id"])
        return await super().__call__(scope, receive, send)


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        self.user = self.scope["user"]
        # self.group = await self.get_group(self.room_name)
        self.group = await get_group(self.room_name)

        if not await check_user(self.user, self.group):
            await self.close(reason="Forbidden")

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        message_list = await get_group_messages(self.group)

        for message in message_list:
            await self.send(text_data=json.dumps({
                "message": message
            }))


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await create_message(self.user, self.group, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        datetime_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sender = self.user
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": f'{datetime_str}  {sender} : {message}'
        }))
