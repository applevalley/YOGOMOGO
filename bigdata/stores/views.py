from django.shortcuts import render
from .models import Restaurant, Review
from .serializers import (
    WriterSerializer, 
    RestaurantSerializer, 
    ReviewSerializer,
    UserFeedSerializer
)

from accounts.models import User, Profile
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser

from django.shortcuts import get_object_or_404
from rest_framework import status, generics, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny


class SmallPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

class RestaurantViewSet(viewsets.ModelViewSet):
    '''
    ## 식당 목록 정보 반환
    '''
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    pagination_class = SmallPagination


class ReviewViewSet(viewsets.ViewSet):

    def list(self, request):
        '''
        ## 리뷰 목록 정보 반환
        '''
        queryset = Review.objects.filter(writer=request.user)
        serializer = ReviewSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        '''
        ## pk를 통해 개별 리뷰 조회하기
        '''
        review = get_object_or_404(Review, id=pk)
        review.viewed_num += 1
        review.save()
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    def create(self, request):
        '''
        ## 리뷰 생성 
        '''
        data = request.data
        theme_list = ['가족', '연인', '회식', '친구']
        reviewer = request.user
        print(reviewer)
        review_restaurant = get_object_or_404(Restaurant, pk=data['restaurant'])

        if data['theme'] not in theme_list:   # 카테고리(가족, 연인, 회식, 친구)에 해당되지 않는 테마를 입력한 경우
            return Response({"response": "wrong theme"})

        new_review = Review.objects.create(
            theme=data['theme'], title=data['title'], content=data['content'], score=data['score'], writer=reviewer, restaurant=review_restaurant
        )
        new_review.save()
        serializer = ReviewSerializer(new_review)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        '''
        ## pk를 통해 개별 리뷰 수정하기
        '''

        data = request.data
        theme_list = ['가족', '연인', '회식', '친구']

        if data['theme'] not in theme_list:   # 카테고리(가족, 연인, 회식, 친구)에 해당되지 않는 테마를 입력한 경우
            return Response({"response": "wrong theme"})
        
        review = get_object_or_404(Review, id=pk)
        if review.writer != request.user:
            return Response({"response": "access denied"})

        serializer = ReviewSerializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def destroy(self, request, pk=None):
        '''
        ## pk를 통해 개별 리뷰 삭제하기
        '''
        # data = request.data
        review = get_object_or_404(Review, id=pk)
        if review.writer != request.user:
            return Response({"response": "access denied"})
        review.delete()
        return Response({"response":"Successfully deleted"})    


class PopularFeedViewSet(viewsets.ViewSet):
    
    def list(self, request):
        queryset = Review.objects.all().order_by('-viewed_num')
        serializer = UserFeedSerializer(queryset, many=True)
        return Response(serializer.data)