from django.db import models
from accounts.models import User,Friendship
# Create your models here.
class Group(models.Model):
    '''
    ## master: 그룹 주
    ## name: 그룹 이름 
    ## img: 그룹 이미지
    ## members: 그룹 구성원 정보
    '''
    master = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name='그룹주', related_name="master_users")
    name = models.CharField('group name', max_length=50)
    img = models.URLField('group image', default='')
    members = models.ManyToManyField(Friendship)
    registered_time  = models.DateTimeField('registered time', auto_now_add=True)