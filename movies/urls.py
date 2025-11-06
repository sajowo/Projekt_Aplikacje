# urls.py 
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from .views import MoviesView, LinksView, TagsView, RatingsView, SeasonsViews

router = routers.DefaultRouter()

# Rejestracja ViewSetów
router.register('links', LinksView)
router.register('ratings', RatingsView)
router.register('seasons', SeasonsViews)

# Rejestrujemy nowe ViewSety, aby pojawiły się w API Root
router.register('movies', MoviesView)  # Używa 'movie_id' jako lookup_field
router.register('tags', TagsView)

# Rejestrujemy DBView; basename jest wymagane,
# ponieważ nie jest to ModelViewSet (nie ma queryset)
# router.register('db', viewsDB.DBView, basename='db')

urlpatterns = [
                  path('', include(router.urls)),

                  path('admin/', admin.site.urls),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
