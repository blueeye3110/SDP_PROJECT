import numpy as np 
import pandas as pd
from operator import itemgetter
import csv
from csv import writer
from sklearn.metrics.pairwise import cosine_similarity as sim
from requests import get
from bs4 import BeautifulSoup


import os
import time
import gc
import argparse
from fuzzywuzzy import fuzz

# data science imports
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors


#sort data by perticuer user rating
def sortdata(df,gener,user):
    user=int(user)
    narray=df.to_numpy()                                        #convert dataframe into numpy array
    array=np.asarray(gener)                                     #convert genre list into array
    array=np.vstack((array,narray))                             #appenf genre list as 1st row in array for sort data with their genre
    array=array.transpose()                                     #transpose array to sort row wise            
    array=array[array[:,user].argsort()[::-1]]                  #sort array in decending order    
    array=array.transpose()                                     #transpose again to get same data        
    return array
    
## ----- similar movie data using similar user -----

#Function to get the average genre ratings for each of genres
def similarUser(rating, movie, genre, column,index,userID,gener,user):
    genre_ratings = pd.DataFrame()                                                                    #dataframe for genre avg rating              
    similar_User=[]        
    userRating=rating[rating['userId']==int(userID)]
    m=[]                                                                           #lisr for movie similar userId and genrelist      
    for g in genre:        
        l=[]
        l.append(g)
        mgroup = movie[movie['genres'].str.contains(g)]                                               #grp same genre movie  
        avgRating = rating[rating['movieId'].isin(mgroup['movieId'])].loc[:, ['userId', 'rating']].groupby(['userId'])['rating'].mean().round(2)     #find avg rating for genres by each user
        genre_ratings = pd.concat([genre_ratings, avgRating], axis=1)                                 #concat genre with user          
        totelRating=len(userRating[userRating['movieId'].isin(mgroup['movieId'])])
        l.append(totelRating)
        totelAvgRating=userRating[userRating['movieId'].isin(mgroup['movieId'])]
        totelAvgRating=totelAvgRating["rating"].mean()
        l.append(totelAvgRating)
        m.append(l)
    m=sorted(m,key=itemgetter(1),reverse=True)                  #sort array in decending order    
    genre_ratings.columns = column                                                                    #add column name      
    genre_ratings=genre_ratings.fillna(0)   
    genre_ratings=sortdata(genre_ratings,gener,userID)                                                #sort data to get most four rated genre                  
    Genres_list=list(genre_ratings[0:1,:4].ravel() )
    Genres_list_most_view=[]
    for i in range(4):
        Genres_list_most_view.append(m[i][0])
    genre_ratings=pd.DataFrame(genre_ratings[1:,:4],columns=genre_ratings[0:1,:4].ravel())            #convert sorted array in dataframe  
    genre_ratings=sim(genre_ratings)                                                                  #find cosine similarity      
    genre_ratings=pd.DataFrame(genre_ratings,columns=user)                                            #convert into dataframe  
    genre_ratings=sortdata(genre_ratings,user,userID)                                                 #sort user with similarity in descending order   
    genre_ratings=pd.DataFrame(genre_ratings[1:,:],columns=genre_ratings[0:1,:].ravel())              #convert into dataframe  
    genre_ratings=genre_ratings.loc[userID:userID,:]                                                  #similar user row for given user  
    similar_User.append(genre_ratings.columns.values.tolist())                                              #append similar user id into list  
    similar_User.append(Genres_list)
    similar_User.append(Genres_list_most_view)                                                                  #append genre list into list      
    return similar_User



                

