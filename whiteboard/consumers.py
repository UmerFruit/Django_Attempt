import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Whiteboard

logger = logging.getLogger(__name__)


class WhiteboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time whiteboard collaboration.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.whiteboard_id = self.scope['url_route']['kwargs']['whiteboard_id']
        self.room_group_name = f'whiteboard_{self.whiteboard_id}'
        self.user = self.scope["user"]
        
        # Check if user has permission to view the whiteboard
        if not await self.can_access_whiteboard():
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current whiteboard data to the newly connected user
        whiteboard_data = await self.get_whiteboard_data()
        if whiteboard_data:
            await self.send(text_data=json.dumps({
                'type': 'whiteboard_data',
                'data': whiteboard_data
            }))
        
        logger.info(f"User {self.user.username if self.user.is_authenticated else 'Anonymous'} connected to whiteboard {self.whiteboard_id}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"User {self.user.username if self.user.is_authenticated else 'Anonymous'} disconnected from whiteboard {self.whiteboard_id}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'drawing_update':
                # Broadcast drawing update to all users in the room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'drawing_update',
                        'data': data.get('data'),
                        'user': self.user.username if self.user.is_authenticated else 'Anonymous'
                    }
                )
            
            elif message_type == 'save_whiteboard':
                # Only allow authenticated users to save
                if self.user.is_authenticated and await self.can_edit_whiteboard():
                    success = await self.save_whiteboard_data(data.get('data'))
                    await self.send(text_data=json.dumps({
                        'type': 'save_response',
                        'success': success
                    }))
            
            elif message_type == 'cursor_position':
                # Broadcast cursor position to other users
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'cursor_update',
                        'user': self.user.username if self.user.is_authenticated else 'Anonymous',
                        'x': data.get('x'),
                        'y': data.get('y'),
                        'channel_name': self.channel_name
                    }
                )
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from user {self.user.username if self.user.is_authenticated else 'Anonymous'}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
    
    async def drawing_update(self, event):
        """Send drawing update to WebSocket."""
        # Don't send the update back to the sender
        if event.get('user') != (self.user.username if self.user.is_authenticated else 'Anonymous'):
            await self.send(text_data=json.dumps({
                'type': 'drawing_update',
                'data': event['data'],
                'user': event['user']
            }))
    
    async def cursor_update(self, event):
        """Send cursor position update to WebSocket."""
        # Don't send cursor update back to the sender
        if event.get('channel_name') != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'cursor_update',
                'user': event['user'],
                'x': event['x'],
                'y': event['y']
            }))
    
    @database_sync_to_async
    def can_access_whiteboard(self):
        """Check if the current user can access the whiteboard."""
        try:
            whiteboard = Whiteboard.objects.get(id=self.whiteboard_id)
            return whiteboard.can_view(self.user)
        except Whiteboard.DoesNotExist:
            return False
    
    @database_sync_to_async
    def can_edit_whiteboard(self):
        """Check if the current user can edit the whiteboard."""
        try:
            whiteboard = Whiteboard.objects.get(id=self.whiteboard_id)
            return whiteboard.can_edit(self.user)
        except Whiteboard.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_whiteboard_data(self):
        """Get the current whiteboard data."""
        try:
            whiteboard = Whiteboard.objects.get(id=self.whiteboard_id)
            return whiteboard.get_drawing_data()
        except Whiteboard.DoesNotExist:
            return None
    
    @database_sync_to_async
    def save_whiteboard_data(self, data):
        """Save whiteboard data to the database."""
        try:
            from .views import validate_drawing_data
            whiteboard = Whiteboard.objects.get(id=self.whiteboard_id)
            
            if whiteboard.can_edit(self.user):
                validated_data = validate_drawing_data(data)
                whiteboard.data = validated_data
                whiteboard.save()
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving whiteboard data: {str(e)}")
            return False
