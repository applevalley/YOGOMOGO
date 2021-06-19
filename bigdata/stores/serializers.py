from rest_framework import serializers, fields
from accounts.models import User, Profile
from .models import Restaurant, Review, group_list


class RestaurantInfoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Restaurant
        fields = ['id', 'store_name', 'address']


class WriterSerializer(serializers.ModelSerializer):
    profile_img=serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'profile_img']
    def get_profile_img(self, user):
        return Profile.objects.get(user=user).profile_img


class UserFeedSerializer(serializers.ModelSerializer):
    restaurant = RestaurantInfoSerializer(read_only=True)
    writer = WriterSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'image', 'theme', 'title', 'score', 'headcount', 'restaurant',
        'writer', 'viewed_num']


class RestaurantSerializer(serializers.ModelSerializer):
    reviewd_num=serializers.SerializerMethodField()
    class Meta:
        model = Restaurant
        fields = '__all__'
    def get_reviewd_num(self, restaurant):
        return Review.objects.filter(restaurant=restaurant).count()


class ReviewSerializer(serializers.ModelSerializer):
    restaurant = RestaurantInfoSerializer(read_only=True)
    writer = WriterSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'




