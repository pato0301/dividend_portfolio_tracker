from django import forms
from .models import Portfolio

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


class SellStockForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        super(SellStockForm, self).__init__(*args, **kwargs)
        
        self.fields['ticker'] = forms.ChoiceField(label="Stock ticker", widget=forms.Select(choices=[]))
        self.fields['number_stocks'] = forms.FloatField(label="Number of stock", min_value=0)
        self.fields['price_stocks'] = forms.FloatField(label="Price", min_value=0)
        self.fields['date'] = forms.DateField(
            label="Date",
            widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            input_formats=["%Y-%m-%d"]
        )

        portfolio_entries = Portfolio.objects.filter(user_id=user)
        
        if portfolio_entries.exists():
            ticker_choices = [(entry.ticker, entry.ticker) for entry in portfolio_entries]
            self.fields['ticker'].choices = ticker_choices
            
            # Set initial value for ticker from POST data
            if 'ticker' in self.data:
                self.fields['ticker'].initial = self.data['ticker']

        else:
            self.fields['ticker'].choices = [('', '---')]
            self.fields['ticker'].initial = ''
            self.fields['ticker'].disabled = True
            self.fields['ticker'].required = False


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