from django.urls import path
from . import views

app_name = "portfolio"
urlpatterns = [
    path("", views.index, name="index"),
    path("buy-stock", views.buy_stock, name="buy_stock"),
    path("sell-stock", views.sell_stock, name="sell_stock")
]