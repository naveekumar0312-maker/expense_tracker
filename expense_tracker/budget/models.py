from django.db import models
from types import SimpleNamespace
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.utils import timezone


# ==============================
# CATEGORY MODEL
# ==============================
class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z ]+$',
                message="Category name must contain only alphabets"
            )
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user","name")

    def __str__(self):
        return self.name


# ==============================
# BUDGET MODEL
# ==============================
class Budget(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="budgets"
    )

    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="budgets"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # Budget Period Start Date
    start_date = models.DateField()

    # Budget Period End Date
    end_date = models.DateField()

    # Auto Derived Fields
    month = models.PositiveSmallIntegerField(editable=False)
    year = models.PositiveSmallIntegerField(editable=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.month = self.start_date.month
        self.year = self.start_date.year
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.category.name} - ₹{self.amount}"

    class Meta:
        ordering = ["-created_at"]


# ==============================
# INCOME MODEL
# ==============================
class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.source} - {self.amount}"


# ==============================
# EXPENSE MODEL
# ==============================
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    budget = models.ForeignKey(
        Budget, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.category} - {self.amount}"


# ==============================
# USER PROFILE MODEL
# ==============================

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    age = models.IntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to="profiles/", null=True, blank=True)

    def __str__(self):
        return self.user.username