def similarMovieList(rating,movie,movieID,genre,column,userID):
    recomendedMovieData=[]                                                                              #List for similar movie id 
    for g in genre:
        movie_rating=pd.DataFrame()                                                                     #dataframe for perticuler genre
        movie_grp=movie[movie['genres'].str.contains(g)].loc[:,['movieId']]                             #same genre movie grp
        movieId=movie_grp['movieId'].unique().tolist()                                                  #same genre movie id list        
        user_Rating=rating[rating['movieId'].isin(movie_grp['movieId'])]                                #all user rating for same genre movie
        movie_rating=pd.concat([movie_rating,movie_grp],axis=1)                                         #add movie id for merge
        for i in range(1,611):
            p_user_Rating=user_Rating[user_Rating['userId']==int(i)].loc[:,['movieId','rating']]        #perticuler user rating
            movie_rating=pd.merge(movie_rating,p_user_Rating,on='movieId',how='left')                   #combine in dataframe                
        movie_rating=movie_rating.loc[:,movie_rating.columns != 'movieId']                              #remove movieId for all user
        movie_rating.columns=column                                                                     #add column values as user
        movie_rating=movie_rating.fillna(0)                                                             #fill NaN value with zero    
        movie_rating=sim(movie_rating)                                                                  #find cosine similarity between movie based on user rating    
        movie_rating=pd.DataFrame(movie_rating,columns=movieId)                                         #convert similarity array into dataframe
        movie_rating.index = [x for x in movieId]                                                       #add index as movie id
        movie_rating.index.name='movieId'                                                               
        movie_rating=sortdata(movie_rating.loc[movie_rating.index==movieID],movieId,1)                  #sort data for given movie id
        movie_rating=pd.DataFrame(movie_rating[1:,:],columns=movie_rating[0:1,:].ravel())               #convert sorted array into dataframe    
        movie_rating.index = [movieID]                                                          
        movie_rating.index.name='movieId'
        ownRating=rating[rating['userId']==(int(userID))]                                               #user all rating data
        ownMovie=ownRating['movieId'].tolist()                                                          #movieid list for given user rated movie
        for x in range(1,len(movieId)):                                                                 #loop for find not watched similar movie
            Id=int(movie_rating.columns.values[x])
            if(Id  not in recomendedMovieData and Id not in ownMovie ):
                recomended=movie[movie['movieId']==Id]
                recomendedMovieData.append(recomended['movieId'].iat[0])
    return recomendedMovieData


#movie recomendation function
def recomendation(rating,movie,imdb,genre_list,userID,similar_user_Id,column,Genres_list_most_view):
    recomendedData={}
    ownRating=rating[rating['userId']==(int(userID))]                               #user all rating data
    ownMovie=ownRating['movieId'].tolist()                                          #movieid list for given user rated movie
    recomendedData['genreList']=genre_list
    for g in genre_list:
        i=0
        j=1
        li=[]
        while(i<6):
            userRating=rating[rating['userId']==(int(similar_user_Id[j]))]                     #similar user all rating data
            j=j+1
            userMovie=movie[movie['movieId'].isin(userRating['movieId'])]                   #similar user movie data which he give rating
            movieList=userMovie[userMovie['genres'].str.contains(g)]                    #movie data for perticuler genre
            movieLists=userRating[userRating['movieId'].isin(movieList['movieId'])]     #movie rating for that perticuler genre     
            movieLists=movieLists.sort_values('rating',ascending=False)                 #sort accorfing to rating value                            
            for x in range(len(movieLists)):                                            #loop for to get movie seen by user or not                                        
                movieId=movieLists['movieId'].iat[x]
                if(movieId  not in ownMovie ):
                    i=i+1
                    recomended=movie[movie['movieId']==movieId]
                    l=[]
                    l.append(recomended['movieId'].iat[0])
                    l.append(recomended['title'].iat[0])
                    imdbId=imdb[imdb['movieId']==movieId]
                    l.append(recomended['avgRating'].iat[0])
                    ln ="../static/img/Movie_Poster_Dataset/tt0"+str(imdbId['imdbId'].iat[0])+".jpg"
                    l.append(ln)
                    li.append(l)
                    if(i==6):
                        break
            
        recomendedData[g]=li  
    for g in Genres_list_most_view:
        i=0
        j=1
        li=[]
        while(i<6):
            userRating=rating[rating['userId']==(int(similar_user_Id[j]))]                     #similar user all rating data
            j=j+1
            userMovie=movie[movie['movieId'].isin(userRating['movieId'])]                   #similar user movie data which he give rating
            movieList=userMovie[userMovie['genres'].str.contains(g)]                    #movie data for perticuler genre
            movieLists=userRating[userRating['movieId'].isin(movieList['movieId'])]     #movie rating for that perticuler genre     
            movieLists=movieLists.sort_values('rating',ascending=False)                 #sort accorfing to rating value                            
            for x in range(len(movieLists)):                                            #loop for to get movie seen by user or not                                        
                movieId=movieLists['movieId'].iat[x]
                if(movieId  not in ownMovie ):
                    i=i+1
                    recomended=movie[movie['movieId']==movieId]
                    l=[]
                    l.append(recomended['movieId'].iat[0])
                    l.append(recomended['title'].iat[0])
                    imdbId=imdb[imdb['movieId']==movieId]
                    l.append(recomended['avgRating'].iat[0])
                    ln ="../static/img/Movie_Poster_Dataset/tt0"+str(imdbId['imdbId'].iat[0])+".jpg"
                    l.append(ln)
                    li.append(l)
                    if(i==6):
                        break
            
        recomendedData[g]=li  
  
    recomendedData['mostView']=Genres_list_most_view          
    return recomendedData




