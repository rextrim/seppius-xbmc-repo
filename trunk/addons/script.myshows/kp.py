# -*- coding: utf-8 -*-
__author__ = "DiMartino"
import urllib2, re, cookielib
from kinopoisk.HTTP import *

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.172 Safari/537.22'
class Login():
    def __init__(self,login,password,cookie=None):
        self.login = login
        self.password = password
        self.cookie = cookie

    def get_cookie(self):
        #if self.cookie: return self.cookie

        address = 'http://www.kinopoisk.ru/login/?auth=%C3%A2%C3%AE%C3%A9%C3%B2%C3%A8%20%C3%AD%C3%A0%20%C3%B1%C3%A0%C3%A9%C3%B2&shop_user%5Blogin%5D='\
                  +self.login+'&shop_user%5Bmem%5D=on&shop_user%5Bpass%5D='+self.password

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        request = urllib2.Request(address)
        request.add_header('User-agent', USER_AGENT)
        request.add_header("Content-Type", "text/html")
        urllib2.install_opener(opener)
        response = urllib2.urlopen(request)

        if len(cj._cookies['.kinopoisk.ru']['/'])>0:
            self.cookie = ''
            for i in cj._cookies['.kinopoisk.ru']['/']:
                self.cookie=self.cookie+cj._cookies['.kinopoisk.ru']['/'][i].name+'='+cj._cookies['.kinopoisk.ru']['/'][i].value+'; '
        return self.cookie

    def testAcc(self):
        url = 'http://www.kinopoisk.ru/'
        headers = {'User-Agent' : USER_AGENT,
                   'Host' : 'www.kinopoisk.ru',
                   'Cookie': self.cookie,
                   'Accept': 'text/html',
                  }

        req = HTTPRequest(url, headers = headers)
        data = HTTP().fetch(req)
        if self.login in str(data.body).decode('cp1251'):
            return True

class Rate():
    def __init__(self,rate,kpId,cookie):
        self.cookie = cookie
        self.kpId=kpId
        self.code=self.get_code()
        self.rate=rate

    def get_code(self):
        url = 'http://www.kinopoisk.ru/film/'+str(self.kpId)+'/'
        headers = {'User-Agent' : USER_AGENT,
                   'Host' : 'www.kinopoisk.ru',
                   'Cookie': self.cookie,
                   'Accept': 'text/html',
                  }

        req = HTTPRequest(url, headers = headers)
        data = HTTP().fetch(req)

        reobj = re.compile(r'user_code:\'(.+?)\',')
        self.code = reobj.findall(str(data.body).decode('cp1251'))[0]
        return self.code

    def rateit(self):
        url = 'http://www.kinopoisk.ru/vote.php?film='+str(self.kpId)+'&film_vote='+str(self.rate)+'&c='+self.code
        headers = {'User-Agent' : USER_AGENT,
                   'Host' : 'www.kinopoisk.ru',
                   'Cookie': self.cookie,
                   'Accept': 'text/html',
                  }

        req = HTTPRequest(url, headers = headers)
        data = HTTP().fetch(req)
        if str(data.body).decode('cp1251')=='Ok':
            return True
