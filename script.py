import numpy as np 
import pandas as pd
import csv

movie = pd.read_csv('ml-latest-small/movies.csv',encoding = "ISO-8859-1")
rating = pd.read_csv('ml-latest-small/ratings.csv')
userData=pd.read_csv('ml-latest-small/users.csv',encoding = "ISO-8859-1")
gener =['Action','Adventure','Animation','Children','Comedy','Crime','Documentary','Drama','Fantasy','Film-Noir','Horror','Musical','Mystery','Romance','Sci-Fi','Thriller','War','Western']
avgRating=pd.read_csv('ml-latest-small/userAvgRating.csv')
ratingCount=pd.read_csv('ml-latest-small/userRatingCount.csv')


movieRow=movie[movie["movieId"]==int(1)]
genre = movieRow['genres'].iat[0]
genre= genre.split("|")
       

userId=1
rating=1
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
# avgRating.to_csv('ml-latest-small/userAvgRating.csv')

ratingCount=pd.DataFrame(ratingCount,columns=["userId",'Action','Adventure','Animation','Children','Comedy','Crime','Documentary','Drama','Fantasy','Film-Noir','Horror','Musical','Mystery','Romance','Sci-Fi','Thriller','War','Western'])
ratingCount=ratingCount.loc[:,ratingCount.columns != "index"]
ratingCount.to_csv('ml-latest-small/userRatingCount.csv')




# movie=movie.values.tolist()
# j=0
# col=5
# for i in movie:
#     if i[0]==1:
#         movie[j][col]=movie[j][col]+1
#         movie[j][14]=(float((float(movie[j][14])*float(movie[j][3])+float(1)))/(float(movie[j][3])+1 ))
#         movie[j][14]=round(movie[j][14],2)
#         movie[j][3]=movie[j][3]+1
#         break
#     j=j+1
# movie=pd.DataFrame(movie,columns=["movieId","title","genres","ratingCount","0.5 Star","1 Star","1.5 Star","2 Star","2.5 Star","3 Star","3.5 Star","4 Star","4.5 Star","5 Star","avdRating"])
# movie=movie.loc[:,movie.columns != "index"]
# movie.to_csv('ml-latest-small/movies.csv',index=False)













# userData=userData.values.tolist()

# j=0
# for i in userData:
#     print(i)
#     if i[0]==1:
#         print(i[6])
#         print(j)
#         userData[j][6]=userData[j][6]+1
#         break
#     j=j+1

# userData=pd.DataFrame(userData,columns=["userId","first_name","last_name","phone","email","password","ratingCount"])
# userData=userData.loc[:,userData.columns != 'index']
# print(userData)
# userData.to_csv('ml-latest-small/users.csv',index=False)
    



# movieId=movie['movieId'].tolist()
# l=[]
# for i in  movieId:
#     ratingCount=rating[rating['movieId']==i].loc[:,['rating']].mean().round(2)
#     l.append(float(ratingCount))
# movie['avgRating']=l
# movie.to_csv('ml-latest-small/movies.csv')







# movieId=movie['movieId'].tolist()
# l=[]
# q=[]
# w=[]
# e=[]
# r=[]
# t=[]
# y=[]
# u=[]
# o=[]
# h=[]
# for i in  movieId:
#     ratingCount=rating[rating['movieId']==i]
#     ratingCount=ratingCount[ratingCount["rating"]==1]
#     l.append(len(ratingCount))
# for i in movieId:    
#     ratingCount=rating[rating['movieId']==i]
#     ratingCount=ratingCount[ratingCount["rating"]==2]
#     q.append(len(ratingCount))
# for i in movieId:
#     ratingCount=rating[rating['movieId']==i]
#     ratingCount=ratingCount[ratingCount["rating"]==3]
#     w.append(len(ratingCount))
# for i in movieId:
#     ratingCount=rating[rating['movieId']==i]
#     ratingCount=ratingCount[ratingCount["rating"]==4]
#     e.append(len(ratingCount))
# for i in movieId:
#     ratingCount=rating[rating['movieId']==i]
#     ratingCount=ratingCount[ratingCount["rating"]==5]
#     r.append(len(ratingCount))
# for i in  movieId:
#     ratingCount=rating[rating['movieId']==i]
#     ratingCount=ratingCount[ratingCount["rating"]==1.5]
#     t.append(len(ratingCount))
# for i in movieId:    
#     ratingCount=rating[rating['movieId']==i]
#     ratingCount=ratingCount[ratingCount["rating"]==2.5]
#     y.append(len(ratingCount))
# for i in movieId:
#     ratingCount=rating[rating['movieId']==i]
#     ratingCount=ratingCount[ratingCount["rating"]==3.5]
#     u.append(len(ratingCount))
# for i in movieId:
#     ratingCount=rating[rating['movieId']==i]
#     ratingCount=ratingCount[ratingCount["rating"]==4.5]
#     o.append(len(ratingCount))
# for i in movieId:
#     ratingCount=rating[rating['movieId']==i]
#     ratingCount=ratingCount[ratingCount["rating"]==0.5]
#     h.append(len(ratingCount))