def recommend(userEmailAdd):
    movie = pd.read_csv('ml-latest-small/movies.csv',encoding = "ISO-8859-1")
    rating = pd.read_csv('ml-latest-small/ratings.csv')
    imdb = pd.read_csv('ml-latest-small/links.csv')
    userData=pd.read_csv('ml-latest-small/users.csv')
    
    userID=userData[userData['email']==userEmailAdd]
    if (len(userID)==0):
        return False
    userID=userID['userId'].iat[0]
    gener =['Action','Adventure','Animation','Children','Comedy','Crime','Documentary','Drama','Fantasy','Film-Noir','Horror','Musical','Mystery','Romance','Sci-Fi','Thriller','War','Western']
    user=rating['userId'].unique().tolist()
    similar_user=similarUser(rating, movie,gener,gener,user,userID,gener,user)
    dic=recomendation(rating,movie,imdb,similar_user[1],userID,similar_user[0],user,similar_user[2])
    return dic

## -------- end ---------


## ------ similar movie data using simila movie ------

def _prep_data():
        # read data
        df_movies = pd.read_csv(r"ml-latest-small/movies.csv",usecols=['movieId', 'title'],dtype={'movieId': 'int32', 'title': 'str'},encoding="ISO-8859-1")
        df_ratings = pd.read_csv( r"ml-latest-small/ratings.csv",usecols=['userId', 'movieId', 'rating'],dtype={'userId': 'int32', 'movieId': 'int32', 'rating': 'float32'})
        # filter data
        df_movies_cnt = pd.DataFrame(df_ratings.groupby('movieId').size(),columns=['count'])
        popular_movies = list(set(df_movies_cnt.query('count >= 0').index))  # noqa
        movies_filter = df_ratings.movieId.isin(popular_movies).values

        df_users_cnt = pd.DataFrame(df_ratings.groupby('userId').size(),columns=['count'])
        active_users = list(set(df_users_cnt.query('count >= 0').index))  # noqa
        users_filter = df_ratings.userId.isin(active_users).values

        df_ratings_filtered = df_ratings[movies_filter & users_filter]

        # pivot and create movie-user matrix
        movie_user_mat = df_ratings_filtered.pivot(index='movieId', columns='userId', values='rating').fillna(0)
        # create mapper from movie title to index
        hashmap = {
            movie: i for i, movie in enumerate(list(df_movies.set_index('movieId').loc[movie_user_mat.index].title)) # noqa
        }
        # transform matrix to scipy sparse matrix
        movie_user_mat_sparse = csr_matrix(movie_user_mat.values)

        # clean up
        del df_movies, df_movies_cnt, df_users_cnt
        del df_ratings, df_ratings_filtered, movie_user_mat
        gc.collect()
        return movie_user_mat_sparse, hashmap




