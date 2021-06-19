from rest_framework import serializers, fields
from accounts.models import User, Profile
from .models import Restaurant, Review, group_list, Images, Bookmark, UserRecommend, Menu, GroupRecommend


class RestaurantInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'store_name', 'address', 'image',]


class WriterSerializer(serializers.ModelSerializer):
    profile_img=serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_img']
    def get_profile_img(self, user):
        return Profile.objects.get(user=user).profile_img


class UserFeedSerializer(serializers.ModelSerializer):
    restaurant = RestaurantInfoSerializer(read_only=True)
    writer = WriterSerializer(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'image', 'theme', 'title', 'score', 'headcount', 'restaurant',
        'writer', 'viewed_num']
    
    def get_image(self, review):
        return [ single_img.image for single_img in Images.objects.filter(review=review) ] 


class GroupRecommendRestaurantSerializer(serializers.ModelSerializer):
    reviewed_num=serializers.SerializerMethodField()
    class Meta:
        model = Restaurant
        fields = ['id', 'store_name', 'address', 'score', 'reviewed_num']
        # fields = ['id', 'store_name', 'address', 'image', 'score', 'reviewed_num']
    def get_reviewed_num(self, restaurant):
        return Review.objects.filter(restaurant_info=restaurant).count()


class RestaurantSerializer(serializers.ModelSerializer):
    reviewed_num=serializers.SerializerMethodField()
    class Meta:
        model = Restaurant
        fields = '__all__'
    def get_reviewed_num(self, restaurant):
        return Review.objects.filter(restaurant_info=restaurant).count()


class RestaurantMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['menu', 'price']


class RestaurantDetailSerializer(serializers.ModelSerializer):
    menus = serializers.SerializerMethodField()
    class Meta:
        model = Restaurant
        fields = ['id', 'store_name', 'image', 'menus', 'address', 'score', 'category', 'tel', 'longitude', 'latitude']
    def get_menus(self, restaurant):
        return [{"name": single_menu.menu, "price": single_menu.price, "image": single_menu.image} for single_menu in Menu.objects.filter(store=restaurant.id)]


class BestRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'store_name', 'address']


class ReviewThemeSerializer(serializers.ModelSerializer):
    restaurant_info = RestaurantInfoSerializer(read_only=True)
    writer = WriterSerializer(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'image', 'theme', 'title', 'score', 'headcount', 'restaurant_info', 'writer', 'bookmarked', 'viewed_num']

    def get_image(self, review):
        return [ single_img.image for single_img in Images.objects.filter(review=review) ] 


class ReviewSerializer(serializers.ModelSerializer):
    restaurant_info = RestaurantSerializer(read_only=True)
    writer = WriterSerializer(read_only=True)
    tags = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = '__all__'

    def get_tags(self, review):
        return review.tags.split('|')

    def get_image(self, review):
        return [ single_img.image for single_img in Images.objects.filter(review=review) ] 


class ReviewImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Images
        fields = '__all__'


class ReviewBookmarkSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Bookmark
        fields = ['id', 'review', 'created_at', 'image']
    def get_image(self, bookmark):
         return [ single_img.image for single_img in Images.objects.filter(review=bookmark.review) ] 


class UserRecommendSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserRecommend
        fields = '__all__'


class GroupRecommendSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupRecommend
        fields = '__all__'
