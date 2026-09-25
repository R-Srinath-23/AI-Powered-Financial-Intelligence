from django.db import models

class Transaction(models.Model):
    transaction_id = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    description = models.TextField()
    counterparty = models.CharField(max_length=200)
    amount = models.FloatField()
    method = models.CharField(max_length=50)
    
    # AI Classification fields
    ai_category = models.CharField(max_length=100, null=True, blank=True)
    ai_confidence = models.FloatField(null=True, blank=True)
    needs_review = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.transaction_id} - {self.description}"

class Correction(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    corrected_category = models.CharField(max_length=100)
    corrected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Correction for {self.transaction.transaction_id}"