def simMovie(fav_movie, n_recommendations):
    l=[]
    movie = pd.read_csv('ml-latest-small/movies.csv',encoding="ISO-8859-1")
    imdb = pd.read_csv('ml-latest-small/links.csv')
    
    # get data
    movie_user_mat_sparse, hashmap = _prep_data()
        
    model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
    
    # get recommendations
    raw_recommends = _inference(model_knn, movie_user_mat_sparse, hashmap,fav_movie, n_recommendations)
    # print results
    reverse_hashmap = {v: k for k, v in hashmap.items()}
    print('Recommendations for {}:'.format(fav_movie))
    for i,(idx, dist) in enumerate(raw_recommends):
        li=[]
        title=str(reverse_hashmap[idx])
        movieId=movie[movie["title"]==str(title)]
        li.append(int(movieId["movieId"].iat[0]))
        li.append(title) 
        li.append(float(movieId["avgRating"].iat[0]))
        imdbId=imdb[imdb['movieId']==int(movieId["movieId"].iat[0])]
        ln ="../static/img/Movie_Poster_Dataset/tt0"+str(imdbId['imdbId'].iat[0])+".jpg"
        li.append(ln)
        l.append(li) 
        print(i)
    return l   



def _inference(model, data, hashmap,fav_movie, n_recommendations):
       
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

    
# -------- end ------------------



def userInfo(userEmailAdd,genre,mostView):
    l={}
    m=[]
    v=[]
    userData=pd.read_csv('ml-latest-small/users.csv')
    userRow=userData[userData['email']==userEmailAdd]
    userID=int(userRow['userId'].iat[0])
    userFName=userRow['first_name'].iat[0]
    userLName=userRow['last_name'].iat[0]
    userPassword=userRow['password'].iat[0]
    l['userId']=userID
    l['Fname']=userFName
    l['Lname']=userLName
    l['pass']=userPassword
    movie = pd.read_csv('ml-latest-small/movies.csv',encoding = "ISO-8859-1")
    rating = pd.read_csv('ml-latest-small/ratings.csv')
    rating=rating[rating['userId']==int(userID)]
    for g in genre:
        li=[]
        mgroup = movie[movie['genres'].str.contains(g)]                                               #grp same genre movie  
        avgRating = rating[rating['movieId'].isin(mgroup['movieId'])].loc[:, ['rating']].mean().round(2)     #find avg rating for genres by each user
        totalRating=len(rating[rating['movieId'].isin(mgroup['movieId'])])
        li.append(g)
        li.append(totalRating)
        li.append(float(avgRating))
        m.append(li)
    l['gnereList']=m
    for g in mostView:
        li=[]
        mgroup = movie[movie['genres'].str.contains(g)]                                               #grp same genre movie  
        avgRating = rating[rating['movieId'].isin(mgroup['movieId'])].loc[:, ['rating']].mean().round(2)     #find avg rating for genres by each user
        totalRating=len(rating[rating['movieId'].isin(mgroup['movieId'])])
        li.append(g)
        li.append(totalRating)
        li.append(float(avgRating))
        v.append(li)
    l['mostView']=v
    return l

def allUserInfo():
    userData=pd.read_csv('ml-latest-small/users.csv')
    usersInfo=[]
    for i in range(1,len(userData)):
        a=[]
        a.append(i)
        userRow=userData[userData['userId']==i]
        a.append(userRow['email'].iat[0])
        a.append(userRow['ratingCount'].iat[0])
        usersInfo.append(a)
    return usersInfo

def userStatestics(userId):
    l=[]
    userData=pd.read_csv('ml-latest-small/users.csv')
    userData=userData[userData["userId"]==int(userId)]
    l.append(userData["first_name"].iat[0])
    l.append(userData["last_name"].iat[0])
    gener =['Action','Adventure','Animation','Children','Comedy','Crime','Documentary','Drama','Fantasy','Film-Noir','Horror','Musical','Mystery','Romance','Sci-Fi','Thriller','War','Western']
    l.append(gener)
    userRating=pd.read_csv('ml-latest-small/userAvgRating.csv')
    userRatingCount=pd.read_csv('ml-latest-small/userRatingCount.csv')
    userRating=userRating[userRating['userId']==int(userId)]
    userRatingCount=userRatingCount[userRatingCount['userId']==int(userId)]
    userRating=userRating.values.tolist()[0]
    userRatingCount=userRatingCount.values.tolist()[0]
    userRating.pop(0)
    userRatingCount.pop(0)
    l.append(userRating)
    l.append(userRatingCount)
    return l


