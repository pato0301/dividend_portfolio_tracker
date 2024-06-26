from django.urls import path
from . import views

app_name = "portfolio"
urlpatterns = [
    path("", views.index, name="index"),
    path("buy-stock", views.load_buy_stock, name="load_buy_stock"),
    path("save-buy-stock", views.save_buy_stock, name="save_buy_stock"),
    path("sell-stock", views.load_sell_stock, name="load_sell_stock"),
    path("save-sell-stock", views.save_sell_stock, name="save_sell_stock"),
    path("view-dividends", views.load_dividen_log, name="view_dividends"),
    path("upload-csv-history", views.upload_csv, name="upload_csv_history"),
    path("portfolio-metrics", views.portfolio_metrics, name="portfolio_metrics"),
    path("pay-div", views.pay_div, name="pay_div")
]