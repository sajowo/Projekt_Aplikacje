from rest_framework import serializers
from .models import Links, Movies, Ratings,Tags,Seasons


class SeasonsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seasons
        queryset = Seasons.objects.all()
        fields = '__all__'


class MoviesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movies
        queryset = Movies.objects.all()
        #fields = ('movie_id', 'title', 'genres', 'year', 'rating_avg', 'rating_amount')
        fields = '__all__'



class LinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Links
        fields = '__all__'


class RatingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ratings
        fields = '__all__'


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'


class MoviesDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movies
        queryset = Movies.objects.all()
        exclude = ('id',)