def allMovieInfo():
    movie = pd.read_csv('ml-latest-small/movies.csv',encoding = "ISO-8859-1")
    moviesInfo=[]
    movieId=movie['movieId'].tolist()
    movieId.pop(0)
    for i in movieId:
        a=[]
        a.append(i)
        movieRow=movie[movie['movieId']==i]
        a.append(movieRow['title'].iat[0])
        a.append(movieRow['ratingCount'].iat[0])
        moviesInfo.append(a)
    return moviesInfo

def movieStatestics(movieId):
    l=[]
    movie = pd.read_csv('ml-latest-small/movies.csv',encoding = "ISO-8859-1")
    imdb = pd.read_csv('ml-latest-small/links.csv')
    imdbId=imdb[imdb['movieId']==int(movieId)]
    if movieId==0:
        ln="../static/img/alt.png';"
    else:
        ln ="../static/img/Movie_Poster_Dataset/tt0"+str(imdbId['imdbId'].iat[0])+".jpg"
    movieRow=movie[movie["movieId"]==int(movieId)]
    l.append(ln)
    l.append(str(movieRow["title"].iat[0]))
    l.append(str(movieRow["genres"].iat[0]))
    l.append(movieRow["avgRating"].iat[0])
    l.append(movieRow["ratingCount"].iat[0])
    l.append(movieRow["0.5 Star"].iat[0])
    l.append(movieRow["1 Star"].iat[0])
    l.append(movieRow["1.5 Star"].iat[0])
    l.append(movieRow["2 Star"].iat[0])
    l.append(movieRow["2.5 Star"].iat[0])
    l.append(movieRow["3 Star"].iat[0])
    l.append(movieRow["3.5 Star"].iat[0])
    l.append(movieRow["4 Star"].iat[0])
    l.append(movieRow["4.5 Star"].iat[0])
    l.append(movieRow["5 Star"].iat[0])
    l.append(movieRow["movieId"].iat[0])
    return l



def searchDataInfo(query):
    l=[]
    query=query.lower()
    movie = pd.read_csv('ml-latest-small/movies.csv',encoding = "ISO-8859-1")
    imdb = pd.read_csv('ml-latest-small/links.csv')
    movie = movie[movie['title'].str.contains(query,case=False  )]
    movie = movie.values.tolist()
    length=len(movie)
    print(length)
    print(movie)
    for i in range(length):
        li=[]
        li.append(movie[i][0])
        li.append(movie[i][1])
        print("qwqw")
        li.append(movie[i][14])
        imdbId=imdb[imdb['movieId']==li[0]]
        print(imdbId)
        print("sss")
        print(str(imdbId['imdbId'].iat[0]))
        print("kkk")

        ln ="../static/img/Movie_Poster_Dataset/tt0"+str(imdbId['imdbId'].iat[0])+".jpg"
        print(ln)
        li.append(ln)
        l.append(li)
    return l     


def userEntry(Fname,Lname,password,Email,contact):
    userData=pd.read_csv('ml-latest-small/users.csv')
    userId=int(userData['userId'].max())+1
    row=[userId,Fname,Lname,contact,Email,password,0]
    with open('ml-latest-small/users.csv', 'a+', newline='') as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(row)

def addMovieData(title,genre,imdbid):
    movie=pd.read_csv('ml-latest-small/movies.csv',encoding = "ISO-8859-1")
    movieId=int(movie['movieId'].max())+1
    row1=[movieId,imdbid]
    genre=genre.replace(",","|")
    row=[movieId,title,genre,0,0,0,0,0,0,0,0,0,0,0,0]
    with open('ml-latest-small/movies.csv', 'a+', newline='') as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(row)
    with open('ml-latest-small/links.csv', 'a+', newline='') as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(row1)
    


