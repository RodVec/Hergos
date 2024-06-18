from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10, unique=True)

    company_name = models.CharField(max_length=50)
    country = models.CharField(max_length=50, default="España")
    city = models.CharField(max_length=50, default="Madrid")
    
    code = models.CharField(max_length=9, unique=True)
    
    date = models.DateField(auto_now_add=True)

    email = models.EmailField(max_length=100, unique=True)

    email_is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'last_name', 'phone', 'company_name', 'country', 'city', 'code', 'username']

    def __str__(self):
        return self.name