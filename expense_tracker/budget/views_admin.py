from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Sum
from .models import Income, Expense,Profile
from django.contrib.admin.views.decorators import staff_member_required
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from .utils import get_user_financial_data
from reportlab.platypus import SimpleDocTemplate, Paragraph,Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import csv
from budget.models import Income, Expense, Budget, Profile
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm




def superuser_only(user):
    return user.is_superuser



@user_passes_test(superuser_only)
def admin_user_profile(request, user_id):
    u = get_object_or_404(User, id=user_id)
    profile = Profile.objects.filter(user=u).first()

    return render(
        request,
        "admin/user_profile.html",
        {
            "u": u,
            "profile": profile,
        }
    )

@user_passes_test(superuser_only)
def admin_user_savings(request, user_id):
    u = get_object_or_404(User, id=user_id)
    income = Income.objects.filter(user=u).aggregate(t=Sum("amount"))["t"] or 0
    expense = Expense.objects.filter(user=u).aggregate(t=Sum("amount"))["t"] or 0
    return render(
        request,
        "admin/user_savings.html",
        {"u": u, "income": income, "expense": expense, "savings": income - expense},
    )

@user_passes_test(superuser_only)
def admin_user_reports(request, user_id):
    u = get_object_or_404(User, id=user_id)
    incomes = Income.objects.filter(user=u).order_by("-date")
    expenses = Expense.objects.filter(user=u).order_by("-date")
    return render(
        request,
        "admin/user_reports.html",
        {"u": u, "incomes": incomes, "expenses": expenses},
    )

# ================= CSV EXPORT (SINGLE USER) =================
@staff_member_required
def admin_export_csv_single_user(request, user_id):
    u = User.objects.get(id=user_id)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{u.username}_data.csv"'

    writer = csv.writer(response)

    # ================= USER INFO =================
    writer.writerow(["USER DETAILS"])
    writer.writerow(["Username", u.username])
    writer.writerow(["Email", u.email])
    writer.writerow([])

    # ================= PROFILE =================
    profile = Profile.objects.filter(user=u).first()
    writer.writerow(["PROFILE"])
    if profile:
        writer.writerow(["Full Name", profile.full_name])
        writer.writerow(["Age", profile.age])
        writer.writerow(["DOB", profile.date_of_birth])
    else:
        writer.writerow(["Profile not completed"])
    writer.writerow([])

    # ================= INCOME =================
    writer.writerow(["INCOME"])
    writer.writerow(["Source", "Amount", "Date"])
    for i in Income.objects.filter(user=u):
        writer.writerow([i.source, i.amount, i.date])
    writer.writerow([])

    # ================= EXPENSE =================
    writer.writerow(["EXPENSE"])
    writer.writerow(["Category", "Amount", "Date"])
    for e in Expense.objects.filter(user=u):
        writer.writerow([e.category.name, e.amount, e.date])
    writer.writerow([])

    # ================= BUDGET =================
    writer.writerow(["BUDGET"])
    writer.writerow(["Category", "Amount", "Month", "Year"])
    for b in Budget.objects.filter(user=u):
        writer.writerow([b.category.name, b.amount, b.month, b.year])

    return response


# ================= PDF EXPORT (SINGLE USER) =================
@staff_member_required
def admin_export_pdf_single_user(request, user_id):
    u = User.objects.get(id=user_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{u.username}_report.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>User Financial Report</b>", styles["Title"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"Username: {u.username}", styles["Normal"]))
    story.append(Paragraph(f"Email: {u.email}", styles["Normal"]))
    story.append(Spacer(1, 15))

    profile = Profile.objects.filter(user=u).first()
    if profile:
        story.append(Paragraph(f"Full Name: {profile.full_name}", styles["Normal"]))
        story.append(Paragraph(f"Age: {profile.age}", styles["Normal"]))
        story.append(Paragraph(f"DOB: {profile.date_of_birth}", styles["Normal"]))
    else:
        story.append(Paragraph("Profile not completed", styles["Normal"]))

    story.append(Spacer(1, 20))

    # INCOME
    story.append(Paragraph("<b>Income</b>", styles["Heading2"]))
    for i in Income.objects.filter(user=u):
        story.append(Paragraph(f"{i.source} - ₹{i.amount}", styles["Normal"]))

    story.append(Spacer(1, 15))

    # EXPENSE
    story.append(Paragraph("<b>Expense</b>", styles["Heading2"]))
    for e in Expense.objects.filter(user=u):
        story.append(Paragraph(f"{e.category.name} - ₹{e.amount}", styles["Normal"]))

    doc.build(story)
    return response

@staff_member_required
def admin_user_dashboard(request, user_id):
    u = get_object_or_404(User, id=user_id)

    # ✅ PROFILE
    profile = Profile.objects.filter(user=u).first()

    # ✅ FINANCIAL DATA
    incomes = Income.objects.filter(user=u)
    expenses = Expense.objects.filter(user=u)

    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)
    savings = total_income - total_expense

    context = {
        "u": u,
        "profile": profile,
        "total_income": total_income,
        "total_expense": total_expense,
        "savings": savings,
    }

    return render(request, "admin/user_dashboard.html", context)


@staff_member_required
def get_user_financial_data(user):
    incomes = Income.objects.filter(user=user)
    expenses = Expense.objects.filter(user=user)
    budgets = Budget.objects.filter(user=user)

    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)
    savings = total_income - total_expense

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "savings": savings,
        "incomes": incomes,
        "expenses": expenses,
        "budgets": budgets,
    }

class CustomUserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2"),
        }),
    )


# remove default admin
admin.site.unregister(User)

# register fixed admin
admin.site.register(User, CustomUserAdmin)