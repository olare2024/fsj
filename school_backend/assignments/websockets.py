#assignments/websockets.py 
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class AssignmentConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time assignment updates"""
    
    async def connect(self):
        self.user = self.scope['user']
        self.assignment_group = None
        
        if self.user.is_authenticated:
            await self.accept()
            await self.send(json.dumps({
                'type': 'connection_established',
                'message': 'Connected to assignment updates'
            }))
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        if self.assignment_group:
            await self.channel_layer.group_discard(
                self.assignment_group,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Receive messages from WebSocket"""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'subscribe_assignment':
            assignment_id = data.get('assignment_id')
            await self.subscribe_to_assignment(assignment_id)
        
        elif message_type == 'subscribe_student':
            student_id = data.get('student_id')
            await self.subscribe_to_student(student_id)
    
    async def subscribe_to_assignment(self, assignment_id):
        """Subscribe to assignment updates"""
        assignment = await self.get_assignment(assignment_id)
        
        if assignment and await self.can_view_assignment(assignment):
            self.assignment_group = f'assignment_{assignment_id}'
            await self.channel_layer.group_add(
                self.assignment_group,
                self.channel_name
            )
            
            await self.send(json.dumps({
                'type': 'subscription_success',
                'message': f'Subscribed to assignment {assignment.title}'
            }))
    
    @database_sync_to_async
    def get_assignment(self, assignment_id):
        """Get assignment from database"""
        try:
            return Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return None
    
    @database_sync_to_async
    def can_view_assignment(self, assignment):
        """Check if user can view assignment"""
        if self.user.is_staff or self.user.is_superuser:
            return True
        
        if self.user.is_teacher:
            return assignment.teacher.user == self.user
        
        if self.user.is_student:
            return assignment.classroom == self.user.student_profile.classroom
        
        return False