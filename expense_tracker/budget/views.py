from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.models import User
from django.db.models import Sum, Avg
from django.db.models.functions import TruncDate,TruncWeek
from django.db import transaction
from django.utils.safestring import mark_safe
from datetime import date
from datetime import datetime
import json
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from .utils import get_user_financial_data
from collections import defaultdict
from django.utils import timezone


from .models import Profile, Budget, Category, Income, Expense
from .forms import BudgetForm, CategoryForm, IncomeForm, ExpenseForm

# -------------------------
# AUTHENTICATION VIEWS
# -------------------------

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Create user profile if not created
            Profile.objects.get_or_create(user=user)

            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'budget/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')


@transaction.atomic
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        # 🔥 CREATE USER ONLY ONCE
        user = User.objects.create_user(
            username=username,
            password=password
        )

        # ❌ DO NOT touch Profile here
        # Signal handles it

        messages.success(request, "Account created successfully")
        return redirect("login")

    return render(request, "budget/register.html")



# -------------------------
# DASHBOARD
# -------------------------
@login_required
def dashboard(request):
    user = request.user
    from django.db.models import Sum

    total_income = Income.objects.filter(user=user).aggregate(
        total=Sum("amount")
    )["total"] or 0

    total_expense = Expense.objects.filter(user=user).aggregate(
        total=Sum("amount")
    )["total"] or 0

    return render(request, "budget/dashboard_premium.html", {
        "total_income": total_income,
        "total_expense": total_expense,
    })

# -------------------------
# PROFILE VIEWS
# -------------------------

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        # FULL NAME
        profile.full_name = request.POST.get("full_name", "").strip()

        # AGE (safe handling)
        age_value = request.POST.get("age")
        if age_value and age_value.isdigit():
            profile.age = int(age_value)
        else:
            profile.age = None   # 🔥 important for admin display

        # DATE OF BIRTH (string → date)
        dob_value = request.POST.get("date_of_birth")
        if dob_value:
            try:
                profile.date_of_birth = datetime.strptime(
                    dob_value, "%Y-%m-%d"
                ).date()
            except ValueError:
                profile.date_of_birth = None

        # EMAIL UPDATE (User model)
        email_value = request.POST.get("email")
        if email_value:
            request.user.email = email_value
            request.user.save()

        # PROFILE PIC
        if request.FILES.get("profile_pic"):
            profile.profile_pic = request.FILES.get("profile_pic")

        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("view_profile")

    return render(request, "budget/profile.html", {"profile": profile})

@login_required
def view_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, "budget/view_profile.html", {"profile": profile})

@login_required
def update_profile(request):
    profile = request.user.userprofile

    if request.method == "POST":
        profile.full_name = request.POST.get("full_name")

        # AGE FIX 🔥
        age_value = request.POST.get("age")
        profile.age = int(age_value) if age_value and age_value.isdigit() else profile.age

        # DOB FIX
        dob_value = request.POST.get("date_of_birth")
        if dob_value:
            profile.date_of_birth = dob_value

        # EMAIL UPDATE FIX 🔥
        email_value = request.POST.get("email")
        if email_value:
            request.user.email = email_value
            request.user.save()

        # PROFILE IMAGE FIX NAME
        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("view_profile")

    return render(request, "budget/update_profile.html", {"profile": profile})

