from django.urls import path
from . import views
from . import views_admin

app_name = "budget"

urlpatterns = [
    # --------------------
    # Budget CRUD
    # --------------------
    path("", views.budget_list, name="list"),
    path("create/", views.budget_create, name="create"),
    path("edit/<int:id>/", views.edit_budget, name="edit"),
    path("delete/<int:pk>/", views.budget_delete, name="delete"),

    # --------------------
    # ADMIN – USER PREVIEW PAGES
    # --------------------
    path(
        "admin/user/<int:user_id>/dashboard/",
        views.admin_user_dashboard,
        name="admin_user_dashboard",
    ),
    path(
        "admin/user/<int:user_id>/profile/",
        views.admin_user_profile,
        name="admin_user_profile",
    ),
    path(
        "admin/user/<int:user_id>/income/",
        views.admin_user_income,
        name="admin_user_income",
    ),
    path(
        "admin/user/<int:user_id>/expense/",
        views.admin_user_expense,
        name="admin_user_expense",
    ),
    path(
        "admin/user/<int:user_id>/savings/",
        views.admin_user_savings,
        name="admin_user_savings",
    ),
    path(
        "admin/user/<int:user_id>/reports/",
        views.admin_user_reports,
        name="admin_user_reports",
    ),
    path(
        "admin/user/<int:user_id>/budget/",
        views.admin_user_budget,
        name="admin_user_budget",
    ),
        path(
        "admin/export/csv/user/<int:user_id>/",
        views_admin.admin_export_csv_single_user,
        name="admin_export_csv_single_user"
    ),

    path(
        "admin/export/pdf/user/<int:user_id>/",
        views_admin.admin_export_pdf_single_user,
        name="admin_export_pdf_single_user"
    ),
    path(
    "admin/user/<int:user_id>/dashboard/",
    views_admin.admin_user_dashboard,
    name="admin_user_dashboard"
),

]
