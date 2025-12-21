from django import forms
from .models import Category, Income, Expense, Budget

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ["source", "amount", "date"]
        widgets = {
            "source": forms.TextInput(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["category", "amount", "date"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
        }


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ["category", "amount", "date"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"   # 🔥 IMPORTANT
                }
            ),
        }



