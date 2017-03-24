import sys
import os
import cv2

from PyQt4.QtCore import QSize, Qt
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

import locale
import threading
import time
import requests
import json
import traceback
import urllib2
import feedparser
import thread
import datetime
import string
import MySQLdb
import random
import urllib

import pyaudio 
import speech_recognition as sr
import imageUpload as imup
import MSFaceAPI as msface

from PIL import Image, ImageTk
from contextlib import contextmanager
from googlefinance import getQuotes

LOCALE_LOCK = threading.Lock()

#540x960
window_width = 540
window_height = 960
window_x = 400
window_y = 150
dynamic_frame_w = 600
dynamic_frame_h = 400
ip = '<IP>'
ui_locale = '' # e.g. 'fr_FR' fro French, '' as default
time_format = 12 # 12 or 24
date_format = "%b %d, %Y" # check python doc for strftime() for options
news_country_code = 'us'
weather_api_token = '87359f8bd52bb42beafca6b60132ef40' # create account at https://darksky.net/dev/
weather_lang = 'en' # see https://darksky.net/dev/docs/forecast for full list of language parameters values
weather_unit = 'us' # see https://darksky.net/dev/docs/forecast for full list of unit parameters values
latitude = None # Set this if IP location lookup does not work for you (must be a string)
longitude = None # Set this if IP location lookup does not work for you (must be a string)
xlarge_text_size = 48
large_text_size = 28
medium_text_size = 18
small_text_size = 10

base_path = os.path.dirname(os.path.realpath(__file__))
dataset_path = os.path.join(base_path,'dataset')
tmp_path = os.path.join(base_path,'tmp')

cloudinary_dataset = 'http://res.cloudinary.com/aish/image/upload/v1488457817/SmartMirror/dataset'
cloudinary_tmp = 'http://res.cloudinary.com/aish/image/upload/v1488457817/SmartMirror/tmp'
google_map_api = 'AIzaSyCOW4YsV4gl7tAowsyPw_9ocO8iGTKD8A8'

recognised_speech = ''
current_userid = 0
current_userfname = ''
today = datetime.datetime.now().strftime("%d-%m-%Y")

@contextmanager
def setlocale(name): #thread proof function to work with locale
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)

# maps open weather icons to
# icon reading is not impacted by the 'lang' parameter
icon_lookup = {
    'clear-day': "assets/Sun.png",  # clear sky day
    'wind': "assets/Wind.png",   #wind
    'cloudy': "assets/Cloud.png",  # cloudy day
    'partly-cloudy-day': "assets/PartlySunny.png",  # partly cloudy day
    'rain': "assets/Rain.png",  # rain day
    'snow': "assets/Snow.png",  # snow day
    'snow-thin': "assets/Snow.png",  # sleet day
    'fog': "assets/Haze.png",  # fog day
    'clear-night': "assets/Moon.png",  # clear sky night
    'partly-cloudy-night': "assets/PartlyMoon.png",  # scattered clouds night
    'thunderstorm': "assets/Storm.png",  # thunderstorm
    'tornado': "assests/Tornado.png",    # tornado
    'hail': "assests/Hail.png"  # hail
}

font1 = QFont('Helvetica', small_text_size)
font2 = QFont('Helvetica', medium_text_size)
font3 = QFont('Helvetica', large_text_size) 

conn = MySQLdb.connect("sql12.freesqldatabase.com","sql12163783","V1UcBAeFnq","sql12163783" )

TABLE_NAME="users"
cursor = conn.cursor()


