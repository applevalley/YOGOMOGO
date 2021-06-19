from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import renderer_classes, api_view
from rest_framework.renderers import JSONRenderer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import sqlite3
import pandas as pd
import shutil
from sklearn.metrics.pairwise import cosine_similarity
from math import sqrt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from matrix_factorization import BaselineModel, KernelMF, train_update_test_split
from stores.models import Restaurant, Review ,Restaurant2
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser
from django.views import View
from django.shortcuts import get_object_or_404
from rest_framework import status, generics, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import (
    BestRestaurantSerializer,
)
import json
import requests
import random
from django.http.response import JsonResponse, HttpResponse

global reviews
global stores
global stores2
global pred
global matrix_fact
global X_train

class startViewSet(viewsets.ViewSet):
    
    def list(self, request):
        
        global reviews
        global stores
        global stores2
        global pred
        global matrix_fact
        global X_train

        # DB와 데이터를 pandas DataFrame으로 변환
        con = sqlite3.connect("db.sqlite3")
        cur = con.cursor()
        query = cur.execute("SELECT * From stores_review")
        cols = [column[0] for column in query.description]
        reviews = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
        query2 = cur.execute("SELECT * From stores_restaurant")
        cols2 = [column[0] for column in query2.description]
        stores = pd.DataFrame.from_records(data=query2.fetchall(), columns=cols2)
        query3 = cur.execute("SELECT * From stores_restaurant2")
        cols3 = [column[0] for column in query3.description]
        stores2 = pd.DataFrame.from_records(data=query3.fetchall(), columns=cols3)
        con.close()

        # 유저 기반 학습
        ratings_df = reviews[['store', 'user', 'score']].copy()
        ratings_df = ratings_df.rename(columns = {"store":"item_id","user":"user_id","score":"rating"})
        ratings_df = ratings_df[['user_id','item_id','rating']]
        X_train, X_test, y_train, y_test = train_test_split(ratings_df[['user_id','item_id']],ratings_df[['rating']], test_size=0.2, random_state=1234)
        matrix_fact = KernelMF(n_epochs=20, n_factors=100, verbose=1, lr=0.001, reg=0.005)
        matrix_fact.fit(X_train, y_train)
        pred = matrix_fact.predict(X_test)
        return Response("True!!!!!!!")


@method_decorator(csrf_exempt, name='dispatch')
class restaurantViewSet(viewsets.ViewSet):
    
    def create(self, request):
        five = request.data
        for i in range(1, 6):
            reviews = Review(user = five[0].get('user'), score = 5, store = five[i].get('id') )    
            reviews.save()    
        return Response("True!!!!!!!")


@method_decorator(csrf_exempt, name='dispatch')
class reviewrunViewSet(viewsets.ViewSet):
    
    def create(self, request):
        userinfo = request.data
        reviews = Review(user = userinfo[0].get('user'), score =userinfo[0].get('score'), store = userinfo[0].get('store') )    
        reviews.save()
        return Response("True!!!!!!!")


