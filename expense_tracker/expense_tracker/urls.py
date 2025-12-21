from django.contrib import admin
from django.urls import path, include
from budget import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('', views.dashboard, name='dashboard'),

    path('profile/', views.profile, name='profile'),
    path('view-profile/', views.view_profile, name='view_profile'),
    path("delete-profile/", views.delete_profile, name="delete_profile"),


    path('categories/', views.categories, name='categories'),
    path('income/', views.income, name='income'),
    path('expense/', views.expense, name='expense'),

    path('budget/', include('budget.urls', namespace='budget')),

    path("change-password/", views.change_password, name="change_password"),
    path('register/', views.register_view, name='register'),

    path('reports/', views.reports, name='reports'),
    path('savings/', views.savings, name='savings'),

    path("category/delete/<int:id>/", views.delete_category, name="delete_category"),
    
    path("income/delete/<int:id>/", views.delete_income, name="delete_income"),
    
    path("expense/delete/<int:id>/", views.delete_expense, name="delete_expense"),

    path("category/edit/<int:id>/", views.edit_category),
    path("income/edit/<int:id>/", views.edit_income),
    path("expense/edit/<int:id>/", views.edit_expense),

    path("export/csv/all/", views.export_csv_all, name="export_csv_all"),
    path("export/pdf/all/", views.export_pdf_all, name="export_pdf_all"),


]

# ⭐⭐⭐ VERY IMPORTANT — SERVE MEDIA FILES LIKE PROFILE PIC ⭐⭐⭐
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

