import json
import re
from channels.generic.websocket import AsyncWebsocketConsumer

from ecomapp.models import Message, Customer



# '''for the begginers to implement here first'''
# class ChatConsumer(AsyncWebsocketConsumer):
# 	async def connect(self):
# 		self.roomGroupName = "group_chat_gfg"
# 		await self.channel_layer.group_add(
# 			self.roomGroupName ,
# 			self.channel_name
# 		)
# 		await self.accept()
# 	async def disconnect(self , close_code):
# 		await self.channel_layer.group_discard(
# 			self.roomGroupName , 
# 			self.channel_layer 
# 		)
# 	async def receive(self, text_data):
# 		text_data_json = json.loads(text_data)
# 		print('text_data_json------',text_data_json)
# 		message = text_data_json["message"]
# 		username = text_data_json["username"]
# 		await self.channel_layer.group_send(
# 			self.roomGroupName,{
# 				"type" : "sendMessage" ,
# 				"message" : message , 
# 				"username" : username ,
# 			})
# 	async def sendMessage(self , event) : 
# 		message = event["message"]
# 		username = event["username"]
# 		await self.send(text_data = json.dumps({"message":message ,"username":username}))


'''for the chat room for user custom'''

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json


from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Customer, Message, MessageHistory
import hashlib

import firebase_admin
from firebase_admin import messaging





class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender_username = self.scope['url_route']['kwargs']['sender_username']
        
        self.receiver_username = self.scope['url_route']['kwargs']['receiver_username']
        
         # Create a unique room name based on sender and receiver usernames
        # hashed_group_name = hashlib.sha256(f"{self.sender_username}_{self.receiver_username}".encode()).hexdigest()[:50]  # Example hash length limit
        hashed_group_name = hashlib.sha256(f"{min(self.sender_username, self.receiver_username)}_{max(self.sender_username, self.receiver_username)}".encode()).hexdigest()[:50]
        print('hashed_group_name-------',hashed_group_name)
        


        self.room_name = f"group_chat_{hashed_group_name}"

        # Join the chat room
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
    

    async def disconnect(self, close_code):
        # Leave the chat room
        print('--LEAVING THE ROOM ')
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        message = text_data_json['message']
        
        sender_username = text_data_json['username']
        
        receiver_username = self.receiver_username
        

        # Save message to the database asynchronously using sync_to_async
        await sync_to_async(self.save_message_to_database)(sender_username, receiver_username, message)

        # Send message to receiver's chat room
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': sender_username,
                'receiver_username': receiver_username
            }
        )
        
        await self.send_push_notification_to_receiver(message, self.receiver_username)

    def save_message_to_database(self, sender_username, receiver_username, message):
        from django.db.models import Q  # Update the import statement
        sender = Customer.objects.get(email=sender_username)
        receiver = Customer.objects.get(email=receiver_username)

        # Check if a message already exists between sender and receiver
        existing_message = Message.objects.filter(Q(Q(sender=sender) & Q(receiver=receiver)) | Q(Q(sender=receiver) & Q(receiver=sender))).first()

        if existing_message:
            # Update the existing message content
            existing_message.content = message
            existing_message.save()
        else:
            # Create a new message if it doesn't exist
            existing_message = Message.objects.create(sender=sender, receiver=receiver, content=message)
            
        MessageHistory.objects.create(message=existing_message,created_by = sender ,content=message)

    
    async def chat_message(self, event):
    # Send the received message to the WebSocket
        print('----event----',event)
        message = event['message']
        
        sender_username = event['username']
        receiver_username = event['receiver_username']  # Include receiver's username

        # Send the complete data with sender and receiver info to the WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_username': sender_username,
            'receiver_username': receiver_username,
            'created_by': sender_username
        }))
    


    
    async def send_push_notification_to_receiver(self, message, receiver_username):
        try:
            receiver = await sync_to_async(Customer.objects.get)(email=receiver_username)  
            receiver_fcm_token = receiver.fcm_token

            if receiver_fcm_token:
                notification = messaging.Notification(
                    title=f"Message from {receiver_username}",
                    body=message
                )

                push_message = messaging.Message(
                    notification=notification,
                    token=receiver_fcm_token
                )

                response = messaging.send(push_message)
                print('Successfully sent message:', response)
            else:
                print('Error: FCM token is not available for receiver', receiver_username)
        except firebase_admin._messaging_utils.UnregisteredError:
            print('Error: The FCM token is no longer valid. Remove it from the database or handle it accordingly.')
        except Customer.DoesNotExist:
            print('Error: Customer with email', receiver_username, 'does not exist or is not registered.')





    # async def send_push_notification_to_receiver(self, message, receiver_username):
        #     try:
        #         receiver = await sync_to_async(Customer.objects.get)(email=receiver_username)  
        #         print('iiiiiii---receiver',receiver)
        #         receiver_fcm_token = receiver.fcm_token
        #         print('iiiiiii---receiver_fcm_token',receiver_fcm_token)

        #         notification = messaging.Notification(
        #             title=f"message from {receiver_username}",
        #             body=message
        #         )

        #         push_message = messaging.Message(
        #             notification=notification,
        #             token=receiver_fcm_token
        #         )

        #         response = messaging.send(push_message)
        #         print('Successfully sent message:', response)
        #     except firebase_admin._messaging_utils.UnregisteredError:
        #         print('Error: The FCM token is no longer valid. Remove it from the database or handle it accordingly.')

    
    
    
