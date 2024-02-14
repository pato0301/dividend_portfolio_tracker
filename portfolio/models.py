import uuid
from django.conf import settings
from django.db import models

class Portfolio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticker = models.CharField(max_length=64)
    name = models.CharField(max_length=150)
    n_stock = models.FloatField()
    avg_price = models.FloatField()
    industry = models.CharField(max_length=150)
    n_stock_next_exdiv_payment = models.FloatField()
    next_exdiv_payment = models.DateField(auto_now=False, auto_now_add=False)
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

class Transaction(models.Model):
    OPERATION_TYPES = [
        ("sell", "sell"),
        ("buy", "buy"),

    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticker = models.CharField(max_length=64, default="")
    operation = models.CharField(max_length=150, choices=OPERATION_TYPES)
    operation_date = models.DateField(auto_now=False, auto_now_add=False)
    n_stock = models.FloatField()
    price = models.FloatField()
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

class DividendPayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticker = models.CharField(max_length=64)
    payment_date = models.DateField(auto_now=False, auto_now_add=False)
    amount = models.FloatField()
    n_stock = models.FloatField()
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )