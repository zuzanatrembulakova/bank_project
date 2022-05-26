from django.db import models

class LoginCode(models.Model):
    code = models.IntegerField()
    # img = models.CharField(default='undefined', max_length=200)

    def __str__(self):
        return f"{self.code}" 

# Create your models here.