class Weather(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(Weather, self).__init__()
        self.initUI()

    def initUI(self):
        font1 = QFont('Helvetica', small_text_size)
        font2 = QFont('Helvetica', medium_text_size)
        font3 = QFont('Helvetica', large_text_size)

        self.temperature = ''
        self.forecast = ''
        self.location = ''
        self.currently = ''
        self.icon = ''

        self.vbox= QVBoxLayout()
        self.temperatureLbl  = QLabel('Tepr')
        self.iconLbl = QLabel()
        self.currentlyLbl = QLabel('currently')
        self.forecastLbl = QLabel('forecast')
        self.locationLbl = QLabel('location')

        self.temperatureLbl.setFont(font3)
        self.currentlyLbl.setFont(font2)
        self.forecastLbl.setFont(font1)
        self.locationLbl.setFont(font1)

        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.vbox1 = QVBoxLayout()
        self.hbox.addWidget(self.temperatureLbl)
        self.hbox.addWidget(self.iconLbl)
        self.hbox.setAlignment(Qt.AlignLeft)
        self.vbox1.addWidget(self.currentlyLbl)
        self.vbox1.addWidget(self.forecastLbl)
        self.vbox1.addWidget(self.locationLbl)
        self.vbox1.addStretch(1)

        self.vbox.addLayout(self.hbox)
        self.vbox.addLayout(self.vbox1)
        self.vbox.setContentsMargins(0,0,0,0)
        self.setLayout(self.vbox)
        self.get_weather()
        self.weather_update()


    def weather_update(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.get_weather)
        self.timer.start(60000*60)



    def get_ip(self):
        try:
            ip_url = "http://jsonip.com/"
            req = requests.get(ip_url)
            ip_json = json.loads(req.text)
            return ip_json['ip']
        except Exception as e:
            traceback.print_exc()
            return "Error: %s. Cannot get ip." % e

    def get_weather(self):
        try:
            print 'Getting weather ......'
            if latitude is None and longitude is None:
                # get location
                location_req_url = "http://freegeoip.net/json/%s" % self.get_ip()
                r = requests.get(location_req_url)
                location_obj = json.loads(r.text)

                lat = location_obj['latitude']
                lon = location_obj['longitude']

                location2 = "%s, %s" % (location_obj['city'], location_obj['region_code'])

                # get weather
                weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, lat,lon,weather_lang,weather_unit)
            else:
                location2 = ""
                # get weather
                weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, latitude, longitude, weather_lang, weather_unit)

            r = requests.get(weather_req_url)
            weather_obj = json.loads(r.text)

            degree_sign= u'\N{DEGREE SIGN}'
            f = int(weather_obj['currently']['temperature'])
            c = int(5*(f-32)/9)
            temperature2 = "%s%s" % (str(c), degree_sign)
            currently2 = weather_obj['currently']['summary']
            forecast2 = weather_obj["hourly"]["summary"]

            icon_id = weather_obj['currently']['icon']
            icon2 = None

            if icon_id in icon_lookup:
                icon2 = icon_lookup[icon_id]

            if icon2 is not None:
                if self.icon != icon2:
                    self.icon = icon2
                    image = cv2.imread(icon2, cv2.CV_LOAD_IMAGE_COLOR);
                    image = cv2.resize(image,(50,50), interpolation = cv2.INTER_CUBIC)
                    image = QImage(image, image.shape[1], image.shape[0], 
                       image.strides[0], QImage.Format_RGB888)
        
                    #pix = pil2qpixmap(image)

                    self.iconLbl.setPixmap(QPixmap.fromImage(image))
            else:
                # remove image
                self.iconLbl.setPixmap(QPixmap(''))
                a=1

            if self.currently != currently2:
                print self.currently
                self.currently = currently2
                self.currentlyLbl.setText(currently2)
            if self.forecast != forecast2:
                self.forecast = forecast2
                self.forecastLbl.setText(forecast2)
            if self.temperature != temperature2:
                self.temperature = temperature2
                self.temperatureLbl.setText(temperature2)
            if self.location != location2:
                if location2 == ", ":
                    self.location = "Cannot Pinpoint Location"
                    self.locationLbl.setText("Cannot Pinpoint Location")
                else:
                    self.location = location2
                    self.locationLbl.setText(location2)
        except Exception as e:
            traceback.print_exc()
            print "Error: %s. Cannot get weather." % e


    @staticmethod
    def convert_kelvin_to_fahrenheit(kelvin_temp):
        return 1.8 * (kelvin_temp - 273) + 32


