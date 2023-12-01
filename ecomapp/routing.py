from django.urls import path , include
from ecomapp.consumers import ChatConsumer

# Here, "" is routing to the URL ChatConsumer which 
# will handle the chat functionality.
websocket_urlpatterns = [
	# path("" , ChatConsumer.as_asgi()) , 
    path('ws/chat/<str:sender_username>/<str:receiver_username>/', ChatConsumer.as_asgi()),
]
