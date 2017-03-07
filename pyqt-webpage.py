import sys
from PyQt4.QtCore import QSize, Qt
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

html = \
"""<!DOCTYPE html>
<html>
  <head>
    <style>
       #map {
        height: 400px;
        width: 100%;
       }
    </style>
  </head>
  <body>
    <h3>My Google Maps Demo</h3>
    <div id="map"></div>
    <script>
      function initMap() {
        var uluru = {lat: -25.363, lng: 131.044};
        var map = new google.maps.Map(document.getElementById('map'), {
          zoom: 4,
          center: uluru
        });
        var marker = new google.maps.Marker({
          position: uluru,
          map: map
        });
      }
    </script>
    <script async defer
    src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCJBH3iAhxajblBN8g7-XAAE13WV4mNPBM&callback=initMap">
    </script>
  </body>
</html>
"""

class WebWidget(QWidget):

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(Qt.white)
        painter.setPen(Qt.black)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        painter.setBrush(Qt.red)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.width()/4, self.height()/4,
                         self.width()/2, self.height()/2)
        painter.end()
    
    def sizeHint(self):
        return QSize(100, 100)

class WebPluginFactory(QWebPluginFactory):

    def __init__(self, parent = None):
        QWebPluginFactory.__init__(self, parent)
    
    def create(self, mimeType, url, names, values):
        if mimeType == "x-pyqt/widget":
            return WebWidget()
    
    def plugins(self):
        plugin = QWebPluginFactory.Plugin()
        plugin.name = "PyQt Widget"
        plugin.description = "An example Web plugin written with PyQt."
        mimeType = QWebPluginFactory.MimeType()
        mimeType.name = "x-pyqt/widget"
        mimeType.description = "PyQt widget"
        mimeType.fileExtensions = []
        plugin.mimeTypes = [mimeType]
        print "plugins"
        return [plugin]    
        

if __name__ == "__main__":

    app = QApplication(sys.argv)
    QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True)
    view = QWebView()
    factory = WebPluginFactory()
    view.page().setPluginFactory(factory)
    view.setHtml(html)
    view.show()
    sys.exit(app.exec_())            