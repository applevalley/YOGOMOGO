from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser

from .models import ImagePost
from .serializers import ImagePostSerializer
# Create your views here.


class ImagePostViewSet(viewsets.ModelViewSet):
    '''
    사진을 전송받으면 해당 사진을 서버에 저장하고, 해당 이미지의 URL을 돌려줍니다.
    해당 URL을 클릭하면 이미지를 확인할 수 있습니다.
    '''
    queryset = ImagePost.objects.all()
    serializer_class = ImagePostSerializer
    parser_classes = [MultiPartParser, FormParser] 