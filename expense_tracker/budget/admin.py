from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Sum

from budget.models import Category, Budget, Income, Expense


# ==================================================
# 🔐 SUPERUSER ONLY BASE
# ==================================================
class SuperUserOnlyAdmin(admin.ModelAdmin):

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ==================================================
# 👤 CUSTOM USER ADMIN
# ==================================================
admin.site.unregister(User)

from django.utils.html import format_html
from django.db.models import Sum

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "total_income",
        "total_expense",
        "savings",
        "report_buttons",
        "delete_button",
    )

    search_fields = ("username", "email")

    # 🔥 Hide superusers
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_superuser=False)

    # ================= FINANCIAL DATA =================

    def total_income(self, obj):
        total = Income.objects.filter(user=obj).aggregate(
            t=Sum("amount")
        )["t"] or 0
        return f"₹ {total}"

    def total_expense(self, obj):
        total = Expense.objects.filter(user=obj).aggregate(
            t=Sum("amount")
        )["t"] or 0
        return f"₹ {total}"

    def savings(self, obj):
        income = Income.objects.filter(user=obj).aggregate(
            t=Sum("amount")
        )["t"] or 0
        expense = Expense.objects.filter(user=obj).aggregate(
            t=Sum("amount")
        )["t"] or 0
        return f"₹ {income - expense}"

    # ================= REPORT BUTTONS =================

    def report_buttons(self, obj):
        return format_html(
            '<a class="button" href="{}">CSV</a> '
            '<a class="button" href="{}">PDF</a>',
            reverse("budget:admin_export_csv_single_user", args=[obj.id]),
            reverse("budget:admin_export_pdf_single_user", args=[obj.id]),
        )

    report_buttons.short_description = "Reports"

    # ================= DELETE BUTTON =================

    def delete_button(self, obj):
        return format_html(
            '<a class="button" style="background:#dc3545;color:white;padding:4px 8px;border-radius:4px;" '
            'href="{}">Delete</a>',
            reverse("admin:auth_user_delete", args=[obj.id])
        )

    delete_button.short_description = "Delete User"
# ==================================================
# OTHER MODELS (SUPERUSER ONLY)
# ==================================================
@admin.register(Category)
class CategoryAdmin(SuperUserOnlyAdmin):
    list_display = ("name", "user")
    list_filter = ("user",)


@admin.register(Budget)
class BudgetAdmin(SuperUserOnlyAdmin):
    list_display = ("user", "amount")
    list_filter = ("user",)


@admin.register(Income)
class IncomeAdmin(SuperUserOnlyAdmin):
    list_display = ("user", "amount", "source", "date")
    list_filter = ("user", "date")


@admin.register(Expense)
class ExpenseAdmin(SuperUserOnlyAdmin):
    list_display = ("user", "category", "amount", "date")
    list_filter = ("user", "category", "date")