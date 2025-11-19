from django import forms
from .models import Investment, GameSession
from decimal import Decimal

class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ['instrument', 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': '0', 'step': '100'}),
        }
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Сумма инвестиции должна быть положительной")
        return amount

class InvestmentDistributionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.game_session = kwargs.pop('game_session')
        super().__init__(*args, **kwargs)
        
        instruments = self.game_session.investments.all()
        for investment in instruments:
            field_name = f"instrument_{investment.instrument.id}"
            self.fields[field_name] = forms.DecimalField(
                label=investment.instrument.name,
                max_digits=12,
                decimal_places=2,
                min_value=Decimal('0'),
                initial=investment.amount,
                widget=forms.NumberInput(attrs={'class': 'form-control'})
            )
    
    def clean(self):
        cleaned_data = super().clean()
        total_invested = sum(cleaned_data.values())
        available_capital = self.game_session.current_capital
        
        if total_invested > available_capital:
            raise forms.ValidationError(
                f"Общая сумма инвестиций ({total_invested}₽) превышает доступный капитал ({available_capital}₽)"
            )
        return cleaned_data