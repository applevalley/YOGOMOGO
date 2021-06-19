from django.db import models
from accounts.models import Profile, User
from group.models import Group
from django.conf import settings
# Create your models here.
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
    image = models.URLField(default='')
    score = models.FloatField(default=0)
    
    @property
    def category_list(self):
        return self.category.split("|") if self.category else []

class Review(models.Model):
    '''
    restaurant_id = 식당의 id 값
    restaurant_info = 식당의 정보
    theme = 테마(연인, 회식, 가족, 친구)
    title = 리뷰의 제목
    group = 같이 동행한 그룹의 id 값
    contents = 리뷰의 내용
    score = 리뷰에서 식당에 매긴 평점
    writer = 리뷰 작성자
    headcount = 동행한 인원 수
    viewed_num = 해당 리뷰가 조회된 수
    tags = 리뷰에서 지정한 태그
    '''
    restaurant_id = models.PositiveIntegerField(default=0)
    restaurant_info = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='review_restaurant_info', null=True)
    theme = models.CharField(max_length=10)
    title = models.CharField(max_length=150)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='review_group',null=True)
    contents = models.TextField()
    score = models.PositiveSmallIntegerField(default=0)
    writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_user')
    headcount = models.PositiveSmallIntegerField(default=0)
    viewed_num = models.PositiveIntegerField(default=0)
    tags = models.TextField(blank=True)
    bookmarked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Menu(models.Model):
    store = models.PositiveIntegerField()
    menu = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    image = models.URLField(default='')


class Bookmark(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='review_bookmark')
    bookmark_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmark_user')
    created_at = models.DateTimeField(auto_now_add=True)

class Images(models.Model):
    '''
    리뷰 작성시 입력하는 이미지들을 저장
    '''
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='review_image')
    image = models.URLField()


class UserRecommend(models.Model):
    recommend_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommend_user')
    restaurant_id = models.PositiveIntegerField()
    restaurant_name = models.CharField(max_length=100)
    restaurant_address = models.CharField(max_length=100)


class GroupRecommend(models.Model):
    recommend_group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='recommend_group')
    restaurant_id = models.PositiveIntegerField()
    restaurant_name = models.CharField(max_length=100)
    restaurant_address = models.CharField(max_length=100)