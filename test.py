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

import pyaudio 
import speech_recognition as sr

from PIL import Image, ImageTk
from contextlib import contextmanager
from googlefinance import getQuotes

LOCALE_LOCK = threading.Lock()

#540x960
window_width = 540
window_height = 960
window_x = 400
window_y = 150
dynamic_frame_w = 500
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

def pil2qpixmap(pil_image):
    w, h = pil_image.size
    data = pil_image.tobytes("raw", "RGBX")
    qimage = QImage(data, w, h, QImage.Format_RGB888)
    qpixmap = QPixmap(w,h)
    pix = QPixmap.fromImage(qimage)
    return pix

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
            print 'getting weather'
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
            temperature2 = "%s%s" % (str(int(weather_obj['currently']['temperature'])), degree_sign)
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
                    #image = Image.open(icon2)
                    #image = image.resize((100, 100), Image.ANTIALIAS)
                    #image = image.convert('RGB')
                    #photo = ImageTk.PhotoImage(image)
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



class Stocks(QFrame):
    def __init__(self, parent, *args, **kwargs):
        super(Stocks, self).__init__()
        self.initUI()

    def initUI(self):

        self.heading = QLabel('Stock Market')
        self.heading.setAlignment(Qt.AlignCenter)
        self.heading.setFont(font2)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.heading)

        self.fbox = QFormLayout()
        self.fbox.setSpacing(10)
        self.fbox.setAlignment(Qt.AlignLeft)
        self.stockLbl = QLabel('Stocks')
        self.priceLbl = QLabel('Current Price')
        self.stockLbl.setFont(font1)
        self.priceLbl.setFont(font1)
        self.fbox.addRow(self.stockLbl,self.priceLbl)
        self.stockNames = ['SENSEX','NIFTY', 'RELIANCE','ITC','TCS']
        self.update_stocks()
                
        self.vbox.addLayout(self.fbox)
        self.setLayout(self.vbox)

    def update_stocks(self):
        for i,stock in enumerate(self.stockNames):
            stkLbl = QLabel(stock)
            data  = getQuotes(stock)
            prcLbl = QLabel(data[0]['LastTradePrice'])
            stkLbl.setFont(font1)
            prcLbl.setFont(font1)
            self.fbox.addRow(stkLbl,prcLbl)



class Events(QFrame):
    def __init__(self, parent, *args, **kwargs):
        super(Events, self).__init__()
        self.initUI()

    def initUI(self):

        self.heading = QLabel('Todays\'s Events')
        self.heading.setAlignment(Qt.AlignCenter)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.heading)
        self.setLayout(self.vbox)



