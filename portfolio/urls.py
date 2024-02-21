from django.urls import path
from . import views

app_name = "portfolio"
urlpatterns = [
    path("", views.index, name="index"),
    path("buy-stock", views.load_buy_stock, name="load_buy_stock"),
    path("save-buy-stock", views.save_buy_stock, name="save_buy_stock"),
    path("sell-stock", views.sync_load_sell_stock, name="load_sell_stock"),
    path("save-sell-stock", views.save_sell_stock, name="save_sell_stock")
]