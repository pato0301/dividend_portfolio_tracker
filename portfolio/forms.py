from django import forms

# class BuyStockForm(forms.Form):
#     ticker = forms.CharField(label="Stock ticker")
#     number_stocks = forms.FloatField(label="Number of stock", min_value=0, step_size=0.00001)
#     price_stocks = forms.FloatField(label="Price", min_value=0, step_size=0.01)
#     date = forms.DateField(
#         label="Date",
#         widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
#         input_formats=["%Y-%m-%d"]
#     )

class BuyStockForm(forms.Form):
    ticker = forms.CharField(
        label="Stock ticker",
        widget=forms.TextInput(attrs={'class': 'form-field', 'placeholder': 'Stock ticker'})
    )
    number_stocks = forms.FloatField(
        label="Number of stock",
        min_value=0,
        step_size=0.00001,
        widget=forms.NumberInput(attrs={'class': 'form-field'})
    )
    price_stocks = forms.FloatField(
        label="Price",
        min_value=0,
        step_size=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-field'})
    )
    date = forms.DateField(
        label="Date",
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", 'class': 'form-field'}
        ),
        input_formats=["%Y-%m-%d"]
    )

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Select a CSV file',
        help_text='Please upload a CSV file',
        widget=forms.FileInput(attrs={'accept': '.csv', 'onchange': 'displayFileName(this)'})
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('Please upload a valid CSV file.')
        return csv_file