def moviescrap(movieId):
    imdb = pd.read_csv('ml-latest-small/links.csv',encoding = "ISO-8859-1")
    movieId=str(movieId)
    print(movieId)
    if movieId[0]=="t":
        imdbId=movieId
        url = 'https://www.imdb.com/title/'+ str(imdbId)
    
    else:
        imdbId=imdb[imdb["movieId"]==int(movieId)]
        print(imdbId)
        imdbId=int(imdbId["imdbId"].iat[0])    
        url = 'https://www.imdb.com/title/'+ 'tt0'+str(imdbId)
    
    print(imdbId)
    print(url)
    response = get(url, verify=False)
    movieinfo = {}
    if response.status_code == 200: 

        html_soup = BeautifulSoup(response.text, 'html.parser')

        summary = html_soup.find_all('div', class_ = 'summary_text')
        if summary:
            summary = summary[0].text.lstrip().rstrip().split('\n')[0]
        else:
            summary = " "
            


        rating = html_soup.find_all('div', class_ = 'ratingValue')
        if rating:
                rating = rating[0].text.lstrip().rstrip()
        else:
                rating = " "

        title = html_soup.find_all('div', class_ = 'title_wrapper')
        if title:
            name = title[0].h1.text
        else:
            name = " "
        g = []
        releasedate = " "
        time = " "
        subtext = html_soup.find_all('div', class_ = 'subtext')
        if subtext:
            if subtext[0].time:
                time = subtext[0].time.text.replace("\n","").lstrip().rstrip()
            links = subtext[0].find_all('a')
            for a in links:
                if(a['href'].find("genres") != -1):
                    g.append(a.text.replace("\n","").lstrip().rstrip())
                elif(a['href'].find("releaseinfo") != -1):
                    releasedate = a.text.replace("\n","").lstrip().rstrip()
            g = str(g).strip('[]').replace("'","")
        else:
            g = " "
            

        poster = html_soup.find_all('div', class_ = 'poster')
        if poster:
            poster = poster[0].img['src']
        else:
            poster= " "
        
        d=[]
        w=[]
        c=[]
        crew = html_soup.find_all('div', class_ = 'credit_summary_item')
        if crew:
            for i in range(0, len(crew)):
                if(crew[i].h4.text.find("Director") != -1):
                    director = crew[i].find_all('a')
                    for a in director:
                        if(a['href'].find("fullcredits") == -1):
                            d.append(a.text)
                    d = str(d).strip('[]').replace("'","")
                elif(crew[i].h4.text.find("Writer") != -1):
                    writer = crew[1].find_all('a')
                    for a in writer:
                        if(a['href'].find("fullcredits") == -1):
                            w.append(a.text)
                    w = str(w).strip('[]').replace("'","")
                elif(crew[i].h4.text.find("Star") != -1):
                    cast = crew[1].find_all('a')
                    for a in cast:
                        if(a['href'].find("fullcredits") == -1):
                            c.append(a.text)
                    c = str(c).strip('[]').replace("'","")
        else:
            d = " "
            w = " "
            c = " "

        movieinfo['title'] = name
        movieinfo['imdbrating'] = rating
        movieinfo['runtime'] = time
        movieinfo['genre'] = g
        movieinfo['releasedate'] = releasedate
        movieinfo['summary'] = summary
        movieinfo['posterurl'] = poster
        movieinfo['director'] = d
        movieinfo['writer'] = w
        movieinfo['cast'] = c
        print(movieinfo)
        return movieinfo
    
def rated(userId,movieId):
    ratings = pd.read_csv('ml-latest-small/ratings.csv')
    ratings=ratings[ratings["userId"]==int(userId)]
    ratings=ratings.values.tolist()
    j=0
    rat=0
    flag=False
    for i in ratings:
        if i[1]==int(movieId):
            rat=ratings[j][2]
            flag=True
            break
        j=j+1
    if flag:
        l=[]
        l.append(flag)
        l.append(rat)
    else:
        l=[]
        l.append(flag)
        l.append(0)   
    return l 

