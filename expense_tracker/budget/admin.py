from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html

from .models import Category, Budget, Income, Expense


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
# 👤 USER ADMIN (ALL USER DATA ACCESS)
# ==================================================
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "dashboard",
        "profile_btn",
        "income",
        "expense",
        "savings",
        "reports",
        "budget",
        "delete_user",
    )

    search_fields = ("username", "email")

    # 🔥 hide superusers from user list
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_superuser=False)

    # -------- helper --------
    def _btn(self, text, url):
        return format_html('<a class="button" href="{}">{}</a>', url, text)

    # -------- USER PREVIEW PAGES --------
    def dashboard(self, obj):
        return self._btn(
            "Dashboard",
            reverse("budget:admin_user_dashboard", args=[obj.id])
        )
    dashboard.short_description = "Dashboard"

    def profile_btn(self, obj):
        return self._btn(
            "Profile",
            reverse("budget:admin_user_profile", args=[obj.id])
        )
    profile_btn.short_description = "Profile"

    def savings(self, obj):
        return self._btn(
            "Savings",
            reverse("budget:admin_user_savings", args=[obj.id])
        )
    savings.short_description = "Savings"

    def reports(self, obj):
        return self._btn(
            "Reports",
            reverse("budget:admin_user_reports", args=[obj.id])
        )
    reports.short_description = "Reports"

    # -------- ADMIN FILTERED DATA --------
    def income(self, obj):
        url = (
            reverse("admin:budget_income_changelist")
            + f"?user__id__exact={obj.id}"
        )
        return self._btn("Income", url)
    income.short_description = "Income"

    def expense(self, obj):
        url = (
            reverse("admin:budget_expense_changelist")
            + f"?user__id__exact={obj.id}"
        )
        return self._btn("Expense", url)
    expense.short_description = "Expense"

    def budget(self, obj):
        url = (
            reverse("admin:budget_budget_changelist")
            + f"?user__id__exact={obj.id}"
        )
        return self._btn("Budget", url)
    budget.short_description = "Budget"

    def delete_user(self, obj):
        return format_html(
            '<a class="button" style="background:#dc3545;color:white" '
            'href="{}">Delete</a>',
            reverse("admin:auth_user_delete", args=[obj.id])
        )
    delete_user.short_description = "Delete"


# ==================================================
# OTHER MODELS
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

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "dashboard_link")

    def dashboard_link(self, obj):
        url = reverse("budget:admin_user_dashboard", args=[obj.id])
        return format_html('<a href="{}">View Dashboard</a>', url)

    dashboard_link.short_description = "Dashboard"

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)