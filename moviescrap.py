from requests import get
from bs4 import BeautifulSoup

def movie():
    url = 'https://www.imdb.com/title/'+ 'tt0114709'
    print("HI")
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

        return movieinfo

        

        
movie()
        