class Clock(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(Clock, self).__init__()
        self.initUI()

    def initUI(self):
        font1 = QFont('Helvetica', large_text_size)
        font2 = QFont('Helvetica', small_text_size)

        self.vbox= QVBoxLayout()
        self.time1 = ''
        self.timeLbl = QLabel('')
        self.timeLbl.setAlignment(Qt.AlignRight)
        self.timeLbl.setFont(font1)
        self.day_of_week1 = ''
        self.dayOWLbl = QLabel('')
        self.dayOWLbl.setAlignment(Qt.AlignRight)
        self.date1 = ''
        self.dateLbl = QLabel('')
        self.dateLbl.setAlignment(Qt.AlignRight)
        self.vbox.addWidget(self.timeLbl)
        self.vbox.addWidget(self.dayOWLbl)
        self.vbox.addWidget(self.dateLbl)
        self.vbox.addStretch(2)
        self.vbox.setSpacing(0)
        self.setContentsMargins(0,0,0,0)
        self.setLayout(self.vbox)
        self.time_update()

    def time_update(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(200)


    def tick(self):
        with setlocale(ui_locale):
            if time_format == 12:
                time2 = time.strftime('%I:%M %p') #hour in 12h format
            else:
                time2 = time.strftime('%H:%M') #hour in 24h format

            day_of_week2 = time.strftime('%A')
            date2 = time.strftime(date_format)
            # if time string has changed, update it
            if time2 != self.time1:
                self.time1 = time2
                self.timeLbl.setText(time2)
            if day_of_week2 != self.day_of_week1:
                self.day_of_week1 = day_of_week2
                self.dayOWLbl.setText(day_of_week2)
            if date2 != self.date1:
                self.date1 = date2
                self.dateLbl.setText(date2)


class Stocks(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(Stocks, self).__init__()
        self.prev_userid = -1
        self.initUI()

    def initUI(self):
        
        self.heading = QLabel('Stocks Today')
        self.heading.setAlignment(Qt.AlignLeft)
        self.heading.setFont(font2)
        
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.heading)
        self.vbox.setAlignment(Qt.AlignTop)

        self.fbox = QFormLayout()
        self.fbox.setSpacing(10)
        self.fbox.setAlignment(Qt.AlignLeft)
        
        self.stockLbl = QLabel('Stocks')
        self.priceLbl = QLabel('Current Price (Rs.)')
        self.stockLbl.setFont(font1)
        self.priceLbl.setFont(font1)
        
        self.fbox.addRow(self.stockLbl,self.priceLbl)
        self.stockNames = ['SENSEX','NIFTY', 'RELIANCE','ITC','TCS']
        
        self.update_check()        
        self.vbox.addLayout(self.fbox)
        self.setLayout(self.vbox)

    def update_check(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stocks)
        self.timer.start(500)    
    
    def update_stocks(self):
        global current_userid
        
        if self.prev_userid != current_userid:
            

            for i in reversed(range(self.fbox.count())): 
                self.fbox.itemAt(i).widget().setParent(None)
                
            self.prev_userid = current_userid
            
            if (current_userid != 0):
                sql_command = " SELECT * from stocks where userid = %s " % current_userid 
                cursor.execute(sql_command)
                self.obj = cursor.fetchall()
            
                self.stockNames = []
            
                for i,stock in enumerate(self.obj):
                    self.stockNames.append(stock[2])
            
            else:
                self.stockNames = ['SENSEX','NIFTY', 'RELIANCE','ITC','TCS']

            for i,stock in enumerate(self.stockNames):
                stkLbl = QLabel(str(stock))
                data  = getQuotes(stock)
                prcLbl = QLabel(data[0]['LastTradePrice'])
                stkLbl.setFont(font1)
                prcLbl.setFont(font1)
                self.fbox.addRow(stkLbl,prcLbl)



class Events(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(Events, self).__init__()
        self.prev_userid = -1
        self.initUI()

    def initUI(self):

        self.heading = QLabel("Today's Events")
        self.heading.setAlignment(Qt.AlignLeft)
        self.heading.setFont(font2)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.heading)
        self.vbox.setAlignment(Qt.AlignTop)
        
        self.fbox = QFormLayout()
        self.fbox.setSpacing(10)
        self.fbox.setAlignment(Qt.AlignLeft)
        
        self.eventLbl = QLabel('Events')
        self.timeLbl = QLabel('Time')
        self.eventLbl.setFont(font1)
        self.timeLbl.setFont(font1)
        
        self.fbox.addRow(self.eventLbl,self.timeLbl)
        
        self.eventNames = []
        self.eventTime = []
        self.noEventLbl = QLabel('No Event Today')

        self.update_check()

        self.vbox.addLayout(self.fbox)
        self.setLayout(self.vbox)

    
    def update_check(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_events)
        self.timer.start(500)

    def update_events(self):
        global current_userid
        if self.prev_userid != current_userid:
            
            for i in reversed(range(self.fbox.count())): 
                self.fbox.itemAt(i).widget().setParent(None)
            
            self.prev_userid = current_userid

            if (current_userid != 0):

                sql_command = """ SELECT * from events where userid = %s  """ % current_userid
                params = (current_userid)
                cursor.execute(sql_command)
                self.obj = cursor.fetchall()
                self.eventNames = []
                self.eventTime = []
                
                for i,event in enumerate(self.obj):
                        self.eventNames.append(event[2])
                        self.eventTime.append(event[4])
             
                for i,event in enumerate(self.eventNames):
                    
                    eventLbl = QLabel(str(event))
                    timeLbl = QLabel(':'.join(str(self.eventTime[i]).split(':')[:2]))
                    eventLbl.setFont(font1)
                    timeLbl.setFont(font1)
                    self.fbox.addRow(eventLbl, timeLbl)

            if (current_userid == 0):
                self.fbox.addRow(self.noEventLbl)
       


class News(QWidget):
    def __init__(self, source=None):
        super(News, self).__init__()
        # source
        if source:
          self.source = source
        else:
          # self.source = 'the-times-of-india'      
          self.source = 'the-times-of-india'      
      
        self.initUI()

    def initUI(self):
        
        self.vbox = QVBoxLayout()
        self.heading = QLabel()
        
        self.size= "480x360"

        
        #self.source="the-times-of-india"
        self.fbox = QFormLayout()
        self.fbox.setAlignment(Qt.AlignLeft)
        self.fbox.setSpacing(8)

        self.heading.setAlignment(Qt.AlignCenter)
        self.heading.setFont(font2)
        
        self.vbox.addWidget(self.heading)
        self.vbox.addLayout(self.fbox)
        
        self.setLayout(self.vbox)
        self.news_fetcher()
        #self.addWidget(News)
        

    #updating news
    def news_fetcher(self):
        
        try:
            
            news_req_url = "https://newsapi.org/v1/articles?source=%s&sortBy=latest&apiKey=15f23ada1b3d4740b80a2e4c16943993" % self.source
            # print news_req_url
            r = requests.get(news_req_url)
            news_obj = json.loads(r.text)
            
            # print news_obj
            
            data0=news_obj["articles"][0]["title"]
            data1=news_obj["articles"][1]["title"]
            data2=news_obj["articles"][2]["title"]
            data3=news_obj["articles"][3]["title"]
            data4=news_obj["articles"][4]["title"]

          
            data_read = [data0,data1,data2,data3,data4]

            #print data_read
            for i in reversed(range(self.fbox.count())): 
                    self.fbox.itemAt(i).widget().setParent(None)
                
            for (i,x) in enumerate(data_read):
                #INDIA
                image = cv2.imread("assets/Newspaper.png", cv2.CV_LOAD_IMAGE_COLOR);
                image = cv2.resize(image,(25,25), interpolation = cv2.INTER_CUBIC)
                image = QImage(image, image.shape[1], image.shape[0], 
                       image.strides[0], QImage.Format_RGB888)
                newspaperIcon = QLabel()
                newspaperIcon.setPixmap(QPixmap.fromImage(image))

                if self.source == 'the-times-of-india':
                    lbl = QLabel(x)
                    lbl.setWordWrap(True)
                    lbl.setFont(font1)
                    self.fbox.addRow(newspaperIcon,lbl)
                    self.heading.setText('HEADLINES')
                    
                # Sports News
                elif self.source == 'fox-sports':
                    lbl = QLabel(x)
                    lbl.setWordWrap(True)
                    self.fbox.addRow(newspaperIcon,lbl)
                    self.heading.setText('SPORTS NEWS')
                    
                # Tech News
                elif self.source == 'techcrunch':
                    lbl = QLabel(x)
                    lbl.setWordWrap(True)
                    self.fbox.addRow(newspaperIcon,lbl)
                    self.heading.setText('TECHNOLOGY NEWS')
                   
                #WORLD
                elif self.source == 'the-telegraph':
                    lbl = QLabel(x)
                    lbl.setWordWrap(True)
                    self.fbox.addRow(newspaperIcon,lbl)
                    self.heading.setText('WORLD NEWS')
                   
                # Business
                elif self.source == 'business-insider':
                    lbl = QLabel(x)
                    lbl.setWordWrap(True)
                    self.fbox.addRow(newspaperIcon,lbl)
                    self.heading.setText('BUSINESS NEWS')
                    

        except IOError:
            print('no internet')



class Maps(QWidget):
    def __init__(self, zoom=None):
        super(Maps, self).__init__()
        
        if zoom:
            self.zoom = zoom
        else:
            self.zoom = 15
        self.initUI()

    def initUI(self):
        self.style = "style=element:geometry%7Ccolor:0x1d2c4d&style=element:labels.text.fill%7Ccolor:0x8ec3b9&style=element:labels.text.stroke%7Ccolor:0x1a3646&style=feature:administrative.country%7Celement:geometry.stroke%7Ccolor:0x4b6878&style=feature:administrative.land_parcel%7Celement:labels.text.fill%7Ccolor:0x64779e&style=feature:administrative.province%7Celement:geometry.stroke%7Ccolor:0x4b6878&style=feature:landscape.man_made%7Celement:geometry.stroke%7Ccolor:0x334e87&style=feature:landscape.natural%7Celement:geometry%7Ccolor:0x023e58&style=feature:poi%7Celement:geometry%7Ccolor:0x283d6a&style=feature:poi%7Celement:labels.text.fill%7Ccolor:0x6f9ba5&style=feature:poi%7Celement:labels.text.stroke%7Ccolor:0x1d2c4d&style=feature:poi.park%7Celement:geometry.fill%7Ccolor:0x023e58&style=feature:poi.park%7Celement:labels.text.fill%7Ccolor:0x3C7680&style=feature:road%7Celement:geometry%7Ccolor:0x304a7d&style=feature:road%7Celement:labels.text.fill%7Ccolor:0x98a5be&style=feature:road%7Celement:labels.text.stroke%7Ccolor:0x1d2c4d&style=feature:road.highway%7Celement:geometry%7Ccolor:0x2c6675&style=feature:road.highway%7Celement:geometry.stroke%7Ccolor:0x255763&style=feature:road.highway%7Celement:labels.text.fill%7Ccolor:0xb0d5ce&style=feature:road.highway%7Celement:labels.text.stroke%7Ccolor:0x023e58&style=feature:transit%7Celement:labels.text.fill%7Ccolor:0x98a5be&style=feature:transit%7Celement:labels.text.stroke%7Ccolor:0x1d2c4d&style=feature:transit.line%7Celement:geometry.fill%7Ccolor:0x283d6a&style=feature:transit.station%7Celement:geometry%7Ccolor:0x3a4762&style=feature:water%7Celement:geometry%7Ccolor:0x0e1626&style=feature:water%7Celement:labels.text.fill%7Ccolor:0x4e6d70"
        self.size = "480x360"
        #print self.zoom
        #self.zoom = 15
        self.mapLbl=QLabel()
        self.mapLbl.setAlignment(Qt.AlignCenter)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.mapLbl)
        self.setLayout(self.vbox)
        self.show_map()



    def get_ip(self):
        try:
            ip_url = "http://jsonip.com/"
            req = requests.get(ip_url)
            ip_json = json.loads(req.text)
            return ip_json['ip']
        except Exception as e:
            traceback.print_exc()
            return "Error: %s. Cannot get ip." % e 
                
    def show_map(self):
        if latitude is None and longitude is None:
                # get location
                location_req_url = "http://freegeoip.net/json/%s" % self.get_ip()
                r = requests.get(location_req_url)
                location_obj = json.loads(r.text)

                lat = location_obj['latitude']
                lon = location_obj['longitude']
                print ("%.10f,%.10f")%(lat,lon)

                location2 = "%s, %s" % (location_obj['city'], location_obj['region_code'])

            
                self.url = "https://maps.googleapis.com/maps/api/staticmap?key=%s&center=%f,%f&zoom=%d&format=png&maptype=roadmap&%s&size=%s" %(google_map_api,lat,lon,self.zoom,self.style,self.size)
        
        else:
            location2 = ""
            self.url = "https://maps.googleapis.com/maps/api/staticmap?key=%s&center=%f,%f&zoom=%d&format=png&maptype=roadmap&%s&size=%s" %(google_map_api,latitude,longitude,self.zoom,self.style,self.size)
        

        #print self.url  
        req = urllib2.Request(self.url)
        res = urllib2.urlopen(req)
        data= res.read()

        image = QImage()
        image.loadFromData(data)      
        self.mapLbl.setPixmap(QPixmap(image))        

class Directions(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(Directions, self).__init__()
        self.initUI()

    def initUI(self):

        self.web_view = QWebView()

        self.origin = 'Oslo+Norway'
        self.destination = 'Telemark+Norway'
        self.api_key = 'AIzaSyBHq3ygPUhqbjSUFW5E3FMqfagMiStkYFc'
        self.api_base = 'https://www.google.com/maps/embed/v1/directions'
        self.vbox = QVBoxLayout()

        self.vbox.addWidget(self.web_view)

        self.setLayout(self.vbox)
        self.show_directions()

    def show_directions(self):

        self.url = self.api_base + '?key=%s&origin=%s&destination=%s'%(self.api_key,self.origin,self.destination)
        self.html = '''<iframe src="%s" height="%d" width="%d"></iframe>''' %(self.url,dynamic_frame_h,dynamic_frame_w)
        self.web_view.setHtml(self.html)

class Calendar(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(Calendar, self).__init__()
        self.initUI()

    def initUI(self):
        self.vbox = QVBoxLayout()
        self.cal = QCalendarWidget()
        self.cal.setGridVisible(True)
        self.vbox.addWidget(self.cal)
        self.setLayout(self.vbox) 




class Message(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(Message, self).__init__()
        self.initUI()

    def initUI(self):
        self.msgLbl=QLabel('Welcome Have A nice day!')
        self.msgLbl.setAlignment(Qt.AlignCenter)
        self.msgLbl.setFont(font2)
        self.hbox = QHBoxLayout()
        self.fname = ''
        self.hbox.addWidget(self.msgLbl)
        self.setLayout(self.hbox)
        self.update_check()


    def update_check(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_message)
        self.timer.start(500)

    def update_message(self):
        global current_userfname 
        if current_userfname!=self.fname:
            self.msgLbl.setText('Welcome %s! Have A nice day!' % current_userfname)

class Quotes(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(Quotes, self).__init__()
        self.initUI()

    def initUI(self):
        self.vbox = QVBoxLayout()
        self.lbl1 = QLabel()
        self.lbl1.setWordWrap(True)
        self.lbl2 = QLabel()
        self.lbl1.setAlignment(Qt.AlignCenter)
        self.lbl2.setAlignment(Qt.AlignCenter)
        self.vbox.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.lbl1)
        self.vbox.addWidget(self.lbl2)
        self.setLayout(self.vbox)
        self.quotes_get()

        
    def quotes_get(self):
        try:
            url= 'http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en'
            res = requests.get(url)
            # print res
            s = res.text
            s.replace('\r\n', '')
            s.replace("\'", "'")
            data = json.loads(s)
            self.lbl1.setText(data["quoteText"])
            self.lbl2.setText("- " + data["quoteAuthor"])
            # print data
            #print self.data_get(self.data_fetch(url))
        except IOError:
            print('no internet')



class DynamicFrame(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(DynamicFrame, self).__init__()
        self.initUI()
        self.prev_recorded_speech = ''
        self.zoom = 15
        self.map_keys = ["maps","maths"]
        self.cal_keys = ["calendar","calender"]
        self.news_keys = ["news","muse","tech","sports","business","india","world","nude"]

    def initUI(self):
        self.setFixedSize(dynamic_frame_w,dynamic_frame_h)
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.update_check()
        # self.map = Maps(15)
        # self.map.setFixedSize(dynamic_frame_w,dynamic_frame_h)
        # self.vbox.addWidget(self.map)
        self.news = News('the-times-of-india') 
        self.news.setFixedSize(dynamic_frame_w,dynamic_frame_h)
        self.vbox.addWidget(self.news)
        # self.cal = Calendar(QWidget())
        # self.cal.setFixedSize(dynamic_frame_w,dynamic_frame_h)
        # self.vbox.addWidget(self.cal)       


    
    def update_check(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dynamic_frame)
        self.timer.start(500)


    def update_dynamic_frame(self):
        global recognised_speech
        if recognised_speech != self.prev_recorded_speech:
            
            print recognised_speech
            
            self.prev_recorded_speech = recognised_speech

            if "maps" in recognised_speech or "maths" in recognised_speech or "map" in recognised_speech:
                print "showing map"
                self.zoom = 15
                for i in reversed(range(self.vbox.count())): 
                    self.vbox.itemAt(i).widget().setParent(None)
                
                self.map = Maps(self.zoom)
                self.map.setFixedSize(dynamic_frame_w,dynamic_frame_h)
                self.vbox.addWidget(self.map)

            if "zoom in" in recognised_speech or "in" in recognised_speech:
                self.zoom = self.zoom + 1
                print "zooming in"
                if hasattr(self, 'map'):
                    if self.map.parent():
                        for i in reversed(range(self.vbox.count())): 
                            self.vbox.itemAt(i).widget().setParent(None)
                        
                        self.map = Maps(self.zoom)
                        self.map.setFixedSize(dynamic_frame_w,dynamic_frame_h)
                        self.vbox.addWidget(self.map)

            if "zoom out" in recognised_speech or "out" in recognised_speech:
                self.zoom = self.zoom - 1
                print "zooming out"
                if hasattr(self, 'map'):
                    if self.map.parent():
                        for i in reversed(range(self.vbox.count())): 
                            self.vbox.itemAt(i).widget().setParent(None)
                        
                        self.map = Maps(self.zoom)
                        self.map.setFixedSize(dynamic_frame_w,dynamic_frame_h)
                        self.vbox.addWidget(self.map)
                               

            if "calendar" in recognised_speech or "calender" in recognised_speech:
                print "showing calender"
                for i in reversed(range(self.vbox.count())): 
                    self.vbox.itemAt(i).widget().setParent(None)
                
                self.cal = Calendar(QWidget())
                self.cal.setFixedSize(dynamic_frame_w,dynamic_frame_h)
                self.vbox.addWidget(self.cal)
            if any(x in recognised_speech for x in self.news_keys):
                print "showing news"
                for i in reversed(range(self.vbox.count())): 
                    self.vbox.itemAt(i).widget().setParent(None)
                
                if "tech" in recognised_speech:                 
                    self.news = News('techcrunch')

                elif "business" in recognised_speech or "bizness" in recognised_speech:
                    self.news = News('business-insider')

                elif "sport" in recognised_speech or "spot" in recognised_speech or "sports" in recognised_speech:
                    self.news = News('fox-sports')

                elif "world" in recognised_speech or "word" in recognised_speech:
                    self.news = News('the-telegraph')

                else:
                    self.news = News('the-times-of-india')                                    

                self.news.setFixedSize(dynamic_frame_w,dynamic_frame_h)
                self.vbox.addWidget(self.news)



class FullscreenWindow:

    def __init__(self, parent, *args, **kwargs):
        self.qt = QWidget()
        self.qt.showFullScreen()
        # self.qt.resize(window_width, window_height)

        self.pal=QPalette()
        self.pal.setColor(QPalette.Background,Qt.black)
        self.pal.setColor(QPalette.Foreground,Qt.white)
        self.qt.setPalette(self.pal)
        # for wheather and clock

        self.qt.hbox1 = QHBoxLayout()
        self.qt.clock = Clock(QWidget())
        self.qt.weather = Weather(QWidget())
        self.qt.clock.setFixedHeight(150)
        self.qt.weather.setFixedHeight(150)

        
        self.qt.hbox1.addWidget(self.qt.weather)
        self.qt.hbox1.addStretch()
        self.qt.hbox1.addWidget(self.qt.clock)

        # for stocks
        self.qt.hbox2 = QHBoxLayout()
        self.qt.stocks = Stocks(QWidget())
        self.qt.stocks.setFixedWidth(200)
        self.qt.hbox2.addStretch(2)
        self.qt.hbox2.addWidget(self.qt.stocks)

        # for calender event
        self.qt.hbox3 = QHBoxLayout()
        self.qt.hbox3.addStretch(2)
        self.qt.events = Events(QWidget())
        self.qt.events.setFixedWidth(200)
        self.qt.hbox3.addWidget(self.qt.events)

        #dynamic area

        self.qt.hbox4 = QHBoxLayout()
        self.qt.Dynamicframe = DynamicFrame(QWidget())
        self.qt.hbox4.addWidget(self.qt.Dynamicframe)

        # message area
        self.qt.hbox5 = QHBoxLayout()
        self.qt.messageBox = Message(QWidget())
        self.qt.hbox5.addWidget(self.qt.messageBox)

        # quotes area
        self.qt.hbox6 = QHBoxLayout()
        self.qt.quotes = Quotes(QWidget())
        self.qt.hbox6.addWidget(self.qt.quotes)


        self.qt.vbox = QVBoxLayout()
        self.qt.vbox.addLayout(self.qt.hbox1)
        self.qt.vbox.addLayout(self.qt.hbox2)
        self.qt.vbox.addLayout(self.qt.hbox3)
        self.qt.vbox.addStretch(2)
        self.qt.vbox.addLayout(self.qt.hbox4)
        
        self.qt.vbox.addLayout(self.qt.hbox5)
        self.qt.vbox.addLayout(self.qt.hbox6)

        self.qt.setLayout(self.qt.vbox)
        
        # self.qt.setWindowState(Qt.WindowMaximized)
        # self.qt.showMaximized()



def start_qt(tmp):
    a = QApplication(sys.argv)
    w = FullscreenWindow(a)
    sys.exit(a.exec_())

def id_generator(size=20, chars=string.ascii_lowercase + string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

def face_identify(tmp):

    global current_userid
    global current_userfname

    detected_personid = ''
    camera_port = 1
    cascPath = 'haarcascade_frontalface_default.xml'
    faceCascade = cv2.CascadeClassifier(cascPath)
    
    ramp_frames = 10
    
    print "Face identification started .........."
    cam = cv2.VideoCapture(camera_port) 
    try:
        
        while True:
            for i in xrange(ramp_frames):
                s, im = cam.read()   

            ret,image = cam.read()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100),
                flags=cv2.cv.CV_HAAR_SCALE_IMAGE
            )
            
            # Draw a rectangle around the faces
            max_area = 0
            mx = 0
            my = 0 
            mh = 0 
            mw = 0
            for (x, y, w, h) in faces:
                #cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                if w*h > max_area:
                    mx = x
                    my = y
                    mh = h
                    mw = w
                    max_area=w*h

            #cv2.imshow('Video', image)
            if max_area>=15000:        
                image_crop = image[my:my+mh,mx:mx+mw]
                file_name = id_generator()+'.jpg'
                file = os.path.join(tmp_path,file_name)
                cloudinary_url=cloudinary_tmp + '/' + file_name        
                cv2.imwrite(file, image_crop)
                imup.upload_image(file,file_name)
                
                faceid=msface.face_detect(cloudinary_url)
                
                print "faceId = " + str(faceid)
                detected_personid = msface.face_identify(faceid)
                print "detected_personid = " + str(detected_personid)
            
            else:
                continue    

                
            if detected_personid:
                comm = "SELECT * FROM users WHERE personid = '%s'" % detected_personid
                res = cursor.execute(comm)
                res = cursor.fetchone()
                if res:
                    current_userid = res[0]
                    current_userfname = res[2]
                    fname = res[2]
                    print "Welcome %s !" % fname
                    return

                else:
                    print "person id not found in database"

            
            else:
                print "Unknown person found"
                                   
    except Exception as e:
        print "Errors occured !"
        print e    

    cam.release()
    cv2.destroyAllWindows() 




def start_speech_recording(tmp): 
# Record Audio
    global recognised_speech
    BING_KEY = "cfee7d6db79d4671b9cea936da4689d7" 
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            r.adjust_for_ambient_noise(source, duration = 1)
            audio = r.listen(source)
        
        try:
            recognised_speech = r.recognize_bing(audio, key=BING_KEY).lower()
            print("Microsoft Bing Voice Recognition thinks you said:" + recognised_speech)
            if "hallo" in recognised_speech or "wakeup" in recognised_speech or "start" in recognised_speech or "makeup" in recognised_speech or "star" in recognised_speech or "breakup" in recognised_speech:
                thread.start_new_thread( face_identify, (3, ) )       
        except sr.UnknownValueError:
            print("Microsoft Bing Voice Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))





if __name__ == '__main__':

    try:
        
        thread.start_new_thread( start_qt, (1, ) )
        thread.start_new_thread( start_speech_recording, (2, ) )
        thread.start_new_thread( face_identify, (3, ) )

        

    except Exception as e:
        print "Error: unable to start thread"
        print e

    while 1:
       pass  
