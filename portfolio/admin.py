from django.contrib import admin

from .models import Portfolio, User, Transaction, DividendPayment

# Register your models here.
admin.site.register(Portfolio)
#admin.site.register(User)
admin.site.register(Transaction)
admin.site.register(DividendPayment)