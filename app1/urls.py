
from django.urls import path
from .views import chatbot_api, chatbot_view

urlpatterns = [
    
    path('chatbot/', chatbot_api, name='chatbot_api'),  # API endpoint
    path('', chatbot_view, name='chatbot_view'),       # Front-end interface
]

