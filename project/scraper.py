import requests
from bs4 import BeautifulSoup
import smtplib
import datetime as dt
from email.mime.text import MIMEText
from article import Article
from email.mime.multipart import MIMEMultipart
# import base64
from datetime import timedelta
from pytz import timezone
import pytz
import time
import scrapy


CONST_DATETIME_STD_FORMAT = '%Y-%m-%d %H:%M:%S'
CONST_TIMEZONE = pytz.timezone('Europe/Berlin')
articleList = []
URL1 = 'https://www.njuskalo.hr/prodaja-kuca/zagreb?price[max]=131000&livingArea[min]=100'
URL2 = 'https://www.njuskalo.hr/prodaja-kuca/zagreb?price%5Bmax%5D=131000&livingArea%5Bmin%5D=100&page=2'

def get_page(url):
    # last_update_datetime = read_update_date()
    # uzmi zadnjih 4 sata    
    local_now = dt.datetime.now(CONST_TIMEZONE)
    last_update_datetime = local_now - timedelta(hours=4)

    headers = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}

    page = requests.get(url, headers = headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    entityList = soup.find("", {"class": "EntityList--ListItemRegularAd"})
    # entityListItem = entityList.find_all("a", {"class": "link"})

    #iščupaj naslov i cijenu oglasa    
    entityArticles = entityList.find_all('article')
    for article in entityArticles:
        title = (article.find('a').get_text().strip())
        price = (article.find("", {"class": "price--eur"}).get_text().strip().replace(u'\xa0', ' ') + "  " + article.find("", {"class": "price--hrk"}).get_text().strip().replace(u'\xa0', ' '))
        datetime_str = article.find("time").get("datetime")
        # datetime = dt.datetime.strptime(datetime_str[0:19], '%Y-%m-%dT%H:%M:%S')
        datetime = dt.datetime.fromisoformat(datetime_str)
        link = "njuskalo.hr" + article.find("a")['href']
        # image_url = "https:" + article.find("img")['data-src']
        # req = requests.get(image_url, stream=True)
        image = ""
        # print(image)
        published = datetime.strftime("%d.%m.%Y. %H:%M:%S")
     
        if datetime > last_update_datetime:
            articleList.append(Article(title, price, image, link, published))
    
   
    # update_config_file()


#šalji na mail
def send_mail():
    sender_email = "jlock2205@gmail.com"
    receiver_email = "jlock2205@gmail.com"
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(sender_email, 'Gmail2205')

    message = MIMEMultipart("alternative")
    message["Subject"] = "Prodaja kuća"
    message["From"] = sender_email
    message["To"] = receiver_email
        
    html = "<html><body>"

    for article in articleList:
        # data_uri = base64.b64encode(article.image)
        
        html += """\
    <p><a href={link}>{description}</a><br>
       {price}
       <br>
       <h6>Objavljeno:{published}</h6>
    </p>
    <br>
    <hr>
""".format(description=article.description, price=article.price, link = article.link, published = article.published)
        # MIMEText("bla", "plain")
        message.attach(MIMEText(html, 'html'))

    html = "</body></html>"

    server.sendmail(
        sender_email,
        receiver_email,
        message.as_string()
    )
    print('email is sent')
    server.quit()

def read_update_date():
    f = open("config.txt", "r")
    date_time_str =  f.read()
    result = dt.datetime.strptime(date_time_str, CONST_DATETIME_STD_FORMAT)
    f.close()
    return result

def update_config_file():
    f = open("config.txt", "w")
    f.write(dt.datetime.now().strftime(CONST_DATETIME_STD_FORMAT))
    f.close()

def run():
    articleList.clear()
    get_page(URL2)
    get_page(URL1)

    if articleList:
            send_mail()

while(True):
    run()
    time.sleep(60*60*4)