from django.db import models
from django.utils.timezone import now

class TransactionLog(models.Model):
    user_id = models.CharField(max_length=255)  # Extracted from JWT
    action = models.CharField(max_length=255)  # Description of the action
    timestamp = models.DateTimeField(default=now)  # Auto-set timestamp
    endpoint = models.CharField(max_length=255)  # API endpoint accessed
    method = models.CharField(max_length=10)  # HTTP method (GET, POST, etc.)
    details = models.TextField(null=True, blank=True)  # Optional details

    def __str__(self):
        return f"{self.user_id} - {self.action} at {self.timestamp}"
