from django.db import models
from django.contrib.auth.models import User




class SeasonsGroups(models.Model): #eg. "Mr. Robot"
    title = models.CharField(max_length=150)


class Seasons(models.Model): #eg. "Season 1"
    title = models.CharField(max_length=100)
    group =  models.ForeignKey(SeasonsGroups, on_delete=models.CASCADE, db_column="group", null=True)


class Movies(models.Model): #in series just an eposode
    movie_id = models.IntegerField(primary_key=True) # the name can be different
    title = models.CharField(max_length=100)
    genres = models.CharField(max_length=100)
    year = models.IntegerField(null=True)
    img_url = models.CharField(max_length=500 ,null=True)
    rating_avg = models.DecimalField(default=0,null=True, max_digits=3, decimal_places=2)
    rating_amount = models.IntegerField(default=0,null=True)
    season =  models.ForeignKey(Seasons, on_delete=models.CASCADE, db_column="season", null=True)

class Links(models.Model):
    movie_id = models.ForeignKey(Movies, on_delete=models.CASCADE)
    imdb_id = models.IntegerField()
    tmdb_id = models.IntegerField(null=True)

    
class VideoLinks(models.Model):
    movie_id = models.ForeignKey(Movies, on_delete=models.CASCADE)
    vid_link = models.CharField(max_length=500)


class Ratings(models.Model):
    user_id = models.IntegerField()
    external_origin = models.BooleanField(default=True)
    movie_id = models.ForeignKey(Movies, on_delete=models.CASCADE)
    RATINGS = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')]
    rating = models.CharField(max_length=1, choices=RATINGS)
    timestamp = models.IntegerField()


class Tags(models.Model):
    user_id = models.IntegerField()
    movie_id = models.ForeignKey(Movies, on_delete=models.CASCADE)
    tag = models.CharField(max_length=100)
    timestamp = models.IntegerField()



