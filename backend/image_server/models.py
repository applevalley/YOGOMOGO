from django.db import models

# Create your models here.

class ImagePost(models.Model):
    image = models.ImageField(upload_to="%Y/%m/%d")
    img_url = models.URLField()
