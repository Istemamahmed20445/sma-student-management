from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Contact(models.Model):
    """Model for storing contacted students/prospects"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Full name of the contacted person")
    email = models.EmailField(blank=True, null=True, help_text="Email address (optional)")
    phone = models.CharField(max_length=30, blank=True, null=True, help_text="Phone number (optional)")
    facebook_url = models.URLField(blank=True, null=True, help_text="Facebook profile URL (optional)")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about this contact")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_contacts')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
    
    def __str__(self):
        return f"{self.name} ({self.email or self.phone or 'No contact info'})"
    
    def get_display_name(self):
        """Get display name for the contact"""
        return self.name
    
    def get_contact_info(self):
        """Get primary contact information"""
        if self.email:
            return self.email
        elif self.phone:
            return self.phone
        return "No contact info"
    
    def has_facebook(self):
        """Check if contact has Facebook URL"""
        return bool(self.facebook_url)
    
    def get_facebook_display_name(self):
        """Get Facebook display name from URL"""
        if self.facebook_url:
            # Extract username from Facebook URL
            if 'facebook.com/' in self.facebook_url:
                username = self.facebook_url.split('facebook.com/')[-1].split('/')[0].split('?')[0]
                return f"@{username}"
        return None