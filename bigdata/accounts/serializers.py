from rest_framework import serializers
from .models import User, Profile, Group, Friendship, FriendRequest

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
    class Meta:
        model=User
        fields=['email','password']
        
        # post나 put과 같이 데이터를 쓰는 것은 가능하나, 조회는 불가능하게 설정
        extra_kwargs ={
            'password' : {'write_only':True}
        }

class UserProfileSerializer(serializers.ModelSerializer):
    user=serializers.SerializerMethodField()
    groups=serializers.SerializerMethodField()
    class Meta:
        model=Profile
        fields=('user','profile_img', 'region','groups')
    def get_user(self, profile):
        user = User.objects.get(email=profile.user)
        friends =[{'id':f.counterpart.get_user_id(), 'email':str(f.counterpart), 'username':f.counterpart.get_username()} for f in Friendship.objects.filter(me=user)] 
        return {'id': user.get_user_id(), 'email':str(user), 'username': user.get_username(), 'friends':friends}
    def get_groups(self, group):
        user = User.objects.get(email=group.user)
        return [
            {'id':group.id, 
            'name':group.name,
            'img':group.img,
            'members':[friendship.counterpart.get_user_id() for friendship in group.members.all()]}
        for group in Group.objects.filter(master=user)]


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model=Friendship
        fields=('counterpart',)

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model=FriendRequest
        fields='__all__'


class GroupSerializer(serializers.ModelSerializer):
    members=serializers.SerializerMethodField()
    class Meta:
        model=Group
        fields=('id', 'master', 'name', 'img', 'members')
        extra_kwargs ={
            'id' : {'read_only':True}
        }
    def get_members(self, group):
        return [ f.counterpart_id for f in group.members.filter(me__id=group.master.get_user_id())]
 

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
친구 동의하기 ㅠㅠ (??? 어떻게 해야할지 난감)
리뷰 불러오기
'''
