from datetime import datetime, timedelta
from django.db import models
from EphemeralMessages.settings import CHAT_DEFAULT_TIMEOUT

class Chat(models.Model):
    """
    Model class for Chat messages.
    expiration_date column is computed on the fly.
    """
    username = models.CharField(max_length=200)
    text = models.CharField(max_length=512)
    timeout = models.PositiveIntegerField(default=CHAT_DEFAULT_TIMEOUT)
    expiration_date = models.DateTimeField(blank=True)

    def save(self, *args, **kwargs):
        if self.timeout >= 0:
            self.expiration_date = datetime.now() + timedelta(seconds=self.timeout)
        self.full_clean()
        super().save(*args, **kwargs)

