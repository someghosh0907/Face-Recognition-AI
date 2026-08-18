from django.db import models

class User(models.Model):
    class Gender(models.TextChoices):
        MALE = "Male", "male"
        FEMALE = "Female", "female"
        OTHER = "Other", "other"

    employee_id = models.CharField(
        max_length=20,
        unique=True
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=100, blank=False)
    designation = models.CharField(max_length=100, blank=False)
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices
    )
    joining_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def create_employee_id(self):
        prefix = "EMP"
        last_user = User.objects.order_by("-id").first()
        if last_user:
            last_id = int(last_user.employee_id.replace(prefix, ""))
            new_id = last_id + 1
        else:
            new_id = 1
        return f"{prefix}{new_id:04d}"
        

    def __str__(self):
        return f"{self.employee_id} - {self.first_name} - {self.last_name}"