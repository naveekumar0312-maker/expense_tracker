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
# 👤 CUSTOM USER ADMIN
# ==================================================
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "dashboard",
        "income",
        "expense",
        "budget",
        "reports",
        "delete_user",
    )

    search_fields = ("username", "email")

    # 🔥 hide superusers
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_superuser=False)

    def _btn(self, text, url):
        return format_html('<a class="button" href="{}">{}</a>', url, text)

    def dashboard(self, obj):
        return self._btn(
            "Dashboard",
            reverse("budget:admin_user_dashboard", args=[obj.id])
        )

    def income(self, obj):
        return self._btn(
            "Income",
            reverse("admin:budget_income_changelist") + f"?user__id__exact={obj.id}"
        )

    def expense(self, obj):
        return self._btn(
            "Expense",
            reverse("admin:budget_expense_changelist") + f"?user__id__exact={obj.id}"
        )

    def budget(self, obj):
        return self._btn(
            "Budget",
            reverse("admin:budget_budget_changelist") + f"?user__id__exact={obj.id}"
        )

    def reports(self, obj):
        return self._btn(
            "Reports",
            reverse("budget:admin_user_reports", args=[obj.id])
        )

    def delete_user(self, obj):
        return format_html(
            '<a class="button" style="background:#dc3545;color:white" '
            'href="{}">Delete</a>',
            reverse("admin:auth_user_delete", args=[obj.id])
        )


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