@login_required
def profile_settings(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        profile.full_name = request.POST.get("full_name", "")
        profile.age = request.POST.get("age") or None
        profile.date_of_birth = request.POST.get("date_of_birth") or None

        if request.FILES.get("profile_pic"):
            profile.profile_pic = request.FILES["profile_pic"]

        profile.save()

    return render(
        request,
        "budget/profile.html",
        {"profile": profile}
    )

def delete_profile(request):
    if request.method == "POST":
        request.user.delete()
        return redirect("login")


# -------------------------
# CHANGE PASSWORD
# -------------------------

@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user

        # 1️⃣ Old password check
        if not user.check_password(old_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("change_password")

        # 2️⃣ New & confirm match check
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("change_password")

        # 3️⃣ Set new password (IMPORTANT)
        user.set_password(new_password)
        user.save()

        # 4️⃣ Keep user logged in
        update_session_auth_hash(request, user)

        messages.success(request, "Password updated successfully.")
        return redirect("dashboard")

    return render(request, "budget/change_password.html")

# -------------------------
# CATEGORY CRUD
# -------------------------

@login_required
def categories(request):
    cats = Category.objects.filter(user=request.user)
    form = CategoryForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        messages.success(request, "Category added.")
        return redirect("categories")

    return render(request, "budget/categories.html", {"categories": cats, "form": form})
def delete_category(request, id):
    if request.method == "POST":
        Category.objects.filter(id=id).delete()
    return redirect("categories")
def edit_category(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == "POST":
        category.name = request.POST["name"]
        category.save()
    return redirect("categories") 

# -------------------------
# INCOME CRUD
# -------------------------

@login_required
def income(request):
    incomes = Income.objects.filter(user=request.user).order_by("-date")
    form = IncomeForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        messages.success(request, "Income recorded.")
        return redirect("income")

    return render(request, "budget/income.html", {"form": form, "incomes": incomes})

def delete_income(request, id):
    income = get_object_or_404(Income, id=id)
    income.delete()
    return redirect("income")
from datetime import datetime
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import ValidationError

def edit_income(request, id):
    income = get_object_or_404(Income, id=id, user=request.user)

    if request.method == "POST":
        income.source = request.POST.get("name") or request.POST.get("source")
        income.amount = request.POST.get("amount")

        date_str = request.POST.get("date")

        if date_str:
            try:
                income.date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError(
                    "Invalid date format. Use YYYY-MM-DD"
                )
        else:
            raise ValidationError("Date cannot be empty")

        income.save()
        return redirect("income")


# -------------------------
# EXPENSE CRUD
# -------------------------

@login_required
def expense(request):
    expenses = Expense.objects.filter(user=request.user).order_by("-date")
    form = ExpenseForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        messages.success(request, "Expense recorded.")
        return redirect("expense")

    return render(request, "budget/expense.html", {"form": form, "expenses": expenses})
@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id)
    expense.delete()
    return redirect("expense")
@login_required
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id)

    if request.method == "POST":

        # CATEGORY (safe)
        category_id = request.POST.get("category")
        if category_id:
            expense.category = get_object_or_404(Category, id=category_id)

        # AMOUNT (safe)
        amount = request.POST.get("amount")
        if amount:
            expense.amount = amount

        # DATE (safe YYYY-MM-DD)
        date_val = request.POST.get("date")
        if date_val:
            expense.date = date_val

        expense.save()

    return redirect("expense")

# -------------------------
# BUDGET CRUD
# -------------------------

@login_required
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user).order_by("-year", "-month")
    return render(request, "budget/budget_list.html", {"budgets": budgets})


@login_required
def budget_create(request):
    if request.method == "POST":
        form = BudgetForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, "Budget added successfully.")
            return redirect("budget:list")
    else:
        form = BudgetForm()

    return render(request, "budget/budget_form.html", {"form": form})



@login_required
def edit_budget(request, id):
    budget = get_object_or_404(
        Budget,
        id=id,
        user=request.user
    )

    if request.method == "POST":
        budget.category_id = request.POST.get("category")
        budget.amount = request.POST.get("amount")

        date_str = request.POST.get("date")  # YYYY-MM-DD
        budget.date = datetime.strptime(
            date_str, "%Y-%m-%d"
        ).date()

        budget.save()
        messages.success(request, "Budget updated successfully")

    return redirect("budget:list")

@login_required
def budget_delete(request, pk):
    obj = get_object_or_404(Budget, pk=pk)

    if request.method == "POST":
        obj.delete()
        messages.success(request, "Budget deleted.")

    return redirect("budget:list")

