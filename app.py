from flask import Flask,flash,render_template,url_for,request,session,g,redirect
from clustering import recommend,userInfo,searchDataInfo,userEntry,allUserInfo,allMovieInfo,userStatestics,movieStatestics,moviescrap,simMovie,giveRating,addMovieData,rated
import os 
imdbID=""
userData={}
searchData={}
userGnere=[] 
userIn={}
similarMovie=[]
app = Flask(__name__)
app.secret_key=os.urandom(24)
@app.route('/')
def index():
    return render_template('index-sani.html')


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/admin/userDetails')
def userDetails():
    allUserData=allUserInfo()
    return render_template('userDetails-sani.html',data=allUserData)

@app.route('/admin/userStatestic',methods=['POST','GET'])
def userStatestic():
    if request.method=="POST":
        userState=userStatestics(request.form['userId'])
    if request.method=="GET":
        userState=userStatestics(0)
    return render_template('userStatestic-sani.html',data=userState)

@app.route('/admin/movieDetails')
def movieDetails():
    allMovieData=allMovieInfo()
    return render_template('movieDetails-sani.html',data=allMovieData)


@app.route('/admin/movieStatestic',methods=["POST","GET"])
def movieStatestic():
    if request.method=="POST":
        movieState=movieStatestics(request.form["movieId"])
    if request.method=="GET":
        movieState=movieStatestics(0)
    return render_template('movieStatestics-sani.html',data=movieState)


@app.route("/admin/addMovie",methods=["POST","GET"])
def addMovie():
    global imdbID
   
    if request.method=="POST" and request.form["link"]=="addMovieData":
        addMovieData(request.form['title'],request.form['genre'],imdbID)
        movieInfo=moviescrap(imdbID)
        flash("Movie Added")        

    if request.method=="POST" and request.form["link"]=="searchMovieData":
        imdbID=request.form["imdbId"]
        movieInfo=moviescrap(request.form["imdbId"])
        movieInfo['msg']=" "
        
    if request.method=="GET":
        movieInfo={}
        movieInfo['title'] = " "
        movieInfo['imdbrating'] = " "
        movieInfo['runtime'] = " "
        movieInfo['genre'] = " "
        movieInfo['releasedate'] = " "
        movieInfo['summary'] = " "
        movieInfo['posterurl'] = "../static/img/alt.png"
        movieInfo['director'] = " "
        movieInfo['writer'] = " "
        movieInfo['cast'] = " "
        movieInfo['msg']=" "

    return render_template("addMovie-sani.html",mdata=movieInfo)

@app.route('/login',methods=['GET'])
def login():
    if 'user' in session:
        return render_template('home-sani.html',redic=session['userData'])
    return render_template('login.html')

@app.route('/logout',methods=['GET'])
def logout():
    global userData
    global userGnere
    global userIn
    if 'user' in session:
        if session['user']=="admin@movieAdda.com":
            session.pop('user',None)
        else:    
            session.pop('user',None)
            userGnereList.pop()
            userMostView.pop()
            userIn.clear()
            userData.clear()
            searchData.clear()
        flash('You were successfully logged in')
        return render_template('index-sani.html')
    else:
        return redirect(url_for('login'))    


@app.route('/home',methods=['POST','GET'])
def home():
    global userData
    global userIn
    global userGnereList
    global userMostView
    
    if 'user' in session:
        return render_template('home-sani.html',redic=userData,userIn=userIn)

    if request.method=='GET':
        return render_template('home-sani.html',redic=userData,userIn=userIn)

    if request.form['userEmailAdd'] == "admin@movieAdda.com":
        if request.form['password'] == "admin":
            user=request.form['userEmailAdd']
            session['user']=user
            return redirect(url_for('userDetails'))
        else:
            return render_template('login.html',error="The  Email Address of Password you entered is incorrect!!")    


    if request.method=='POST': 
        userIn={}
        userGnereList=[]
        userMostView=[]
        userData={}
        user=request.form['userEmailAdd']
        password=request.form['password']
        userData=recommend(user)
        if not userData:
            if request.form['register'] == 'true':
                Fname=request.form['userFName']
                Lname=request.form['userLName']
                password=request.form['password']
                cpassword=request.form['cpassword']
                Email=request.form['userEmailAdd']
                contact=request.form['userContact']
                if password==cpassword:
                    userEntry(Fname,Lname,password,Email,contact)
                    userData=recommend(user)    
                else:
                    return render_template('register.html',perror="password and confirm password is not match")
            else:
                return render_template('login.html',error="The  Email Address of Password you entered is incorrect!!")

        userGnereList=userData['genreList']
        userMostView=userData['mostView']
        
        userIn=userInfo(user,userGnereList,userMostView)
        if(password != userIn['pass']):
            return render_template('login.html',error="The  Email Address of Password you entered is incorrect!!")
 
        session['user']=user
        print(session['user'])
        return render_template('home-sani.html',redic=userData,userIn=userIn)   
    return redirect(url_for('login'))    

@app.route('/profile',methods=['GET'])
def profile():
    if 'user' in session:
        
        return render_template('profile-sani.html',data=userIn)
    else:
        return redirect(url_for('login'))

@app.route('/movieInfo',methods=['POST','GET'])
def movieInfo():
    global userIn
    global similarMovie
    if request.form["link"] == 'movieInfo':
        rating=request.form["rating"]
        userId=request.form["userId"]
        movieId=request.form["movieId"]
        test=rated(userId,movieId)
        print(test)
        print("ssssssssssssssssssssssssssssssssssssssssss")
        if  not test[0]:
            test[0]=True
            test[1]=rating
            giveRating(rating,userId,movieId)
        movieInfo=movieStatestics(request.form["movieId"])
        movieIn=moviescrap(request.form["movieId"])
        similarMovie=simMovie(movieInfo[1],12)
          
        return render_template('movieInfo-sani.html',data=movieInfo,mdata=movieIn,sdata=similarMovie,userIn=userIn,test=test)
    if request.method=='POST':
        if 'user' in session:

            test=rated(request.form["userId"],request.form["movieId"])
        
            movieInfo=movieStatestics(request.form["movieId"])
            movieIn=moviescrap(request.form["movieId"])
            similarMovie=simMovie(movieInfo[1],12)
            return render_template('movieInfo-sani.html',data=movieInfo,mdata=movieIn,sdata=similarMovie,userIn=userIn,test=test)
        else:
            return redirect(url_for('login'))
    else:
        if 'user' in session:
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))

@app.route('/search',methods=['POST','GET'])
def search():
    global searchData
    global userIn
    if request.method=="POST":
        if 'user' in session:
            searchData=searchDataInfo(request.form['search'])
            print(len(searchData)/6)
            return render_template('search.html',search=searchData,length=int(len(searchData)/6),totel=len(searchData),userIn=userIn)




@app.before_request
def before_request():
    g.user=None
    if 'user' in session:
        g.user = session['user']



if __name__ == '__main__':
    app.run(debug=True)