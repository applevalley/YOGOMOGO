from rest_framework import serializers
from .models import ImagePost


class ImagePostSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    
    class Meta:
        model = ImagePost
        fields = ('image',)
