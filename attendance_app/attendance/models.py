from django.db import models
from user.models import User
class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "Present", "present"
        ABSENT = "Absent", "absent"
        LATE = "Late", "late"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="attendance"
    )

    attendance_date = models.DateField()

    check_in = models.DateTimeField(
        null=True,
        blank=True
    )

    check_out = models.DateTimeField(
        null=True,
        blank=True
    )

    confidence_score = models.FloatField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRESENT
    )

    device_name = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "attendance_date"],
                name="unique_daily_attendance"
            )
        ]

    def __str__(self):
        return f"{self.user.employee_id} - {self.attendance_date}"