from asyncio import tasks
from re import search
from django.shortcuts import redirect
from django.views.generic.list import ListView
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from datetime import datetime


from .forms import TransactionForm
from .models import Transactions, Profile

class CustomLoginView(LoginView):
    template_name = "budget_tracker/login.html"
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('transactions')

class RegisterPage(FormView):
    template_name = 'budget_tracker/register.html'
    form_class = UserCreationForm
    redirect_autheticated_user = True
    success_url = reverse_lazy("transactions")

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            Profile.objects.create(user=user)
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('transactions')
        return super(RegisterPage, self).get(*args, **kwargs)


class TransactionsView(LoginRequiredMixin, ListView):
    model = Transactions
    context_object_name = 'transactions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = context['transactions'].filter(user=self.request.user.prof)
        month = datetime.now().strftime("%Y-%m")
        context['month'] = datetime.now().strftime("%B")
        context['income'] = sum([transaction.amount for transaction in context['transactions'] if (transaction.type and (transaction.date.strftime("%Y-%m")  == month)) ])
        context['expense'] = sum([transaction.amount for transaction in context['transactions'] if (not transaction.type and (transaction.date.strftime("%Y-%m")  == month))])
        income = sum([transaction.amount for transaction in context['transactions'] if transaction.type])
        expense = sum([transaction.amount for transaction in context['transactions'] if not transaction.type])
        context['balance'] = income - expense

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['transactions'] = context['transactions'].filter(title__startswith = search_input)
        
        context['search'] = search_input

        category_values = {}
        
        for transaction in context['transactions']:
            if not(transaction.type and transaction.category == "Income"):
                if transaction.category in category_values:
                    category_values[transaction.category] += transaction.amount
                else:
                    category_values[transaction.category] = transaction.amount

        categories = []
        category_expenses = []
        for category in category_values:
            categories.append(category)
            category_expenses.append(category_values[category])

        context['categories'] = categories
        context['amounts'] = category_expenses
        context['check'] = sum(category_expenses)

        return context


class TransactionCreateView(BSModalCreateView):
    template_name = 'budget_tracker/create.html'
    form_class = TransactionForm
    success_message = "Transaction was created"
    success_url = reverse_lazy('transactions')

    def form_valid(self, form):
        form.instance.user = self.request.user.prof
        return super(TransactionCreateView, self).form_valid(form)

class TransactionUpdateView(BSModalUpdateView):
    model = Transactions
    template_name = 'budget_tracker/update.html'
    form_class = TransactionForm
    success_message = 'Transaction was updated.'
    success_url = reverse_lazy('transactions')

class TransactionDeleteView(BSModalDeleteView):
    model = Transactions
    template_name = 'budget_tracker/delete.html'
    success_message = 'Success: Book was deleted.'
    success_url = reverse_lazy('transactions')
