from django.db import models


class SavedReport(models.Model):
    title = models.CharField(max_length=255)
    symbols = models.JSONField(default=list)
    user_prompt = models.TextField()
    report_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class WatchlistItem(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["symbol"]

    def __str__(self):
        return self.symbol
