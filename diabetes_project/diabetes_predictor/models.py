from django.db import models
from django.contrib.auth.models import User

class DiabetesHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.FloatField()
    gender = models.CharField(max_length=10)
    hypertension = models.BooleanField()
    heart_disease = models.BooleanField()
    smoking_history = models.CharField(max_length=20)
    bmi = models.FloatField()
    hba1c_level = models.FloatField()
    blood_glucose_level = models.FloatField()
    result = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.result}"