class Maps(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(Maps, self).__init__()
        self.initUI()

    def initUI(self):
        self.style = "style=element:geometry%7Ccolor:0x1d2c4d&style=element:labels.text.fill%7Ccolor:0x8ec3b9&style=element:labels.text.stroke%7Ccolor:0x1a3646&style=feature:administrative.country%7Celement:geometry.stroke%7Ccolor:0x4b6878&style=feature:administrative.land_parcel%7Celement:labels.text.fill%7Ccolor:0x64779e&style=feature:administrative.province%7Celement:geometry.stroke%7Ccolor:0x4b6878&style=feature:landscape.man_made%7Celement:geometry.stroke%7Ccolor:0x334e87&style=feature:landscape.natural%7Celement:geometry%7Ccolor:0x023e58&style=feature:poi%7Celement:geometry%7Ccolor:0x283d6a&style=feature:poi%7Celement:labels.text.fill%7Ccolor:0x6f9ba5&style=feature:poi%7Celement:labels.text.stroke%7Ccolor:0x1d2c4d&style=feature:poi.park%7Celement:geometry.fill%7Ccolor:0x023e58&style=feature:poi.park%7Celement:labels.text.fill%7Ccolor:0x3C7680&style=feature:road%7Celement:geometry%7Ccolor:0x304a7d&style=feature:road%7Celement:labels.text.fill%7Ccolor:0x98a5be&style=feature:road%7Celement:labels.text.stroke%7Ccolor:0x1d2c4d&style=feature:road.highway%7Celement:geometry%7Ccolor:0x2c6675&style=feature:road.highway%7Celement:geometry.stroke%7Ccolor:0x255763&style=feature:road.highway%7Celement:labels.text.fill%7Ccolor:0xb0d5ce&style=feature:road.highway%7Celement:labels.text.stroke%7Ccolor:0x023e58&style=feature:transit%7Celement:labels.text.fill%7Ccolor:0x98a5be&style=feature:transit%7Celement:labels.text.stroke%7Ccolor:0x1d2c4d&style=feature:transit.line%7Celement:geometry.fill%7Ccolor:0x283d6a&style=feature:transit.station%7Celement:geometry%7Ccolor:0x3a4762&style=feature:water%7Celement:geometry%7Ccolor:0x0e1626&style=feature:water%7Celement:labels.text.fill%7Ccolor:0x4e6d70"
        self.size = "480x360"
        self.zoom = 15
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

                location2 = "%s, %s" % (location_obj['city'], location_obj['region_code'])

            
                self.url = "https://maps.googleapis.com/maps/api/staticmap?key=%s&center=%d,%d&zoom=%d&format=jpg&maptype=roadmap&%s&size=%s" %(google_map_api,lat,lon,self.zoom,self.style,self.size)
        
        else:
            location2 = ""
            self.url = "https://maps.googleapis.com/maps/api/staticmap?key=%s&center=%d,%d&zoom=%d&format=png&maptype=roadmap&%s&size=%s" %(google_map_api,latitude,longitude,self.zoom,self.style,self.size)
        

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



class Message(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(Message, self).__init__()
        self.initUI()

    def initUI(self):
        self.msgLbl=QLabel('Welcome Have A nice day!')
        self.msgLbl.setAlignment(Qt.AlignCenter)
        self.msgLbl.setFont(font2)
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.msgLbl)
        self.setLayout(self.hbox)

class DynamicFrame(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(DynamicFrame, self).__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(dynamic_frame_w,dynamic_frame_h)
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.update_check()

    
    def update_check(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dynamic_frame)
        self.timer.start(10000)


    def update_dynamic_frame(self):
        global recognised_speech
        if recognised_speech:
            print recognised_speech
            if "maps" in recognised_speech or "maths" in recognised_speech:
                for i in reversed(range(self.vbox.count())): 
                    self.vbox.itemAt(i).widget().setParent(None)
                
                self.map = Maps(QWidget())
                self.map.setFixedSize(dynamic_frame_w,dynamic_frame_h)
                self.vbox.addWidget(self.map)

       
    


class FullscreenWindow:

    def __init__(self, parent, *args, **kwargs):
        self.qt = QWidget()
        self.qt.resize(window_width, window_height)
        self.pal=QPalette()
        self.pal.setColor(QPalette.Background,Qt.black)
        self.pal.setColor(QPalette.Foreground,Qt.white)
        self.qt.setPalette(self.pal)
        # for wheather and clock

        self.qt.hbox1 = QHBoxLayout()
        self.qt.clock = Clock(QWidget())
        #self.qt.clock.setFrameShape(QFrame.StyledPanel)
        self.qt.weather = Weather(QWidget())
        #self.qt.weather.setFrameShape(QFrame.StyledPanel)
        self.qt.clock.setFixedHeight(150)
        self.qt.weather.setFixedHeight(150)

        
        self.qt.hbox1.addWidget(self.qt.weather)
        self.qt.hbox1.addStretch()
        self.qt.hbox1.addWidget(self.qt.clock)

        # for stocks
        self.qt.hbox2 = QHBoxLayout()
        self.qt.Stocksframe = QFrame()
        self.qt.Stocksframe.setFrameShape(QFrame.StyledPanel)
        self.qt.stocks = Stocks(self.qt.Stocksframe)
        self.qt.hbox2.addStretch(2)
        self.qt.hbox2.addWidget(self.qt.stocks)

        # for calender event
        self.qt.hbox3 = QHBoxLayout()
        self.qt.Eventframe = QFrame()
        self.qt.events = Events(self.qt.Eventframe)
        self.qt.Eventframe.setFrameShape(QFrame.StyledPanel)
        self.qt.hbox3.addStretch(2)
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
        self.qt.Quotesframe = QFrame()
        self.qt.Quotesframe.setFrameShape(QFrame.StyledPanel)
        self.qt.hbox6.addWidget(self.qt.Quotesframe)


        self.qt.vbox = QVBoxLayout()
        self.qt.vbox.addLayout(self.qt.hbox1)
        self.qt.vbox.addLayout(self.qt.hbox2)
        self.qt.vbox.addLayout(self.qt.hbox3)
        self.qt.vbox.addLayout(self.qt.hbox4)
        self.qt.vbox.addLayout(self.qt.hbox5)
        # self.qt.vbox.addLayout(self.qt.hbox6)

        self.qt.setLayout(self.qt.vbox)
        self.qt.show()
      


def start_qt(tmp):
    a = QApplication(sys.argv)
    w = FullscreenWindow(a)
    sys.exit(a.exec_())



def start_speech_recording(tmp): 
# Record Audio
    global recognised_speech 
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            r.adjust_for_ambient_noise(source, duration = 1)
            audio = r.listen(source)
        
        try:
            recognised_speech = r.recognize_google(audio)
            print("You said: " + r.recognize_google(audio))
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

if __name__ == '__main__':

    try:
        #thread.start_new_thread( start_video_recording, (1, ) )
        thread.start_new_thread( start_speech_recording, (1, ) )
        thread.start_new_thread( start_qt, (2, ) )

    except Exception as e:
        print "Error: unable to start thread"
        print e

    while 1:
       pass  
        