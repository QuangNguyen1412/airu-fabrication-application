##############################################################
# Name: htmlReader.py
# Description: HtmlReaderClass is made to interact with the google drive where we store binaries and download them
# firmware version, PM sensors and more importantly to show the pair of AirU board and PM sensor
# Author: Quang Nguyen
# Author Email: ntdquang1412@gmail.com
# Date: June 12th, 2019
# Google Sheets API v4.
# client email: airudevicemanager@airudevicemanager.iam.gserviceaccount.com
# AirU https://docs.google.com/spreadsheets/d/1eFpUv7EhIoQ9ztsbGeJe5pxPL9lmTTv1u2OkCFY9Z7E/edit?usp=sharing
# Tetrad https://docs.google.com/spreadsheets/d/1lNxwm1XUpYNcJIXxaP1tOduslou_lqlG9EJgXM6Dhdc/edit?usp=sharing

import urllib.request
import os
from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):

    #Initializing lists
    lsStartTags = list()
    lsEndTags = list()
    lsStartEndTags = list()
    lsComments = list()

    #HTML Parser Methods
    def handle_starttag(self, startTag, attrs):
        self.lsStartTags.append(startTag)

    def handle_endtag(self, endTag):
        self.lsEndTags.append(endTag)

    def handle_startendtag(self, startendTag, attrs):
        self.lsStartEndTags.append(startendTag)

    def handle_data(self, data):
        # print("Encountered some data  :", data)
        if data.find('.bin') > 0:
            self.lsComments.append(data)


class HtmlReaderClass(object):
    def __init__(self):
        self.url = "http://air.eng.utah.edu/files/updates"
        fp = urllib.request.urlopen(self.url)
        self._data = list
        self.mybytes = fp.read()
        fp.close()

    # BIN_LOCAL_PATH should not be changed, hence this directory is used when flashing, see RESOURCE_BIN_PATH in main.py
    def get_file(self, file_name):
        APP_PATH = os.path.dirname(os.path.realpath(__file__))
        BIN_LOCAL_PATH = APP_PATH + os.path.sep + "resources" + os.path.sep + "binary" + os.path.sep + file_name
        urllib.request.urlretrieve("http://air.eng.utah.edu/files/updates/" + file_name,
                                   BIN_LOCAL_PATH)

    def printContent(self):
        mystr = self.mybytes.decode("utf8")
        parser = MyHTMLParser()
        parser.feed(mystr)
        # print("Data", parser.lsComments)

    @property
    def data(self):
        mystr = self.mybytes.decode("utf8")
        # print(mystr)
        parser = MyHTMLParser()
        parser.feed(mystr)
        self._data = parser.lsComments
        return self._data


# if __name__ == '__main__':
#     a = HtmlReaderClass()
#     a.get_file("airu-firmware-2.0.bin")
    # print("data", a.data)

