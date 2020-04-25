#!/usr/bin/env python
# coding: utf-8



import os
import time
import gc
import argparse
from fuzzywuzzy import fuzz

# data science imports
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

def _prep_data():
        """
        prepare data for recommender
        1. movie-user scipy sparse matrix
        2. hashmap of movie to row index in movie-user scipy sparse matrix
        """
        # read data
        df_movies = pd.read_csv(
            r"ml-latest-small/movies.csv",
            usecols=['movieId', 'title'],
            dtype={'movieId': 'int32', 'title': 'str'})
        df_ratings = pd.read_csv(
            r"ml-latest-small/ratings.csv",
            usecols=['userId', 'movieId', 'rating'],
            dtype={'userId': 'int32', 'movieId': 'int32', 'rating': 'float32'})
        # filter data
        df_movies_cnt = pd.DataFrame(
            df_ratings.groupby('movieId').size(),
            columns=['count'])
        popular_movies = list(set(df_movies_cnt.query('count >= 0').index))  # noqa
        movies_filter = df_ratings.movieId.isin(popular_movies).values

        df_users_cnt = pd.DataFrame(
            df_ratings.groupby('userId').size(),
            columns=['count'])
        active_users = list(set(df_users_cnt.query('count >= 0').index))  # noqa
        users_filter = df_ratings.userId.isin(active_users).values

        df_ratings_filtered = df_ratings[movies_filter & users_filter]

        # pivot and create movie-user matrix
        movie_user_mat = df_ratings_filtered.pivot(
            index='movieId', columns='userId', values='rating').fillna(0)
        # create mapper from movie title to index
        hashmap = {
            movie: i for i, movie in
            enumerate(list(df_movies.set_index('movieId').loc[movie_user_mat.index].title)) # noqa
        }
        # transform matrix to scipy sparse matrix
        movie_user_mat_sparse = csr_matrix(movie_user_mat.values)

        # clean up
        del df_movies, df_movies_cnt, df_users_cnt
        del df_ratings, df_ratings_filtered, movie_user_mat
        gc.collect()
        return movie_user_mat_sparse, hashmap




def make_recommendations(fav_movie, n_recommendations):
    """
    make top n movie recommendations
    Parameters
    ----------
    fav_movie: str, name of user input movie
    n_recommendations: int, top n recommendations
    """
    # get data
    movie_user_mat_sparse, hashmap = _prep_data()
        
    model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
    
    # get recommendations
    raw_recommends = _inference(
        model_knn, movie_user_mat_sparse, hashmap,
        fav_movie, n_recommendations)
    # print results
    reverse_hashmap = {v: k for k, v in hashmap.items()}
    print('Recommendations for {}:'.format(fav_movie))
    for i, (idx, dist) in enumerate(raw_recommends):
        print('{0}: {1}, with distance '
                'of {2}'.format(i+1, reverse_hashmap[idx], dist))



def _inference(model, data, hashmap,
                   fav_movie, n_recommendations):
       
        # fit
        model.fit(data)
        # get input movie index
        print('You have input movie:', fav_movie)
        idx = _fuzzy_matching(hashmap, fav_movie)
        # inference
        print('Recommendation system start to make inference')
        print('......\n')
        t0 = time.time()
        distances, indices = model.kneighbors(
            data[idx],
            n_neighbors=n_recommendations+1)
        # get list of raw idx of recommendations
        raw_recommends =             sorted(
                list(
                    zip(
                        indices.squeeze().tolist(),
                        distances.squeeze().tolist()
                    )
                ),
                key=lambda x: x[1]
            )[:0:-1]
        print('It took my system {:.2f}s to make inference \n              '.format(time.time() - t0))
        # return recommendation (movieId, distance)
        return raw_recommends




def _fuzzy_matching(hashmap, fav_movie):
        """
        return the closest match via fuzzy ratio.
        If no match found, return None
        Parameters
        ----------
        hashmap: dict, map movie title name to index of the movie in data
        fav_movie: str, name of user input movie
        Return
        ------
        index of the closest match
        """
        match_tuple = []
        # get match
        for title, idx in hashmap.items():
            ratio = fuzz.ratio(title.lower(), fav_movie.lower())
            if ratio >= 60:
                match_tuple.append((title, idx, ratio))
        # sort
        match_tuple = sorted(match_tuple, key=lambda x: x[2])[::-1]
        if not match_tuple:
            print('Oops! No match is found')
        else:
            print('Found possible matches in our database: '
                  '{0}\n'.format([x[0] for x in match_tuple]))
            return match_tuple[0][1]

make_recommendations("Iron man",10)





