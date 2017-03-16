import datetime
import json
import requests
import urllib
class Quotes():
    def __init__():
        super(Quotes, self).__init__()
        self.initUI()

    def initUI(self):
        self.hbox = QHboxLayout()
        self.hbox.addWidget()
        self.setLayout(self.hbox)
        self.quotes_get()

    def data_fetch(url):
        url = requests.urlopen(url)
        output = url.read().decode('utf-8')
        quotes_obj_req = json.loads(output)
        url.close()
        return quotes_obj_req

    def data_get(quotes_obj_req):
        quote_value=quotes_obj_req["quoteText"]
        quote_Author = quotes_obj_req["quoteAuthor"]
        print(quote_value)
        print(quote_Author)
        
    def quotes_get(self):
        try:
            url= 'http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en'
            print data_get(data_fetch(url))
        except IOError:
            print('no internet')

quotes = Quotes()
