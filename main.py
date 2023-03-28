import pymysql
import datetime
import bs4
import requests
import json
import csv
import numpy
import schedule
import time

def getHTMLtext(url):
    try:
        r = requests.get(url, timeout=30)
        r.encoding ="UTF-8"
        soup = bs4.BeautifulSoup(r.text, "html.parser")
        soup.encode(encoding="UTF-8", errors="strict")
        return r.text
    except:
        print("Fail")
        return ""
#od=第一個 數據是錯的
data_all=[]
#資料庫連線設定

#要先在MYSQLWorkbench 裏面創一個db_weather
db = {
    "host":'localhost',
    "port":3306,
    "user":'root',
    "passwd":'@ablove77@',
    "db":'beauty_1',
    "charset":'utf8'
}
def get_content(html, cityname):
    Now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    final = []
    bs = bs4.BeautifulSoup(html, "html.parser")
    body = bs.body
    data = body.find('div', attrs={'class':'c7d'})
    data2 = body.find_all('div', attrs={'class':'left-div'})
    text = data2[2].find('script').string
    text = text[text.index('=')+1: -2]
    jd = json.loads(text)
    dayone = jd['od']['od2']
    final_day = []
    count = 0
    for i in dayone:
        temp = []
        if count >=1 and count <=24:
            temp.append(str(Now))
            temp.append(i['od21'])
            temp.append(cityname+'市')
            temp.append(i['od22'])
            temp.append(i['od24'])
            temp.append(i['od25'])
            temp.append(i['od26'])
            temp.append(i['od27'])
            temp.append(i['od28'])
            try:
                    # 建立Connection物件
                conn = pymysql.connect(**db)
                    # 建立Cursor物件
                with conn.cursor() as cursor:
                        # 資料表相關操
                        sql = "INSERT INTO weather(time_code,hour,city,temperature,wind_direction,wind_scale,precipitation,relative_temperature,air_quality) VALUES ('" + str(
                            Now) + "', '" + str(temp[1]) + "',  '" + str(temp[2]) + "',  '" + str(temp[3]) + "',  '" + str(temp[4]) + "',  '" + str(temp[5]) + "',  '" + str(temp[6]) + "', '" + str(temp[7]) + "', '" + str(temp[8]) + "')"
                        cursor.execute(sql)
                        conn.commit()
            except Exception as ex:
                    print("f")
        count = count+1
    ul = data.find('ul')
    li = ul.find_all('li')
    i=0
    for day in li:
        if i<7 and i>0:
            temp = []
            date = day.find('h1').string
            date = date[0:date.index('日')]
            temp.append(date)
            inf = day.find_all('p')
            temp.append(inf[0].string)

            tem_low = inf[1].find('i').string

            if inf[1].find('span') is None:
                tem_high = None
            else:
                tem_high = inf[1].find('span').string
            temp.append(tem_low[:-1])
            if tem_high[-1] == '(':
                temp.append(tem_high[:-1])
            else:
                temp.append(tem_high)

            wind = inf[2].find_all('span')
            for j in wind:
                temp.append(j['title'])

            wind_scale = inf[2].find('i').string
            index1 = wind_scale.index('级')
            temp.append(int(wind_scale[index1-1:index1]))
            final.append(temp)
        i = i+1
    return final_day,final


def job():
    for city_code in citycode_lists:
        city_code = list(city_code)
        citycode = city_code[1]
        cityname = city_code[0]
        url1='http://www.weather.com.cn/weather/'+citycode+'.shtml'
        html1 = getHTMLtext(url1)
        data1, data1_7 = get_content(html1, cityname)
schedule.every().day.at("17:14").do(job)
while True:
    schedule.run_pending()
    time.sleep(1)

def write_to_csv(file_name, data, day=14):
    with open (file_name,'a',errors='ignore', newline='') as f:
        if day == 14:
            header = ['日期','城市','天氣','最低氣溫','最高氣溫','風向1','風向2','風級']
        else:
            header = ['小時','城市','溫度','風力方向','風級','降水量','相對溫度','空氣質量']
        a = csv.writer(f)
        a.writerow(header)
        a.writerows(data)
write_to_csv('weather.csv',data_all,1)

region = {"db","hd","hz","hn","xb","xn","gat"}
url2 = 'http://www.weather.com.cn/textFC/'+region+'.shtml'
cithcodelist = getHTMLtext(url2)