def giveRating(rating,userId,movieId):
    rating=float(rating)
    movie = pd.read_csv('ml-latest-small/movies.csv',encoding = "ISO-8859-1")
    userData=pd.read_csv('ml-latest-small/users.csv')
    avgRating=pd.read_csv('ml-latest-small/userAvgRating.csv')
    ratingCount=pd.read_csv('ml-latest-small/userRatingCount.csv')
    ratings = pd.read_csv('ml-latest-small/ratings.csv')
    

    ratings=ratings[ratings["userId"]==int(userId)]
    ratings=ratings.values.tolist()
    j=0
    flag=False
    for i in ratings:
        if i[1]==int(movieId):
            flag=True
            break
    if  not flag:
        row=[int(userId),int(movieId),rating]
        with open('ml-latest-small/ratings.csv', 'a+', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(row)



    userData=userData.values.tolist()
    j=0
    for i in userData:
        if i[0]==int(userId):
            userData[j][6]=userData[j][6]+1
            break
        j=j+1

    userData=pd.DataFrame(userData,columns=["userId","first_name","last_name","phone","email","password","ratingCount"])
    userData=userData.loc[:,userData.columns != 'index']
    print(userData)
    userData.to_csv('ml-latest-small/users.csv',index=False)
    j=0
    if float(rating)== 0.5:
        col=4
    if float(rating)== 1:
        col=5
    if float(rating)== 1.5:
        col=6
    if float(rating)== 2:
        col=7
    if float(rating)== 2.5:
        col=8
    if float(rating)== 3:
        col=9
    if float(rating)== 3.5:
        col=10
    if float(rating)== 4:
        col=11
    if float(rating)== 4.5:
        col=12
    if float(rating)== 5:
        col=13
    
    movie=movie.values.tolist()
    j=0
    for i in movie:
        if i[0]==int(movieId):
            movie[j][col]=movie[j][col]+1
            movie[j][14]=(float((float(movie[j][14])*float(movie[j][3])+float(rating)))/(float(movie[j][3])+1 ))
            movie[j][14]=round(movie[j][14],2)
            movie[j][3]=movie[j][3]+1
            break
        j=j+1
    movie=pd.DataFrame(movie,columns=["movieId","title","genres","ratingCount","0.5 Star","1 Star","1.5 Star","2 Star","2.5 Star","3 Star","3.5 Star","4 Star","4.5 Star","5 Star","avgRating"])
    movie=movie.loc[:,movie.columns != "index"]
    movie.to_csv('ml-latest-small/movies.csv',index=False)

    movieRow=movie[movie["movieId"]==int(movieId)]
    genre = movieRow['genres'].iat[0]
    genre= genre.split("|")
    gener =['Action','Adventure','Animation','Children','Comedy','Crime','Documentary','Drama','Fantasy','Film-Noir','Horror','Musical','Mystery','Romance','Sci-Fi','Thriller','War','Western']
    
    avgRating=avgRating.values.tolist()
    ratingCount=ratingCount.values.tolist()
    j=0
    for i in avgRating:
        if i[0] == int(userId):
            for g in genre:
                index1=gener.index(g)+1
                avgRating[j][index1]=(float(avgRating[j][index1])*float(ratingCount[j][index1])+float(rating))/(ratingCount[j][index1]+1)
                avgRating[j][index1]=round(avgRating[j][index1],2)
                ratingCount[j][index1]=ratingCount[j][index1]+1
            break
        j=j+1
    avgRating=pd.DataFrame(avgRating,columns=["userId",'Action','Adventure','Animation','Children','Comedy','Crime','Documentary','Drama','Fantasy','Film-Noir','Horror','Musical','Mystery','Romance','Sci-Fi','Thriller','War','Western'])
    avgRating=avgRating.loc[:,avgRating.columns != "index"]
    avgRating.to_csv('ml-latest-small/userAvgRating.csv',index=False)

    ratingCount=pd.DataFrame(ratingCount,columns=["userId",'Action','Adventure','Animation','Children','Comedy','Crime','Documentary','Drama','Fantasy','Film-Noir','Horror','Musical','Mystery','Romance','Sci-Fi','Thriller','War','Western'])
    ratingCount=ratingCount.loc[:,ratingCount.columns != "index"]
    ratingCount.to_csv('ml-latest-small/userRatingCount.csv',index=False)

    
