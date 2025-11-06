from django.contrib import admin
from .models import Links, Movies, Ratings,Tags,Seasons,SeasonsGroups


admin.site.register(Links)
admin.site.register(Movies)
admin.site.register(Ratings)
admin.site.register(Tags)
admin.site.register(SeasonsGroups)
admin.site.register(Seasons)
