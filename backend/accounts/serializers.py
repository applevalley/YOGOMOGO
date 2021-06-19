from rest_framework import serializers
from .models import User, Profile, Friendship, FriendRequest
from group.models import Group

class UserRegisterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=User
        fields=['email','username','password']
        
        # post나 put과 같이 데이터를 쓰는 것은 가능하나, 조회는 불가능하게 설정
        extra_kwargs ={
            'password' : {'write_only':True}
        }
    
    # 검증 과정은 프론트엔드에서 하기 때문에 생략
    def save(self):
        user = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
        )
        # 비밀번호를 암호화해서 저장하기 위해 반드시 set_password 사용할 것
        user.set_password(self.validated_data['password'])
        user.save()


class UserLoginSerializer(serializers.ModelSerializer):
    profile_img=serializers.SerializerMethodField()
    status_msg = serializers.SerializerMethodField()
    class Meta:
        model=User
        fields=['id','email','username','profile_img','password','status_msg']
        read_only_fields=('id','username', 'profile_img','status_msg')
        
        # post나 put과 같이 데이터를 쓰는 것은 가능하나, 조회는 불가능하게 설정
        extra_kwargs ={
            'password' : {'write_only':True}
        }
    def get_profile_img(self, user):
        return Profile.objects.get(user=user).get_profile_img()
    def get_status_msg(self, user):
        return Profile.objects.get(user=user).get_status_msg()


class UserSerailizer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=("id","username", "email")

class UserProfileSerializer(serializers.ModelSerializer):
    user=UserSerailizer()
    friends=serializers.SerializerMethodField()
    groups=serializers.SerializerMethodField()

    class Meta:
        model=Profile
        fields=('user','profile_img', 'region','friends','groups','status_msg')

    def get_friends(self, profile):
        user = User.objects.get(email=profile.user)
        return[{'id':f.counterpart.get_user_id(), 'email':str(f.counterpart), 'username':f.counterpart.get_username(), 'profile_img':Profile.objects.get(user=f.counterpart).get_profile_img()} 
                for f in Friendship.objects.filter(me=user)] 

    def get_groups(self, profile):
        user = User.objects.get(email=profile.user)
        return [
            {'id':group.id, 
            'name':group.name,
            'img':group.img,
            'members':[{'id':m.counterpart.get_user_id(), 'email':str(m.counterpart), 'username':m.counterpart.get_username(), 'profile_img':Profile.objects.get(user=m.counterpart).get_profile_img()}
             for m in group.members.all()]}
        for group in Group.objects.filter(master=user)]


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model=Friendship
        fields=('counterpart',)

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model=FriendRequest
        fields='__all__'


 

class UserProfileSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields=['region']


class ResetPwdSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields=['email','password']
        extra_kwargs ={
            'password' : {'write_only':True},
            'email': {'read_only':True}
        }


#TODO:    
'''
리뷰 갯수 불러오기
한달동안 리뷰 갯수 불러오기
serializer 활용하는 방법 알아보기
'''
