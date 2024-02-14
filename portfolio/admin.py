from django.contrib import admin

from .models import Portfolio, Transaction, DividendPayment

# Register your models here.
admin.site.register(Portfolio)
admin.site.register(Transaction)
admin.site.register(DividendPayment)