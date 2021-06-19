from django.shortcuts import get_object_or_404
from .serializers import (
    UserRegisterSerializer, 
    UserLoginSerializer,
    UserProfileSerializer,
    UserProfileSettingSerializer,
    ResetPwdSerializer,
    FriendSerializer,
    GroupSerializer,
    FriendRequestSerializer,
)
from django.contrib.auth import authenticate
from rest_framework import status, generics, mixins, viewsets

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from .models import User,Profile,Group,Friendship, FriendRequest

# Create your views here.
# 계정 관련 ViewSet
# 프로필 조회, 목록 조회
class UserViewSet(viewsets.ModelViewSet):
    '''
    ## 사용자 관련 정보 반환
    '''
    queryset = Profile.objects.all()
    serializer_class = UserProfileSerializer

# 친구 조회 및 등록, 삭제
class FriendViewSet(viewsets.ViewSet):
    
    def retrieve(self, request, pk=None):
        '''
        ## 친구 목록 조회하기
        ### API url에 pk를 받아서 조회
        '''
        user = get_object_or_404(User, id=pk)
        queryset = Friendship.objects.filter(me=user)
        return Response({"friends":[{
             "id": f.counterpart.get_user_id(),
             "username": f.counterpart.get_username(),
             "profile_img" : Profile.objects.get(user=f.counterpart).get_profile_img()
            }
             for f in queryset]})

    def create(self, request):
        '''
        ## 친구 요청하기
        ### 토큰을 통해서 신청자를 구분한다.
        '''
        user = request.user
        friend = get_object_or_404(User, id=request.data['sendTo'])
        # 친구 관계인지 우선 파악해야할 것
        friendship_set = Friendship.objects.filter(me=user, counterpart=friend)
        if friendship_set.exists():
            return Response({"response":"already friend"}, status=status.HTTP_400_BAD_REQUEST)

        # 요청을 이전에 보냈었는지 파악해야할 것
        friend_request_set = FriendRequest.objects.filter(sender=user, receiver=friend)
        if friend_request_set.exists():
            return Response({"response":"already requested"}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest.objects.create(sender=user, receiver=friend)
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data)

    def update(self, request, pk=None):
        '''
        ## 친구 추가
        ### API url에 pk를 받지만 실제론 토큰을 통해서 사용자를 구분한다.
        '''
        user = request.user
        friend = get_object_or_404(User, id=request.data['friend'])
        
        # 친구 요청을 보냈는지 먼저 확인
        friend_request_set = FriendRequest.objects.filter(sender=friend, receiver=user)
        if friend_request_set.exists():
            friend_request_set[0].delete()
        else:
             return Response({"response":"there are no requests to you"}, status=status.HTTP_400_BAD_REQUEST)

        # 중복 생성 방지
        friendship_set = Friendship.objects.filter(me=user, counterpart=friend)
        if friendship_set.exists():
            return Response({"response":"already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        friendship = Friendship.objects.create(me=user, counterpart=friend)
        # 반대편도 생성해준다.
        Friendship.objects.create(me=friend, counterpart=user)
        serializer = FriendSerializer(friendship)
        return Response(serializer.data)

    def destroy(self, request ,pk=None):
        '''
        ## 친구 삭제
        ### API url에 pk를 받지만 실제론 토큰을 통해서 사용자를 구분한다.
        '''
        user = request.user
        friend = get_object_or_404(User, id=request.data['friend'])
        friendship=get_object_or_404(Friendship, me=user, counterpart=friend)
        friendship.delete()
        friendship=get_object_or_404(Friendship, me=friend, counterpart=user)
        friendship.delete()
        
        return Response({"response":"success"})    

# 그룹 생성, 조회, 목록 조회, 수정, 삭제
class GroupViewSet(viewsets.ViewSet):

    def list(self, request):
        '''
        ## 그룹주가 만든 그룹 목록 확인하기
        ### 토큰 받아서 그룹주 식별함
        '''
        queryset = Group.objects.filter(master=request.user)
        serializer = GroupSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        '''
        ## 그룹 생성하기
        ### 토큰 받아서 그룹 주인을 정하고, 친구 목록 중에서 그룹 멤버로 데려올 수 있음.
        '''
        data = request.data
        # 그룹 이름은 중복되어서는 안된다.
        group_set = Group.objects.filter(master=request.user, name=data['name'])
        if group_set.exists():
            return Response({"response":"group name already exists"}, status=status.HTTP_400_BAD_REQUEST)

        new_group = Group.objects.create(
            master=request.user, name=data['name'], img=data['img']    
        )
        new_group.save()

        for member_id in data['members']:
            try:
                member = Friendship.objects.get(me_id=request.user.get_user_id(), counterpart_id=member_id)
            except Friendship.DoesNotExist:
                pass
            new_group.members.add(member)
        
        serializer = GroupSerializer(new_group)
        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        '''
        ## 그룹 조회하기
        ### API url에 pk를 받아서 조회
        '''
        group = get_object_or_404(Group,id=pk)
        serializer = GroupSerializer(group)
        return Response(serializer.data)

    def update(self, request, pk=None):
        '''
        ## 그룹 정보 수정
        ### 토큰을 통해서 그룹의 주인을 인증하고, pk를 통해서 그룹의 번호에 접근한다.
        '''
        data = request.data
        group = Group.objects.get(master=request.user, id=pk)
        if 'name' in data:
            group.name= data['name']
        if 'img' in data:
             group.img= data['img']
        
        group.save()
        if 'members' in data:
            group.members.clear()
            for member_id in data['members']:
                try:
                    friendship = Friendship.objects.get(me=request.user, counterpart_id=member_id)
                except Friendship.DoesNotExist:
                    pass
                group.members.add(friendship)
        serializer = GroupSerializer(group)
        return Response(serializer.data)

    def destroy(self, request ,pk=None):
        '''
        ## 그룹 삭제
        ### 토큰을 통해서 그룹의 주인을 인증하고, pk를 통해서 그룹의 번호에 접근한다.
        '''
        data = request.data
        group = get_object_or_404(Group, master=request.user, id=pk)
        group.delete()
        return Response({"response":"Successfully deleted"})    


# 계정 생성 API
class UserCreateAPI(generics.CreateAPIView):
    serializer_class=UserRegisterSerializer
    def post(self, request, *args, **kwargs):
        '''
        ## 계정 생성 API
        '''
        return self.create(request, *args, **kwargs)

# 계정 로그인 API
class UserLoginAPI(generics.CreateAPIView):
    serializer_class=UserLoginSerializer
    def post(self, request):
        '''
        ## 계정 로그인 API
        '''
        context={}
        email=request.data['email']
        password=request.data['password']
        # 사용자의 정보를 맞추어보고 해당 user가 있으면 반환한다.
        user=authenticate(email=email, password=password)
        
        if user:
            try:
                token=Token.objects.get(user=user)
                friend_request = FriendRequest.objects.filter(receiver=user)
            except Token.DoesNotExist:
                toekn=Token.objects.create(user=user)
            context['response']="성공적으로 인증되었습니다"
            context['id']=user.id
            context['email']=email
            context['token']=token.key
            context['friend_request']=[fr.sender.get_user_id() for fr in friend_request]
            print(request.user)
            return Response(context, status=status.HTTP_200_OK)
        else:
            context['response']="에러가 발생했습니다"
            context['error_message']="인증에 실패했습니다"
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

# 비밀번호 수정
class ResetPwdView(viewsets.ViewSet):
    
    def update(self, request, pk=None):
        '''
        ## 비밀번호 변경
        ### API url에 pk를 받지만 실제론 토큰을 통해서 계정을 구분한다.
         '''
        data = request.data
        user = User.objects.get(email=request.user)
        serializer = ResetPwdSerializer(user, data=data)
        if serializer.is_valid():
            # 토큰 변경
            token = Token.objects.get(user_id=request.user.get_user_id())
            token.delete()
            Token.objects.create(user_id=request.user.get_user_id())
            # 비밀번호 변경
            user.set_password(data['password'])
            user.save()
            response=serializer.data
            response['response']='Successfully password changed '
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        



   
        