# movie['0.5 Star']=h
# movie['1 Star']=l
# movie['1.5 Star']=t
# movie['2 Star']=q
# movie['2.5 Star']=y
# movie['3 Star']=w
# movie['3.5 Star']=u
# movie['4 Star']=e
# movie['4.5 Star']=o
# movie['5 Star']=r
# movie.to_csv('ml-latest-small/movies.csv')











# userRating=pd.read_csv('ml-latest-small/userAvgRating.csv')
# userRatingCount=pd.read_csv('ml-latest-small/userRatingCount.csv')
# userRating=userRating[userRating['userId']==1]
# userRatingCount=userRatingCount[userRatingCount['userId']==1]
# userRating=userRating.values.tolist()[0]

# print(userRating)        
















# l=[]
# for i in range(1,len(userData)+1):
#     a=[]
#     a.append(i)
#     userRating=rating[rating['userId']==i]
#     for g in gener:
#         mGroup=movie[movie['genres'].str.contains(g)]
#         avgRating=float(userRating[userRating['movieId'].isin(mGroup['movieId'])].loc[:,['rating']].mean().round(2))
#         a.append(avgRating)
#     l.append(a)
# column =['userId','Action','Adventure','Animation','Children','Comedy','Crime','Documentary','Drama','Fantasy','Film-Noir','Horror','Musical','Mystery','Romance','Sci-Fi','Thriller','War','Western']
# df=pd.DataFrame(l)
# df.columns=column
# df=df.fillna(0)
# df.to_csv('ml-latest-small/mattrix.csv')














# movieId=movie['movieId'].tolist()
# l=[]
# for i in  movieId:
#     ratingCount=rating[rating['movieId']==i]
#     l.append(len(ratingCount))
# movie['ratingCount']=l
# movie.to_csv('ml-latest-small/movies.csv')










# userId=userData['userId'].tolist()
# l=[]
# print(len(userData))
# for i in range(1,len(userData)+1):
#     ratingCount=rating[rating['userId']==i]
#     l.append(len(ratingCount))
# userData['ratingCount']=l
# userData.to_csv('ml-latest-small/users.csv')








# movie_rating=pd.DataFrame()                                                                     #dataframe for perticuler genre
# movieId=movie['movieId'].unique().tolist()                                                  #same genre movie id list        
# movie_grp=movie.loc[:,['movieId']]                             #same genre movie grp
# movie_rating=pd.concat([movie_rating,movie_grp],axis=1)                                         #add movie id for merge
                
# movie_rating.index = [x for x in movieId]                                                       #add index as movie id
# movie_rating.index.name='movieid'                                                               
                       
# for i in range(1,611):
#     p_user_Rating=rating[rating['userId']==int(i)].loc[:,['movieId','rating']]   
#     # print(p_user_Rating)     #perticuler user rating
#     movie_rating=pd.merge(movie_rating,p_user_Rating,on='movieId',how='left')                   #combine in dataframe                
# print("1")
# movie_rating=movie_rating.loc[:,movie_rating.columns != 'movieId']                              #remove movieId for all user
# movie_rating.columns=[x for x in range(1,611)]                                                                     #add column values as user
# movie_rating=movie_rating.fillna(0)                                                             #fill NaN value with zero    
# movie_rating=movie_rating.T
# movie_rating.columns=movieId