@login_required
def reports(request):

    # ---------- USER FILTER ----------
    income_qs = Income.objects.filter(user=request.user)
    expense_qs = Expense.objects.filter(user=request.user)

    # ---------- CHECK DATA EXISTS ----------
    has_data = income_qs.exists() or expense_qs.exists()

    # ---------- DEFAULT EMPTY CONTEXT ----------
    context = {
        "has_data": has_data,
        "days": json.dumps([]),
        "income_values": json.dumps([]),
        "expense_values": json.dumps([]),
        "category_labels": json.dumps([]),
        "category_totals": json.dumps([]),
    }

    # ---------- IF NO DATA → RETURN EMPTY STATE ----------
    if not has_data:
        return render(request, "budget/reports.html", context)

    # ---------- PER DAY INCOME ----------
    daily_income = (
        income_qs
        .annotate(day=TruncDate("date"))
        .values("day")
        .annotate(total=Avg("amount"))
        .order_by("day")
    )

    # ---------- PER DAY EXPENSE ----------
    daily_expense = (
        expense_qs
        .annotate(day=TruncDate("date"))
        .values("day")
        .annotate(total=Avg("amount"))
        .order_by("day")
    )

    income_dict = {str(i["day"]): float(i["total"]) for i in daily_income}
    expense_dict = {str(e["day"]): float(e["total"]) for e in daily_expense}

    all_days = sorted(set(income_dict) | set(expense_dict))

    # ---------- CATEGORY BREAKDOWN ----------
    category_qs = (
        expense_qs
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    category_labels = [row["category__name"] for row in category_qs]
    category_totals = [float(row["total"]) for row in category_qs]

    # ---------- FINAL CONTEXT ----------
    context.update({
        "days": json.dumps(all_days),
        "income_values": json.dumps([income_dict.get(d, 0) for d in all_days]),
        "expense_values": json.dumps([expense_dict.get(d, 0) for d in all_days]),
        "category_labels": json.dumps(category_labels),
        "category_totals": json.dumps(category_totals),
    })

    return render(request, "budget/reports.html", context)
    
@login_required
def savings(request):

    # ---------- USER FILTER ----------
    income_qs = Income.objects.filter(user=request.user)
    expense_qs = Expense.objects.filter(user=request.user)

    # ---------- CHECK DATA ----------
    has_data = income_qs.exists() or expense_qs.exists()

    # ---------- DEFAULT EMPTY CONTEXT ----------
    context = {
        "has_data": has_data,
        "weeks": json.dumps([]),
        "weekly_savings": json.dumps([]),
        "savings": 0,
        "goal": 50000,
        "percent": 0,
    }

    # ---------- NO DATA → EMPTY STATE ----------
    if not has_data:
        return render(request, "budget/savings.html", context)

    # ---------- WEEKLY INCOME ----------
    weekly_income = (
        income_qs
        .annotate(week=TruncWeek("date"))
        .values("week")
        .annotate(total=Sum("amount"))
        .order_by("week")
    )

    # ---------- WEEKLY EXPENSE ----------
    weekly_expense = (
        expense_qs
        .annotate(week=TruncWeek("date"))
        .values("week")
        .annotate(total=Sum("amount"))
        .order_by("week")
    )

    income_dict = {str(i["week"]): float(i["total"]) for i in weekly_income}
    expense_dict = {str(e["week"]): float(e["total"]) for e in weekly_expense}

    all_weeks = sorted(set(income_dict) | set(expense_dict))

    weekly_savings = [
        income_dict.get(w, 0) - expense_dict.get(w, 0)
        for w in all_weeks
    ]

    # ---------- TOTAL SAVINGS ----------
    savings_total = sum(weekly_savings)

    goal = 50000
    percent = int((savings_total / goal) * 100) if goal > 0 else 0

    # ---------- FINAL CONTEXT ----------
    context.update({
        "weeks": json.dumps([f"Week {i+1}" for i in range(len(all_weeks))]),
        "weekly_savings": json.dumps(weekly_savings),
        "savings": round(savings_total, 2),
        "goal": goal,
        "percent": min(percent, 100),
    })

    return render(request, "budget/savings.html", context)


def superuser_only(user):
    return user.is_superuser


@user_passes_test(superuser_only)
def admin_user_dashboard(request, user_id):
    u = get_object_or_404(User, id=user_id)
    profile = Profile.objects.filter(user=u).first()

    total_income = Income.objects.filter(user=u).aggregate(
        total=Sum("amount")
    )["total"] or 0

    total_expense = Expense.objects.filter(user=u).aggregate(
        total=Sum("amount")
    )["total"] or 0

    return render(request, "admin/user_dashboard.html", {
        "u": u,
        "profile": profile,
        "total_income": total_income,      # ✅ match template
        "total_expense": total_expense,    # ✅ match template
        "savings": total_income - total_expense
    })


@user_passes_test(superuser_only)
def admin_user_profile(request, user_id):
    u = get_object_or_404(User, id=user_id)
    profile, _ = Profile.objects.get_or_create(user=u)

    return render(
        request,
        "admin/user_profile.html",
        {
            "u": u,
            "profile": profile
        }
    )

@user_passes_test(superuser_only)
def admin_user_income(request, user_id):
    user = get_object_or_404(User, id=user_id)
    items = Income.objects.filter(user=user)
    return render(request, "admin/user_income.html", {"u": user, "items": items})


@user_passes_test(superuser_only)
def admin_user_expense(request, user_id):
    user = get_object_or_404(User, id=user_id)
    items = Expense.objects.filter(user=user)
    return render(request, "admin/user_expense.html", {"u": user, "items": items})


@user_passes_test(superuser_only)
def admin_user_savings(request, user_id):
    user = get_object_or_404(User, id=user_id)
    # reuse your savings logic here
    return render(request, "admin/user_savings.html", {"u": user})


@user_passes_test(superuser_only)
def admin_user_reports(request, user_id):
    user = get_object_or_404(User, id=user_id)
    # reuse your reports logic here
    return render(request, "admin/user_reports.html", {"u": user})


@user_passes_test(superuser_only)
def admin_user_budget(request, user_id):
    user = get_object_or_404(User, id=user_id)
    items = Budget.objects.filter(user=user)
    return render(request, "admin/user_budget.html", {"u": user, "items": items})

@login_required
def export_csv_all(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dailyexpense_all_data.csv"'

    writer = csv.writer(response)

    profile = Profile.objects.get(user=request.user)

    # ================= USER INFO =================
    writer.writerow(["USER DETAILS"])
    writer.writerow(["Username", request.user.username])
    writer.writerow(["Email", request.user.email])  # ✅ FIX
    writer.writerow(["Full Name", profile.full_name])
    writer.writerow([])

    # ================= INCOME =================
    writer.writerow(["INCOME"])
    writer.writerow(["Source", "Amount", "Date"])

    for i in Income.objects.filter(user=request.user):
        writer.writerow([i.source, i.amount, i.date])

    writer.writerow([])

    # ================= EXPENSE =================
    writer.writerow(["EXPENSE"])
    writer.writerow(["Category", "Amount", "Date"])

    for e in Expense.objects.filter(user=request.user):
        writer.writerow([e.category.name, e.amount, e.date])

    writer.writerow([])

    # ================= BUDGET =================
    writer.writerow(["BUDGET"])
    writer.writerow(["Category", "Amount", "Month", "Year"])

    for b in Budget.objects.filter(user=request.user):
        writer.writerow([b.category.name, b.amount, b.month, b.year])

    return response

@login_required
def export_pdf_all(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="dailyexpense_report.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 40

    profile = Profile.objects.get(user=request.user)

    # ================= USER DETAILS =================
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, y, "DailyExpense – Full Report")
    y -= 30

    p.setFont("Helvetica", 10)
    p.drawString(40, y, f"Username : {request.user.username}")
    y -= 15
    p.drawString(40, y, f"Email    : {request.user.email}")  # ✅ FIX
    y -= 25

    # ================= INCOME =================
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "Income")
    y -= 20

    p.setFont("Helvetica", 10)
    for i in Income.objects.filter(user=request.user):
        p.drawString(40, y, f"{i.source} | ₹{i.amount} | {i.date}")
        y -= 15
        if y < 40:
            p.showPage()
            y = height - 40

    y -= 20

    # ================= EXPENSE =================
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "Expense")
    y -= 20

    p.setFont("Helvetica", 10)
    for e in Expense.objects.filter(user=request.user):
        p.drawString(40, y, f"{e.category.name} | ₹{e.amount} | {e.date}")
        y -= 15
        if y < 40:
            p.showPage()
            y = height - 40

    y -= 20

    # ================= BUDGET =================
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "Budget")
    y -= 20

    p.setFont("Helvetica", 10)
    for b in Budget.objects.filter(user=request.user):
        p.drawString(
            40, y,
            f"{b.category.name} | ₹{b.amount} | {b.month}/{b.year}"
        )
        y -= 15
        if y < 40:
            p.showPage()
            y = height - 40

    p.showPage()
    p.save()

    return response

