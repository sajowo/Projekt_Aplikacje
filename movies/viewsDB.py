import csv
import os
import re
import shutil
import zipfile
from multiprocessing.dummy import Pool as ThreadPool

import requests
from django.db import connections
from django.db.models import Avg
from imdb import IMDb
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView

from .models import Links, Movies, Ratings, Tags


class DBView(APIView):
    def norm(self, name):
        norm_name = ""
        for letter in name:
            if letter.isupper():
                norm_name += "_"
            norm_name += letter.lower()
        return norm_name

    def year_from_title(self, title):
        year = None
        pattern = re.compile("[(][0-9][0-9][0-9][0-9][)]")
        pattern_only_num = re.compile("[0-9][0-9][0-9][0-9]")
        if title and pattern.search(title):
            print(pattern.search(title).string)
            try:
                year_str = pattern_only_num.search((pattern.search(title).group(0)))
                year = int(year_str.group(0))
            except:
                print("Pattern (yyyy) found, but yyyy not")
        return year

    def unzip_db(self):
        # Delete old files, unpack zip
        path_unzip = "media/unzip"
        path = "media/ml-latest-small.zip"
        if os.path.exists(path_unzip):
            shutil.rmtree(path_unzip)
        os.mkdir(path_unzip)
        print("Dir prepared")
        zip_ref = zipfile.ZipFile(path, 'r')
        zip_ref.extractall(path_unzip)
        zip_ref.close()
        print("DB unzipped")

    def download_db(self):
        # Download and replace ml-latest-small.zip if file already exists
        url = "http://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
        path = "media/ml-latest-small.zip"
        chunk = 2048
        req = requests.get(url, stream=True)
        if req.status_code == 200:
            with open(path + "new", 'wb') as f:
                for chunk in req.iter_content(chunk):
                    f.write(chunk)
                f.close()
        if os.path.exists(path + "new"):
            if os.path.exists(path):
                os.remove(path)
                print("Old zip removed")
            os.rename(path + "new", path)
        print("DB downloaded")

    def load_movies(self, conn):
        entity_name = "movies_movies"
        path_csv = "media/unzip/ml-latest-small/movies.csv"
        print("Now deleting:", entity_name)
        self.delete_entity(entity_name, conn)
        print("Now intesring:", entity_name)
        with open(path_csv, encoding="utf8") as csv_file:
            csv_file.seek(0)
            csv_reader = csv.reader(csv_file, delimiter=',')
            header = next(csv_reader)
            for row in csv_reader:
                print(row)
                new_movie = Movies()
                new_movie.movie_id = int(row[0])
                new_movie.title = row[1]
                new_movie.genres = row[2]
                new_movie.year = self.year_from_title(row[1])
                print(new_movie)
                new_movie.save()

    def load_links(self, conn):
        entity_name = "movies_links"
        path_csv = "media/unzip/ml-latest-small/links.csv"
        print("Now deleting:", entity_name)
        self.delete_entity(entity_name, conn)
        with open(path_csv, encoding="utf8") as csv_file:
            csv_file.seek(0)
            csv_reader = csv.reader(csv_file, delimiter=',')
            header = next(csv_reader)
            for row in csv_reader:
                print(row[0], row[1], row[2])
                new_link = Links()
                new_link.movie_id = Movies.objects.get(movie_id=int(row[0]))
                new_link.imdb_id = row[1]
                if not row[2]:
                    row[2] = None
                new_link.tmdb_id = row[2]
                new_link.save()

    def load_tags(self, conn):
        entity_name = "movies_tags"
        path_csv = "media/unzip/ml-latest-small/tags.csv"
        print("Now deleting:", entity_name)
        try:
            self.delete_entity(entity_name, conn)
        except:
            print("not delted")
        with open(path_csv, encoding="utf8") as csv_file:
            csv_file.seek(0)
            csv_reader = csv.reader(csv_file, delimiter=',')
            header = next(csv_reader)
            for row in csv_reader:
                print(row[0], row[1], row[2], row[3])
                new_tag = Tags()
                new_tag.user_id = row[0]
                print("(row):", row)
                print("id", str(row[1]))
                new_tag.movie_id = Movies.objects.get(movie_id=int(row[1]))
                print("yeas")
                new_tag.tag = row[2]
                new_tag.timestamp = row[3]
                print(new_tag.tag)
                new_tag.save()

    def load_ratings(self, conn):
        entity_name = "movies_ratings"
        path_csv = "media/unzip/ml-latest-small/ratings.csv"
        print("Now deleting:", entity_name)
        self.delete_entity(entity_name, conn)
        with open(path_csv, encoding="utf8") as csv_file:
            csv_file.seek(0)
            csv_reader = csv.reader(csv_file, delimiter=',')
            header = next(csv_reader)
            for row in csv_reader:
                print(row[0], row[1], row[2], row[3])
                new_tag = Ratings()
                new_tag.user_id = row[0]
                new_tag.movie_id = Movies.objects.get(movie_id=int(row[1]))
                new_tag.rating = row[2]
                new_tag.timestamp = row[3]
                new_tag.save()

    def post(self, request, format=None):
        try:
            json_valided = json.loads(request.body)
        except:
            return Response({"Status": "json not valid"})

        if request.body and json_valided == {"source": "ml-latest-small"}:
            status = "Status init"
            try:
                conn = connections['default']
                # self.download_db()
                # self.unzip_db()
                # self.load_movies(conn)
                # self.load_links(conn)
                self.load_tags(conn)
                self.load_ratings(conn)
                status = "OK"
            except Exception as e:
                print(e)
                print("Unable to reload DB")
                status = "Fail"
        elif request.body and json_valided == {"reset": "rating"}:
            status = self.add_ratings2movies()
            # status = "Ratings reseted"
        elif request.body and json_valided == {"reset": "cover"}:
            status = self.add_covers2movies()
        else:
            status = "Wrong request"
        return Response({"Status": status})

    def add_ratings2movies(self):
        movies = Movies.objects.all()
        iter = 1
        movies_len = len(movies)
        for movie in movies:
            iter += 1
            try:
                ratings = Ratings.objects.filter(movie_id=movie.movie_id)
                movie.rating_avg = list(ratings.aggregate(Avg('rating')).values())[0]
                movie.rating_amount = len(ratings)
                movie.save()
            except Exception as e:
                movie.rating_avg = float(0.0)
                movie.rating_amount = 0
                movie.save()
                return str(e) + str(list(ratings.aggregate(Avg('rating')).values())[0]["dict_values"])
            print(str(iter), "/", str(movies_len))
        return "ok"

    def add_cover(self, movie):
        try:
            ia = IMDb()
            movie_link = Links.objects.get(movie_id=movie)
            matreix_imdb = ia.get_movie(movie_link.imdb_id)
            movie.img_url = str(matreix_imdb['cover url'])
            movie.save()
            print(movie.movie_id)
        except Exception as e:
            print(str(e))

    def add_covers2movies(self):
        movies = Movies.objects.all()
        movies_len = len(movies)
        iter = 1
        pool = ThreadPool(16)
        pool.map(self.add_cover, movies)

    def delete_entity(self, entity_name, conn):
        conn.cursor().execute("PRAGMA foreign_keys = OFF;")
        conn.cursor().execute("delete from " + entity_name)
        conn.cursor().execute("PRAGMA foreign_keys = ON;")
