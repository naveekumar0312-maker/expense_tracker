from django.apps import AppConfig   # ✅ THIS LINE WAS MISSING

class BudgetConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "budget"

    def ready(self):
        import budget.signals