@login_required
def dashboard(request):
    data = get_user_financial_data(request.user)

    return render(request, "budget/dashboard_premium.html", data)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile

@login_required
def profile_update(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST":

        # ✅ ITHA THAAN NEENGA KEKURE CODE
        profile.full_name = request.POST.get("full_name")
        profile.age = request.POST.get("age")
        profile.date_of_birth = request.POST.get("date_of_birth")
        profile.profile_pic = request.FILES.get(
            "profile_pic", profile.profile_pic
        )

        profile.save()   # 🔥 MOST IMPORTANT

        return redirect("view_profile")  # or profile page

    return render(request, "budget/profile_update.html", {
        "profile": profile
    })

@login_required
def income(request):
    incomes = Income.objects.filter(user=request.user).order_by("-date")

    if request.method == "POST":
        form = IncomeForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect("income")
    else:
        form = IncomeForm()

    return render(request, "budget/income.html", {
        "form": form,
        "incomes": incomes   # 🔥 MUST
    })

@login_required
def expense(request):
    expenses = Expense.objects.filter(user=request.user).order_by("-date")

    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect("expense")
    else:
        form = ExpenseForm()

    return render(request, "budget/expense.html", {
        "form": form,
        "expenses": expenses   # 🔥 MUST
    })

from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Income, Expense

@login_required
def income_expense_summary(request):
    user = request.user
    today = date.today()

    ranges = {
        "today": today,
        "yesterday": today - timedelta(days=1),
        "last7": today - timedelta(days=7),
        "last30": today - timedelta(days=30),
        "year": date(today.year, 1, 1),
    }

    data = {}

    # TODAY
    data["today_income"] = Income.objects.filter(
        user=user, date=today
    ).aggregate(t=Sum("amount"))["t"] or 0

    data["today_expense"] = Expense.objects.filter(
        user=user, date=today
    ).aggregate(t=Sum("amount"))["t"] or 0

    # YESTERDAY
    data["yesterday_income"] = Income.objects.filter(
        user=user, date=ranges["yesterday"]
    ).aggregate(t=Sum("amount"))["t"] or 0

    data["yesterday_expense"] = Expense.objects.filter(
        user=user, date=ranges["yesterday"]
    ).aggregate(t=Sum("amount"))["t"] or 0

    # LAST 7 DAYS
    data["last7_income"] = Income.objects.filter(
        user=user, date__gte=ranges["last7"]
    ).aggregate(t=Sum("amount"))["t"] or 0

    data["last7_expense"] = Expense.objects.filter(
        user=user, date__gte=ranges["last7"]
    ).aggregate(t=Sum("amount"))["t"] or 0

    # LAST 30 DAYS
    data["last30_income"] = Income.objects.filter(
        user=user, date__gte=ranges["last30"]
    ).aggregate(t=Sum("amount"))["t"] or 0

    data["last30_expense"] = Expense.objects.filter(
        user=user, date__gte=ranges["last30"]
    ).aggregate(t=Sum("amount"))["t"] or 0

    # THIS YEAR
    data["year_income"] = Income.objects.filter(
        user=user, date__gte=ranges["year"]
    ).aggregate(t=Sum("amount"))["t"] or 0

    data["year_expense"] = Expense.objects.filter(
        user=user, date__gte=ranges["year"]
    ).aggregate(t=Sum("amount"))["t"] or 0

    return render(
        request,
        "budget/income_expense_summary.html",
        data
    )