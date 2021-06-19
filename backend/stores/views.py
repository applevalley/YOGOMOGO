import json
import requests
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Restaurant, Review, Images, Bookmark, UserRecommend, GroupRecommend, Menu
from .serializers import (
    WriterSerializer,
    RestaurantSerializer,
    ReviewSerializer,
    UserFeedSerializer,
    BestRestaurantSerializer,
    ReviewImageSerializer,
    ReviewBookmarkSerializer,
    ReviewThemeSerializer,
    UserRecommendSerializer,
    GroupRecommendSerializer,
    RestaurantDetailSerializer,
    RestaurantMenuSerializer
)

from accounts.models import User, Profile
from group.models import Group
from group.serializers import GroupSerializer
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404
from rest_framework import status, generics, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

import sqlite3
import pandas as pd
import shutil
from sklearn.metrics.pairwise import cosine_similarity
from math import sqrt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from matrix_factorization import BaselineModel, KernelMF, train_update_test_split


class SmallPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    # page_size_query_param = "page_size"
    max_page_size = 50


class RestaurantViewSet(viewsets.ModelViewSet):
    '''
    ## 식당 목록 정보 반환
    '''
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    pagination_class = SmallPagination

    def retrieve(self, request, pk=None):
        restaurant = get_object_or_404(Restaurant, id=pk)
        restaurant.image = 'https://yogomogo.com/static/img/'+str(pk)+'/1.jpg'
        restaurant.save()

        menus = Menu.objects.filter(store=pk)

        idx = 2
        for single_menu in menus:
            if idx < 5:
                single_menu.image = 'https://yogomogo.com/static/img/'+str(pk)+'/'+str(idx)+'.jpg'
            else:
                single_menu.image = ''

            if single_menu.price == "0.0":
                single_menu.price = '가격 정보 없음'

            idx += 1
            single_menu.save()
        
        serializer = RestaurantDetailSerializer(restaurant)
           
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = SmallPagination

    def list(self, request):
        '''
        ## 리뷰 목록 정보 반환
        '''
        queryset = Review.objects.filter(writer=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        bookmarked_reviews = Review.objects.filter(bookmarked=True)
        all_bookmark = Bookmark.objects.all()
        for single_bookmark in all_bookmark:
            target_review = Review.objects.get(id=single_bookmark.review)
            if single_bookmark.bookmark_user.id == request.user.id:
                target_review.bookmarked = True
            else:
                target_review.bookmarked = False
            target_review.save()

        serializer = ReviewSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        '''
        ## pk를 통해 개별 리뷰 조회하기
        '''

        review = get_object_or_404(Review, id=pk)
        review.viewed_num += 1
        review.save()

        # 해당 리뷰가 북마크된 경우, 북마크한 사용자가 자기 자신인지에 따라
        # bookmarked의 T/F 여부를 구분합니다.
        bookmark_for_review = Bookmark.objects.filter(review=pk)
        for single_bookmark in bookmark_for_review:
            if single_bookmark.bookmark_user.id != request.user.id:
                review.bookmarked = False
                review.save()
            else:
                review.bookmarked = True
                review.save()

        serializer = ReviewSerializer(review)

        group = Group.objects.get(pk=1)
        return Response(serializer.data)

    def create(self, request):
        '''
        ## 리뷰 생성 
        '''
        headers = {'Content-Type': 'application/json; charset=utf-8'}

        reviewer = request.user
        data = json.loads(request.body)
        image_list = []
        theme_list = ['가족', '연인', '회식', '친구']

        # 카테고리(가족, 연인, 회식, 친구)에 해당되지 않는 테마를 입력한 경우
        if data['theme'] not in theme_list:
            return Response({"response": "wrong theme"})

        if 'group' in data:
            visited_group = Group.objects.get(id=data['group'])

        target_restaurant = Restaurant.objects.get(id=data['restaurant_id'])

        # 리뷰 작성 시 작성자 정보, 리뷰의 대상인 식당, 평점이 추천 서버로 전달되는 과정
        # recommended_server_URL = "http://127.0.0.1:8081/reviewrun/"  # 주소 변경 부탁드립니다!
        recommended_server_URL = "https://j4b203.p.ssafy.io:7788/reviewrun/"  # 주소 변경 부탁드립니다!
        recommended_list = [
            {
                "user": reviewer.email,
                "store": data["restaurant_id"],
                "score": data["score"]
            }
        ]
        response = requests.post(recommended_server_URL, data=json.dumps(
            recommended_list), headers=headers)

        if data['tags']:
            data['tags'] = '|'.join(data['tags'])

        new_review = Review.objects.create(
            theme=data['theme'], title=data['title'], contents=data['contents'], score=data['score'], group=visited_group,
            tags=data['tags'], headcount=data['headcount'], writer=reviewer,
            restaurant_id=target_restaurant.id, restaurant_info=target_restaurant
        )

        if data['images']:
            review_images = data['images']
            for single_image in review_images:
                new_image = Images.objects.create(
                    review=new_review, image=single_image
                )

        # 리뷰가 달린 식당의 총 평점을 구하는 과정
        review_for_score = Review.objects.filter(
            restaurant_id=target_restaurant.id)
        score_agg = 0
        for single_score in review_for_score:
            score_agg += ReviewSerializer(single_score).data['score']
        target_restaurant.score = (score_agg / len(review_for_score))
        target_restaurant.save()

        return Response(ReviewSerializer(new_review).data)

    def update(self, request, pk=None):
        '''
        ## pk를 통해 개별 리뷰 수정하기
        '''

        data = json.loads(request.body)
        theme_list = ['가족', '연인', '회식', '친구']

        # 카테고리(가족, 연인, 회식, 친구)에 해당되지 않는 테마를 입력한 경우
        if data['theme'] not in theme_list:
            return Response({"response": "wrong theme"})

        review = get_object_or_404(Review, id=pk)

        if data['restaurant_id'] != review.restaurant_id:
            review.restaurant_id = data['restaurant_id']
            review.restaurant_info = Restaurant.objects.get(id=data['restaurant_id'])
        review.save()

        if review.writer != request.user:
            return Response({"response": "access denied"})

        if 'tags' in data:
            data['tags'] = '|'.join(data['tags'])

        if data['images']:
            Images.objects.filter(review=review).delete()
            review_images = data['images']
            for single_image in review_images:
                updated_image = Images.objects.create(
                    review=review, image=single_image
                )

        serializer = ReviewSerializer(review, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['tags'] = data['tags']
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        '''
        ## pk를 통해 개별 리뷰 삭제하기
        '''
        review = get_object_or_404(Review, id=pk)
        if review.writer != request.user:
            return Response({"response": "access denied"})
        review.delete()
        return Response({"response": "Successfully deleted"})


class BestRestaurantViewSet(viewsets.ViewSet):

    def create(self, request):
        '''
        인생맛집 입력하기
        '''
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        # recommended_server_URL = "http://127.0.0.1:8081/restaurant/"
        recommended_server_URL = "https://j4b203.p.ssafy.io:7788/restaurant/"
        writer = request.user
        client = User.objects.get(email=writer)
        restaurant_list = []
        restaurant_list.append({"user": client.email})

        for single_restaurant in request.data['restaurant_list']:
            target_restaurant = Restaurant.objects.get(id=single_restaurant)
            restaurant_list.append(
                BestRestaurantSerializer(target_restaurant).data)
        response = requests.post(recommended_server_URL, data=json.dumps(
            restaurant_list), headers=headers)
        return Response(restaurant_list)


class PopularFeedViewSet(viewsets.ViewSet):

    def list(self, request):
        '''
        전국 인기 피드
        '''
        queryset = Review.objects.all().order_by('-viewed_num')
        serializer = ReviewThemeSerializer(queryset, many=True)

        return Response(serializer.data)


class UserFeedViewSet(viewsets.ModelViewSet):

    queryset = Review.objects.all()
    serializer_class = ReviewThemeSerializer
    pagination_class = SmallPagination

    def list(self, request):
        '''
        사용자 맞춤 피드
        '''
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        permission_classes = [IsAuthenticated, ]

        # long = request.GET['long']
        # lat = request.GET['lat']
        address = request.GET['address']

        requests_list = [
            {
                "user_email": request.user.email,
                "address": request.GET['address']
            }
        ]

        # recommended_server_URL = "http://127.0.0.1:8081/feed/"  # 주소 변경 부탁드립니다!
        recommended_server_URL = "https://j4b203.p.ssafy.io:7788/feed/"  # 주소 변경 부탁드립니다!
        response = requests.post(recommended_server_URL, data=json.dumps(
            requests_list), headers=headers)
        review_list = []
        recomm_list = UserRecommend.objects.filter(
            recommend_user=request.user.id)

        for single_recomm in recomm_list:
            review_list.append(Restaurant.objects.get(
                id=UserRecommendSerializer(single_recomm).data['restaurant_id']))

        print(review_list)
        page = self.paginate_queryset(review_list)
        if page is not None:
            serializer = RestaurantSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ReviewThemeSerializer(review_list, many=True)
        return Response(serializer.data)


class ThemeFeedViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    pagination_class = SmallPagination
    serializer_class = ReviewThemeSerializer

    def list(self, request):
        '''
        테마별 피드
        '''
        if request.GET['theme'] not in ["연인", "친구", "가족", "회식"]:
            return Response("wrong")

        queryset = Review.objects.filter(theme=request.GET['theme'], restaurant_info__address__contains=request.GET['address'].split(
            ' ')[0], tags__contains=request.GET['tag'])

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_paginated_response(
                self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class SearchTagViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewThemeSerializer
    pagination_class = SmallPagination

    def list(self, request):
        '''
        태그 검색
        '''
        queryset = Review.objects.filter(tags__icontains=request.GET['search'])

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ReviewThemeSerializer(queryset, many=True)
        return Response(serializer.data)


class BookmarkViewSet(viewsets.ModelViewSet):
    queryset = Bookmark.objects.all()
    permission_classes = [IsAuthenticated, ]
    serializer_class = ReviewBookmarkSerializer
    pagination_class = SmallPagination

    def list(self, request):
        '''
        북마크된 리뷰들 불러오기
        '''
        if request.GET['ord'] == 'asc':    # 시간 순으로 정렬
            queryset = Bookmark.objects.filter(
                bookmark_user=request.user).order_by('created_at')
        elif request.GET['ord'] == 'desc':
            queryset = Bookmark.objects.filter(
                bookmark_user=request.user).order_by('-created_at')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ReviewBookmarkSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, pk=None):
        '''
        북마크하기
        '''
        
        target_review = get_object_or_404(Review, id=pk)

        bookmark_for_user = Bookmark.objects.filter(
            review=target_review, bookmark_user=request.user)

        if bookmark_for_user.exists():
            bookmark_for_user.delete()
            target_review.bookmarked = False
            target_review.save()
            return Response("Successfully deleted")
        else:
            Bookmark.objects.create(
                review=target_review, bookmark_user=request.user)
            target_review.bookmarked = True
            target_review.save()
            return Response("bookmark success")


class MonthlyReviewViewSet(viewsets.ViewSet):
    '''
    한 달간 리뷰 횟수 확인하기
    '''
    def create(self, request):
        end = datetime.now() - relativedelta(months=1)
        start = datetime.now()
        user_reviews = Review.objects.filter(
            writer=request.user, created_at__gte=end, created_at__lte=start).count()
        return Response(user_reviews)


@method_decorator(csrf_exempt, name='dispatch')
class FeedingViewSet(viewsets.ViewSet):
    def create(self, request):
        five = request.data

        if type(five[0]) == str:
            user = User.objects.get(email=five[0])
            old_recommendation = UserRecommend.objects.filter(
                recommend_user=user)
            old_recommendation.delete()
            for single_recommend in five[1:]:
                UserRecommend.objects.create(
                    recommend_user=user, restaurant_id=single_recommend['id'], restaurant_name=single_recommend['store_name'], restaurant_address=single_recommend['address'])

        if type(five[0]) == list:
            user = User.objects.get(id=five[0][0])
            another_user = five[0][1:]
            another_user_list = []
            user_group = Group.objects.filter(master=user)
            for single_group in user_group:
                for single_member in GroupSerializer(single_group).data['members']:
                    another_user_list.append(single_member['id'])
                if sorted(another_user) == sorted(another_user_list):
                    user_group = single_group
                    break
                else:
                    another_user_list = []

            old_recommendation = GroupRecommend.objects.filter(
                recommend_group=user_group)
            old_recommendation.delete()

            for single_recommend in five[1:]:
                GroupRecommend.objects.create(recommend_group=user_group, restaurant_id=single_recommend[
                                              'id'], restaurant_name=single_recommend['store_name'], restaurant_address=single_recommend['address'])
        return Response(five)


global reviews
global stores
global item_based
global store_review


class startViewSet(viewsets.ViewSet):

    def list(self, request):

        global reviews
        global stores
        global item_based
        global store_review

        # DB와 데이터를 pandas DataFrame으로 변환
        con = sqlite3.connect("db.sqlite3")
        cur = con.cursor()
        query = cur.execute("SELECT * From stores_review")
        cols = [column[0] for column in query.description]
        reviews = pd.DataFrame.from_records(
            data=query.fetchall(), columns=cols)
        query2 = cur.execute("SELECT * From stores_restaurant")
        cols2 = [column[0] for column in query2.description]
        stores = pd.DataFrame.from_records(
            data=query2.fetchall(), columns=cols2)
        con.close()

        store_review = pd.merge(
            stores, reviews, left_on='id', right_on='restaurant_info_id')
        store_review_rating = store_review.pivot_table(
            'score_y', index='writer_id', columns="store_name")
        store_review_rating.fillna(0, inplace=True)
        item_based = cosine_similarity(store_review_rating)
        item_based = pd.DataFrame(
            data=item_based, index=store_review_rating.index, columns=store_review_rating.index)
        return Response("True1")


class UserFeedReViewSet(viewsets.ModelViewSet):

    def list(self, request):

        global reviews
        global stores
        global item_based
        global store_review

        userinfo = request.user.pk
        check = list(item_based.index)
        # 학습이 되지 않은 유저의 경우 같은 지역의 피드를 보여줍니다
        if check.count(userinfo) == 0:
            result = []
            result2 = []
            # 사용자 지역으로 한정
            location = request.GET['address']
            location = location[0:2]
            store_review = store_review[store_review['address'].str.startswith(
                location)]
            # 조회수 순으로 정렬
            store_review = store_review.sort_values(
                by='viewed_num', ascending=False)
            for i in store_review['id_y']:
                result.append(i)
            for i in result:
                result2.append(Review.objects.get(id=i))
            serializer = ReviewSerializer(
                result2, many=True)
            return Response(serializer.data)

        # 학습이 된 유저의 경우 리뷰 추천 결과를 보여줍니다 (최대 20개)
        else:
            # 유사도가 높은 5명의 유저 저장
            result = item_based[userinfo].sort_values(ascending=False)[
                1: 6]
            result = list(result.index)
            reco = []
            result2 = []
            for i in result:
                info = reviews[reviews['writer_id'] == i]
                info = info[info['contents'] != '']
                info = info.sort_values(by='score', ascending=False)
                # 각 유저 리뷰 4개의 정보를 저장
                info = info[0: 4]
                reinfo = list(info['id'])
                for k in reinfo:
                    reco.append(k)
            for i in reco:
                result2.append(Review.objects.get(id=i))
            serializer = ReviewSerializer(result2, many=True)
            return Response(serializer.data)
