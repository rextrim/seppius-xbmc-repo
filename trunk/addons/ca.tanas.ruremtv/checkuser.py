import httplib, urllib, urllib2, re
import xml.parsers.expat
import config

class CheckUser:
    req = \
        '<?xml version="1.0" encoding="utf-8"?>' \
        '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">' \
        '<soap:Body>' \
        '<CheckUser xmlns="http://www.iptv-distribution.com/ucas/">' \
        '<sUserLogin>{Username}</sUserLogin>' \
        '<sUserPassword>{Password}</sUserPassword>' \
        '</CheckUser>' \
        '</soap:Body>' \
        '</soap:Envelope>'

    result = None

    def __init__(self, Username, Password):
        self.req = self.req.replace('{Username}', Username).replace('{Password}', Password)

    def Request(self):
        conn = httplib.HTTPConnection(config.server)
        conn.request('POST', config.vodService, self.req, {
            'SOAPAction': 'http://www.iptv-distribution.com/ucas/CheckUser',
            'Content-Type': 'text/xml; charset=utf-8'
        })
        response = conn.getresponse()
        data = response.read()

        p = xml.parsers.expat.ParserCreate()

        p.StartElementHandler = self.start_element
        p.CharacterDataHandler = self.char_data
        
        p.Parse(str(data))
        return self.result == 'true'

    element = None
    def start_element(self, name, attrs):
        if name == 'CheckUserResult':
            self.result = ""
        self.element = name
    def char_data(self, data):
        if self.element == 'CheckUserResult':
            self.result += data

def validateLogin(Username, Password):
    if Username == None or len(Username) < 1 or Password == None or len(Password) < 1:
        return False

    lc = CheckUser(Username, Password)
    return lc.Request()

