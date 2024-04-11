from django import forms

class BuyStockForm(forms.Form):
    ticker = forms.CharField(label="Stock ticker")
    number_stocks = forms.FloatField(label="Number of stock", min_value=0, step_size=0.00001)
    price_stocks = forms.FloatField(label="Price", min_value=0, step_size=0.01)
    date = forms.DateField(
        label="Date",
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )