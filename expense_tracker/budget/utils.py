from .models import Income, Expense, Budget

def get_user_financial_data(user):
    incomes = Income.objects.filter(user=user)
    expenses = Expense.objects.filter(user=user)
    budgets = Budget.objects.filter(user=user)

    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)
    savings = total_income - total_expense

    return {
        "incomes": incomes,
        "expenses": expenses,
        "budgets": budgets,
        "total_income": total_income,
        "total_expense": total_expense,
        "savings": savings
    }
