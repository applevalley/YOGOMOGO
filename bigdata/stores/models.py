from django.db import models
from accounts.models import Profile, User
from django.conf import settings


group_list = (
    ('family', '가족'),
    ('love', '연인'),
    ('friend', '친구'),
    ('company', '회식'),
)

class Restaurant(models.Model):
    store_name = models.CharField(max_length=100)
    branch = models.TextField(null=True)
    area = models.TextField(null=True)
    tel = models.TextField(null=True)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    address = models.TextField(null=True)
    category = models.TextField(null=True)
    
    @property
    def category_list(self):
        return self.category.split("|") if self.category else []


class Restaurant2(models.Model):
    store_name = models.CharField(max_length=100)
    branch = models.TextField(null=True)
    area = models.TextField(null=True)
    tel = models.TextField(null=True)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    address = models.TextField(null=True)
    category = models.TextField(null=True)


class Review(models.Model):
    store= models.PositiveSmallIntegerField()
    score = models.PositiveSmallIntegerField(default=0)
    user= models.TextField()