@method_decorator(csrf_exempt, name='dispatch')
class feedViewSet(viewsets.ViewSet):
    
    def create(self, request):
        global reviews
        global stores
        global stores2
        global pred
        global matrix_fact
        global X_train

        userinfo = request.data
        username = userinfo[0].get('user_email')
        review = Review.objects.filter(user=username)
        location = userinfo[0].get('address')
        location = location[0:2]
        re = list(review.values('store'))
        store2 = []
        reco2 = [] 
        reco3 = []
        
        '''
        *** 아이템 기반 협업 필터링을 이용한 음식점 추천(개인) ***
        *** 아이템 기반 추천은 연산량이 많아 메모리 부족으로 AWS에서 사용 할 수 없습니다 ***

        if len(re) < 6: # 유저의 리뷰 갯수가 일정 개수 이하면 아이템 기반 추천을 합니다.
            for i in range(0, 5):
                store = Restaurant.objects.filter(id=re[i].get('store'))
                st = list(store.values('store_name'))
                store2.append(st[0].get('store_name'))

                for i in range(0, 5):
                    store = Restaurant.objects.filter(id=re[i].get('store'))
                    st = list(store.values('store_name'))
                    store2.append(st[0].get('store_name'))

                for i in range(0,5):
                    recommend=item_based[store2[i]].sort_values(ascending=False)[1:500]
                    recommend_store = pd.merge(recommend, stores, on='store_name')
                    addr=recommend_store[recommend_store['address'].str.startswith(location)]
                    b = addr.drop_duplicates("store_name", keep='first')
                    b = b[0:4]
                    reco2.append(b)

            final = pd.concat([reco2[0], reco2[1], reco2[2], reco2[3], reco2[4]])
            final = final.drop_duplicates("store_name", keep='first')
            reco = list(final['id'])
            
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            recommended_server_URL = "https://yogomogo.com/api/feeding/"   # 수신 서버의 URL // 실제로 사용할 URL로 교체가 필요합니다
            restaurant_list = []
        
            restaurant_list.append(username)

            for single_restaurant in reco:
                target_restaurant = Restaurant.objects.get(id=single_restaurant)
                restaurant_list.append(BestRestaurantSerializer(target_restaurant).data)
            # 수신 서버로 requests를 보내고, 돌려받은 return의 Response를 response에 담음
            response = requests.post(recommended_server_URL, data=json.dumps(restaurant_list), headers=headers)
        '''

        if len(re) >= 0: #유저 기반 추천 알고리즘이 동작 합니다.
            user = username
            # 식신 데이터 추천    
            recommend_store2 = stores2[stores2['address'].str.startswith(location)]
            reco = list(recommend_store2['id'])
            choice = random.sample(reco, 3)
            restaurant_list = []
            restaurant_list.append(username)
            for single_restaurant in choice:
                target_restaurant = Restaurant2.objects.get(id=single_restaurant)
                restaurant_list.append(BestRestaurantSerializer(target_restaurant).data)

            #유저 기반 추천
            items_known = X_train.query("user_id == @user")["item_id"]
            result_df = matrix_fact.recommend(user=user, items_known=items_known, amount=5000)
            ids = result_df['item_id'].to_list()
            recommend_store = stores[stores['id'].isin(ids)]
            recommend_store = recommend_store[recommend_store['address'].str.startswith(location)]
            recommend_store = recommend_store.drop_duplicates("store_name", keep='first')
            recommend_store = recommend_store[:15]
            reco=list(recommend_store['id']) 
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            # recommended_server_URL = "http://127.0.0.1:8000/api/feeding/"   # 수신 서버의 URL // 실제로 사용할 URL로 교체가 필요합니다
            recommended_server_URL = "https://yogomogo.com/api/feeding/"   # 수신 서버의 URL // 실제로 사용할 URL로 교체가 필요합니다

            for single_restaurant in reco:
                target_restaurant = Restaurant.objects.get(id=single_restaurant)
                restaurant_list.append(BestRestaurantSerializer(target_restaurant).data)
            # 수신 서버로 requests를 보내고, 돌려받은 return의 Response를 response에 담음
            response = requests.post(recommended_server_URL, data=json.dumps(restaurant_list), headers=headers)
        return Response(restaurant_list)


@method_decorator(csrf_exempt, name='dispatch')
class teamfeedViewSet(viewsets.ViewSet):
    
    def create(self, request):
        global reviews
        global stores
        global stores2
        global pred
        global matrix_fact
        global X_train

        userinfo = request.data
        user_list = userinfo[0].get('group_members')
        location = userinfo[0].get('address')
        
        # user_list = ['774323', 'abc@naver.com', '249051']
        reco = []
        restaurant_list = []
        restaurant_list.append(user_list)

        # 식신 데이터 추천    
        recommend_store2 = stores2[stores2['address'].str.startswith(location)]
        reco2 = list(recommend_store2['id'])
        choice = random.sample(reco2, 3)
        for single_restaurant in choice:
            target_restaurant = Restaurant2.objects.get(id=single_restaurant)
            restaurant_list.append(BestRestaurantSerializer(target_restaurant).data)

        # 유저 기반  추천    
        for user in user_list:     
            items_known = X_train.query("user_id == @user")["item_id"]
            result_df = matrix_fact.recommend(user=user, items_known=items_known, amount=5000)
            ids = result_df['item_id'].to_list()
            recommend_store = stores[stores['id'].isin(ids)]
            recommend_store = recommend_store[recommend_store['address'].str.startswith(location)]
            recommend_store = recommend_store.drop_duplicates("store_name", keep='first')
            recommend_store = recommend_store[:7]
            result = list(recommend_store['id'])  
            for i in result:
                reco.append(i)

        my_set = set(reco)
        reco = list(my_set)
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        # recommended_server_URL = "http://127.0.0.1:8000/api/feeding/"   # 수신 서버의 URL // 실제로 사용할 URL로 교체가 필요합니다
        recommended_server_URL = "https://yogomogo.com/api/feeding/"   # 수신 서버의 URL // 실제로 사용할 URL로 교체가 필요합니다

        for single_restaurant in reco:
            target_restaurant = Restaurant.objects.get(id=single_restaurant)
            restaurant_list.append(BestRestaurantSerializer(target_restaurant).data)

        result_restaurant_list = {'data': restaurant_list}
        
        # 수신 서버로 requests를 보내고, 돌려받은 return의 Response를 response에 담음
        response = requests.post(recommended_server_URL, data=json.dumps(restaurant_list), headers=headers)      
        return HttpResponse(json.dumps({'group_feed': result_restaurant_list}),
                    content_type='application/json; charset=utf8')

