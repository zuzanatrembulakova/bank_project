from django.db import models

class LoginCode(models.Model):
    code = models.IntegerField()

    def __str__(self):
        return f"{self.code}"

# Create your models here.
