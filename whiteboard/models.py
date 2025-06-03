from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import json


class Whiteboard(models.Model):
    """
    Model representing a whiteboard with drawing data and metadata.
    """
    title = models.CharField(max_length=200, help_text="Title of the whiteboard")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='whiteboards')
    data = models.JSONField(default=dict, help_text="Drawing data in JSON format")
    is_public = models.BooleanField(default=False, help_text="Whether the whiteboard is publicly accessible")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} by {self.owner.username}"
    
    def get_absolute_url(self):
        return reverse('whiteboard:view', kwargs={'pk': self.pk})
    def can_view(self, user):
        """Check if a user can view this whiteboard."""
        return self.is_public or (user.is_authenticated and self.owner == user)
    
    def can_edit(self, user):
        """Check if a user can edit this whiteboard."""
        return user.is_authenticated and self.owner == user
    
    def get_drawing_data(self):
        """Get drawing data in Fabric.js compatible format."""
        default_data = {
            "version": "5.3.0",
            "objects": []
        }
        if not self.data:
            return default_data
        
        # If data is in old format, convert to Fabric.js format
        if isinstance(self.data, dict):
            if "objects" in self.data:
                # Already in Fabric.js format
                return self.data
            elif "strokes" in self.data or "shapes" in self.data or "text" in self.data:
                # Old format, return empty for now (drawings will be lost but new ones will work)
                return default_data
        
        return default_data


class WhiteboardSession(models.Model):
    """
    Model to track active whiteboard sessions for analytics.
    """
    whiteboard = models.ForeignKey(Whiteboard, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['whiteboard', 'user']
    
    def __str__(self):
        return f"{self.user.username} on {self.whiteboard.title}"
