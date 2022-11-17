from django.db import models
from django.contrib.sessions.backends.db import SessionStore as DBStore
from django.contrib.sessions.base_session import AbstractBaseSession
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.contrib.auth.models import User


class DataUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    region = models.CharField(max_length=100)

class DataOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    urls_list = models.CharField(max_length=4000)
    status = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)

class DataPrice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.CharField(max_length=100)
    date = models.DateTimeField()


