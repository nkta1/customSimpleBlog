from django.db import models


class Person(models.Model):
    first_name = models.TextField()
    last_name = models.TextField()
    login = models.CharField(max_length=20, primary_key=True)
    password = models.CharField(max_length=20)
    admin = 'admin'
    user = 'user'
    statusValues = ((admin, 'admin'), (user, 'user'))
    status = models.CharField(choices=statusValues, default=user, max_length=5)
    token = models.CharField(max_length=30, unique=True)


class Post(models.Model):
    name = models.TextField()
    content = models.TextField()
