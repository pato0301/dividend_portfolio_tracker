import uuid
from django.db import models

# Create your models here.
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    password = models.CharField(max_length=50, default="password1234")

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
        "User",
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
        "User",
        on_delete=models.CASCADE,
    )

class DividendPayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticker = models.CharField(max_length=64)
    payment_date = models.DateField(auto_now=False, auto_now_add=False)
    amount = models.FloatField()
    n_stock = models.FloatField()
    user_id = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
    )