from django.shortcuts import get_object_or_404
from .serializers import (
    UserRegisterSerializer, 
    UserLoginSerializer,
    UserSerailizer,
    UserProfileSerializer,
    UserProfileSettingSerializer,
    ResetPwdSerializer,
    FriendSerializer,
    FriendRequestSerializer,
)
from django.contrib.auth import authenticate
from rest_framework import status, generics, mixins, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from .models import User,Profile,Friendship, FriendRequest

# Create your views here.
# 계정 관련 ViewSet
# 프로필 조회, 목록 조회
class UserViewSet(viewsets.ModelViewSet):
    '''
    ## 사용자 관련 정보 반환
    '''
    queryset = Profile.objects.all()
    serializer_class = UserProfileSerializer
    
    # username, profile_img, region
    def update(self,request,*args, **kwargs):
        profile = Profile.objects.get(user=request.user)
        print(request.user)
        if 'username' in request.data:
            profile.user.username = request.data['username']
            profile.user.save()
        if 'region' in request.data:
            profile.region = request.data['region']
        if 'status_msg' in request.data:
            profile.status_msg = request.data['status_msg']
        if 'profile_img' in request.data:
            profile.profile_img =request.data['profile_img']
        profile.save()
        response={}
        response['response']='Successfully changed'
        return Response(response)
        
# 친구 요청 조회, 요청, 요청삭제하기 API
class FriendRequestViewSet(viewsets.ViewSet):
    def list(self, request):
        '''
        ## 친구 요청 조회하기
        '''
        friend_request = FriendRequest.objects.filter(receiver=request.user)
        return Response ({"requests": [UserLoginSerializer(fr.sender).data for fr in friend_request]})

    def retrieve(self, request, pk=None):
        '''
        ## 친구 요청 대기 조회하기
        '''
        flag = False
        receiver = get_object_or_404(User, id=pk)
        if FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists():
            flag = True
        return Response({"pending": flag})

    def create(self, request):
        '''
        ## 친구 요청하기
        ### 토큰을 통해서 신청자를 구분한다.
        '''
        user = request.user
        friend = get_object_or_404(User, id=request.data['sendTo'])

        # 본인인 경우
        if request.user == friend:
            return Response({"response": "user and friend are same"}, status=status.HTTP_400_BAD_REQUEST)

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
    def destroy(self, request ,pk=None):
        '''
        ## 친구 요청 삭제
        '''
        user = request.user
        friend = get_object_or_404(User, id=pk)
        friend_request_set = get_object_or_404(FriendRequest, sender=friend, receiver=user)
        friend_request_set.delete()
        
        return Response({"response":"success"}) 

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
             "profile_img" : Profile.objects.get(user=f.counterpart).get_profile_img(),
             "status_msg" :  Profile.objects.get(user=f.counterpart).get_status_msg()
            }
             for f in queryset]})

    def create(self, request):
        '''
        ## 친구 추가
        ### API url에 pk를 받지만 실제론 토큰을 통해서 사용자를 구분한다.
        '''
        user = request.user
        friend = get_object_or_404(User, id=request.data['friend'])
        # 본인인 경우
        if request.user == friend:
            return Response({"response": "user and friend are same"}, status=status.HTTP_400_BAD_REQUEST)

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
        '''
        user = request.user
        friend = get_object_or_404(User, id=pk)
        friendship = get_object_or_404(Friendship, counterpart=friend, me=user)
        friendship.delete()
        friendship = get_object_or_404(Friendship, counterpart=user, me=friend)
        friendship.delete()
        
        return Response({"response":"success"})    





class EmailRedundancyCheckAPI(generics.RetrieveAPIView):
    serializer_class=UserLoginSerializer
    def get(self, request):
        '''
        ## 이메일 중복 확인
        '''
        redundancy = False
        if User.objects.filter(email=request.GET.get('email')).exists():
            redundancy = True
        return Response ({"redundancy": redundancy})

class UsernameRedundancyCheckAPI(generics.RetrieveAPIView):
    serializer_class=UserLoginSerializer
    def get(self, request):
        '''
        ## username 중복 확인
        '''
        redundancy = False
        if User.objects.filter(username=request.GET.get('username')).exists():
            redundancy = True
        return Response ({"redundancy": redundancy})

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
                
            except Token.DoesNotExist:
                toekn=Token.objects.create(user=user)
            context['response']="성공적으로 인증되었습니다"
            context['id']=user.id
            context['email']=email
            context['username']=user.get_username()
            context['profile_img']=Profile.objects.get(user=user).get_profile_img()
            context['region']=Profile.objects.get(user=user).get_region()
            context['token']=token.key
            return Response(context, status=status.HTTP_200_OK)
        else:
            context['response']="에러가 발생했습니다"
            context['error_message']="인증에 실패했습니다"
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

class UserSearchView(viewsets.ViewSet):
    def list(self, request):
        queryset = User.objects.filter(username__startswith=request.GET.get('search','')).exclude(id=request.user.get_user_id())
        for friendship in Friendship.objects.filter(me=request.user):
            queryset = queryset.exclude(id = friendship.counterpart.get_user_id())
        serializer = UserSerailizer(queryset, many=True)
        return Response(serializer.data)

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
        



   
        