from django.urls import path
from . import views

app_name = "portfolio"
urlpatterns = [
    path("", views.index, name="index"),
    path("buy-stock", views.load_buy_stock, name="load_buy_stock"),
    path("save-buy-stock", views.buy_stock, name="save_buy_stock"),
    path("sell-stock", views.sell_stock, name="sell_stock")
]