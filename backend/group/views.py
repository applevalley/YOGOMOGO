import json
import requests


from django.shortcuts import get_object_or_404
from rest_framework import status, generics, mixins, viewsets

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token

from accounts.models import User, Friendship
from .models import Group
from stores.models import Restaurant, Review, GroupRecommend
from .serializers import GroupRecommendStoreSerializer, GroupReviewSerializer, GroupSerializer
from stores.serializers import RestaurantSerializer, GroupRecommendRestaurantSerializer, GroupRecommendSerializer, ReviewThemeSerializer, RestaurantInfoSerializer
# Create your views here.


class SmallPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 50


class GroupRecommendViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = SmallPagination

    def list(self, request):
        return Response("input group number")

    def retrieve(self, request, pk=None):
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        restaurant_lists = []
        member_list = []
        queryset = Group.objects.get(id=pk) # 그룹 id를 params에서 받는다면 id=request.GET['id']

        recommend_restaurants = Restaurant.objects.filter(address__startswith=request.GET['address']).order_by('-score')[:5]

        for single_recommendation in recommend_restaurants:
            restaurant_lists.append(GroupRecommendRestaurantSerializer(single_recommendation).data)

        long = request.GET['long']
        lat = request.GET['lat']
        address = request.GET['address']

        # 추천 서버로 그룹 구성원의 정보를 보내기 위한 과정
        member_list.append(GroupSerializer(queryset).data['master']['id'])  # 그룹장 추가
        for single_member in GroupSerializer(queryset).data['members']:     # 그룹원들 추가
            member_list.append(single_member['id'])

        # 요청하는 사용자가 해당 id값을 가진 그룹에 속해있지 않은 경우 오류를 반환
        if request.user.id not in member_list:
            return Response("wrong")

        # 유저의 위치와 그룹 내 모든 구성원의 id를 추천 서버로 보내는 과정
        requests_list = [
            {
                "address": request.GET["address"],
                "group_members": member_list

            }
        ]

        # recommended_server_URL = "http://127.0.0.1:8081/teamfeed/"  # 주소 변경 부탁드립니다!
        recommended_server_URL = "https://j4b203.p.ssafy.io:7788/teamfeed/"  # 주소 변경 부탁드립니다!
        ret = requests.post(recommended_server_URL, data=json.dumps(requests_list), headers=headers)

        # 추천 서버로부터 데이터 수신
        state = True
        while state:
            try:
                recomm_stores = json.loads(ret.text)    
            except:       
                ret = requests.post(recommended_server_URL, data=json.dumps(requests_list), headers=headers)
            else:
                break     
        
        aaa = recomm_stores['group_feed']['data'][1:]
        for single_store in aaa:
            if single_store['address'][:2] == "대전":
                target_store = Restaurant.objects.get(id=single_store['id'])
                target_store.image = 'https://yogomogo.com/static/'+str(single_store['id'])+'/1.jpg'
                target_store.save()

        # pagination
        page = self.paginate_queryset(recomm_stores['group_feed']['data'][1:])
        if page is not None:
            for single_store in page:
                if single_store['address'][:2] == "대전":
                    target_store = Restaurant.objects.get(id=single_store['id'])
                    target_store.image = 'https://yogomogo.com/static/'+str(single_store['id'])+'/1.jpg'
                    target_store.save()
                    single_store['image'] = target_store.image

        serializer = RestaurantInfoSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

        
class GroupReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = GroupReviewSerializer
    pagination_class = SmallPagination

    def retrieve(self, request, pk=None):
        '''
        특정 그룹이 작성한 리뷰들을 불러옵니다.
        '''
        if request.GET['ord'] == 'asc':
            queryset = Review.objects.filter(group=pk).order_by('created_at')
        elif request.GET['ord'] == 'desc':
            queryset = Review.objects.filter(group=pk).order_by('-created_at')

        # pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = GroupReviewSerializer(queryset, many=True)
        return Response(serializer.data)


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

    def destroy(self, request, pk=None):
        '''
        ## 그룹 삭제
        ### 토큰을 통해서 그룹의 주인을 인증하고, pk를 통해서 그룹의 번호에 접근한다.
        '''
        data = request.data
        group = get_object_or_404(Group, master=request.user, id=pk)
        group.delete()
        return Response({"response":"Successfully deleted"})    


class GroupRedundancyCheckAPI(generics.RetrieveAPIView):
    serializer_class=GroupSerializer
    def get(self, request):
        '''
        ## group name 중복 확인
        '''
        user = request.user
        group_name = request.GET['name']
        redundancy = False
        if Group.objects.filter(master=user, name=group_name).exists():
            redundancy = True
        return Response ({"redundancy": redundancy})
