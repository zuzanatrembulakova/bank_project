from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Ranking(models.Model):
    rType = models.CharField(max_length=200)
    loan = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.rType} - {self.loan}"

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.IntegerField()
    ranking = models.ForeignKey(Ranking, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.phone}"

class Account(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    accountNumber = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.accountNumber}"

class AccountMovement(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    value = models.IntegerField()
    timestamp = models.DateTimeField(default=now, editable=False)
    description = models.TextField()

    def __str__(self):
        return f"{self.value} - {self.timestamp} - {self.description}"

class Bank(models.Model):
    bankCode = models.CharField(max_length=4)
    path = models.CharField(max_length=250)
    
    def __str__(self):
        return f"{self.bankCode} - {self.path}"

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    loanAmount = models.IntegerField()
    remainingAmount = models.IntegerField()
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.loanAmount} - {self.remainingAmount}"
