from bootstrap_modal_forms.forms import BSModalModelForm
from .models import Transactions

class TransactionForm(BSModalModelForm):
    class Meta:
        model = Transactions
        exclude = ['user']
