from rest_framework import serializers
from accounts.models import User
from stores.models import Restaurant, Review, Images
from stores.serializers import GroupRecommendRestaurantSerializer
from accounts.serializers import UserSerailizer, UserLoginSerializer
from .models import Group


class GroupRecommendStoreSerializer(serializers.Serializer):
    group_id = serializers.SerializerMethodField()
    recomm_stores = serializers.SerializerMethodField()
    def get_group_id(self, group):
        return group.id
    def get_recomm_stores(self, restaurant):
        store_review = Review.objects.get(restaurant_id=restaurant.id)
        print(store_review)
        store_image = Images.objects.filter(review=store_review)
        return [
            {
                'id': restaurant.id,
                'store_name': restaurant.store_name,
                'address': restaurant.address,
                'image': [ img.image for img in store_image],
                'score': restaurant.score,
                'reviewed_num': Review.objects.filter(restaurant=restaurant).count()
            }
        ]


class GroupReviewSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = ['id', 'title', 'contents', 'image', 'updated_at']

    def get_image(self, review):
        return [ single_img.image for single_img in Images.objects.filter(review=review) ] 


class GroupSerializer(serializers.ModelSerializer):
    master=UserSerailizer(read_only=True)
    members=serializers.SerializerMethodField()
    class Meta:
        model=Group
        fields=('id', 'master', 'name', 'img', 'members')
        extra_kwargs ={
            'id' : {'read_only':True}
        }
    def get_members(self, group):
        return [ (UserLoginSerializer(User.objects.get(id=f.counterpart_id))).data for f in group.members.filter(me__id=group.master.get_user_id())]
