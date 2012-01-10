import httplib, urllib, urllib2, re
import xml.parsers.expat
import config

class GetRadioStationListByUser:
    req = \
        '<?xml version="1.0" encoding="utf-8"?>' \
        '<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">' \
        '<soap:Body>' \
        '<GetRadioStationListByUser xmlns="http://www.iptv-distribution.com/ucas/">' \
        '<sUserLogin>{Username}</sUserLogin>' \
        '</GetRadioStationListByUser>' \
        '</soap:Body>' \
        '</soap:Envelope>'

    programs = []
    id = None
    name = None
    stream = None
    icon = None
    element = None

    def __init__(self, Username):
        self.req = self.req.replace('{AppName}', config.appName) \
        .replace('{Username}', Username)
        #print self.req		

    def Request(self):
        conn = httplib.HTTPConnection(config.server)
        conn.request('POST', config.radioService, self.req, {
            'SOAPAction': 'http://www.iptv-distribution.com/ucas/GetRadioStationListByUser',
            'Content-Type': 'text/xml; charset=utf-8'
        })
        response = conn.getresponse()
        data = response.read()
        #print data

        p = xml.parsers.expat.ParserCreate()

        p.StartElementHandler = self.start_element
        p.EndElementHandler = self.end_element
        p.CharacterDataHandler = self.char_data
        
        p.Parse(str(data))
        return self.programs

    def start_element(self, name, attrs):
        if name == 'Radio':
            self.id = ""
            self.name = ""
            self.icon = ""
            self.stream = ""
        self.element = name
    def end_element(self, name):
        if name == 'Radio':
            if len(self.icon) < 10:
                self.icon = ""
            self.programs.append((str(len(self.programs) + 1).zfill(2) + '. ' + self.name, self.id, self.icon, self.stream))
            self.id = None
            self.name = None
            self.stream = None
            self.icon = None
    def char_data(self, data):
        if data.strip():
            data = data.encode('utf-8')
            if self.element == 'ID':
                self.id += data
            elif self.element == 'Name':
                self.name += data
            elif self.element == 'IconUrl':
                self.icon += data
            elif self.element == 'StreamUrl':
                self.stream += data








