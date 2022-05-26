from datetime import datetime
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
    accountNumber = models.CharField(max_length=3)
    isLoan = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.accountNumber}"

class AccountMovement(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    fromAccount = models.CharField(max_length=20, default='undefined')
    value = models.DecimalField(max_digits=30, decimal_places=2)
    timestamp = models.DateTimeField(default=now, editable=False)
    description = models.TextField()

    def __str__(self):
        return f"{self.value} - {self.timestamp} - {self.description}"

class Bank(models.Model):
    bankCode = models.CharField(max_length=4)
    path = models.CharField(max_length=250)
    
    def __str__(self):
        return f"{self.bankCode} - {self.path}"

class LoanRequest(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE) 
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    loanAccount = models.CharField(max_length=250, default='undefined')
    loanAmount = models.DecimalField(max_digits=30, decimal_places=2)
    # remainingAmount = models.IntegerField()
    confirmed = models.CharField(max_length=100, default='undefined')
    # confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.account} - {self.loanAmount} - {self.remainingAmount} - {self.confirmed}"

class AutomaticPayment(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    to_account = models.CharField(max_length=250, default='undefined')
    value = models.DecimalField(max_digits=30, decimal_places=2)
    description = models.TextField()
    repeat_number = models.IntegerField(help_text="number of payment repeats")
    repeat_every = models.IntegerField(help_text="how often should we repeat payment (in minutes)")
    timestamp = models.DateTimeField(default=now, editable=False, help_text="time of last payment")

    def __str__(self):
        return f"{self.account} - {self.to_account} - {self.value} - {self.repeat_number} - {self.timestamp}"

class CreditCard(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    cardNumber = models.IntegerField()
    initialBalance = models.DecimalField(max_digits=30, decimal_places=2)
    spentAmount = models.DecimalField(max_digits=30, decimal_places=2)
    expiryDate = models.DateField(editable=False)
    # expiryDate = models.DateTimeField(default=now, editable=False)
    cvvNumber = models.IntegerField()
    interest = models.DecimalField(max_digits=30, decimal_places=2)

    def __str__(self):
        return f"{self.cardNumber} - {self.initialBalance} - {self.spentAmount} - {self.expiryDate} - {self.cvvNumber}"

class CardMovement(models.Model):
    card = models.ForeignKey(CreditCard, on_delete=models.CASCADE)
    toFrom = models.CharField(max_length=20, default='undefined')
    value = models.DecimalField(max_digits=30, decimal_places=2)
    timestamp = models.DateTimeField(default=now, editable=False)
    description = models.TextField()

    def __str__(self):
        return f"{self.value} - {self.timestamp} - {self.description}"
