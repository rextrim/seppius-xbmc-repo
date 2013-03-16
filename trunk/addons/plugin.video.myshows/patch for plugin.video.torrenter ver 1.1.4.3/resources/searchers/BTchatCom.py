#-*- coding: utf-8 -*-
'''
    Torrenter plugin for XBMC
    Copyright (C) 2012 Vadim Skorba
    vadim.skorba@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import SearcherABC
import urllib
import re
import sys
import tempfile
import os
import Localization
import time

class BTchatCom(SearcherABC.SearcherABC):
    
    '''
    Weight of source with this searcher provided.
    Will be multiplied on default weight.
    Default weight is seeds number
    '''
    sourceWeight = 1

    '''
    Relative (from root directory of plugin) path to image
    will shown as source image at result listing
    '''
    searchIcon = '/resources/searchers/icons/bt-chat.com.png'

    '''
    Flag indicates is this source - magnet links source or not.
    Used for filtration of sources in case of old library (setting selected).
    Old libraries won't to convert magnet as torrent file to the storage
    '''
    @property
    def isMagnetLinkSource(self):
        return False

    '''
    Main method should be implemented for search process.
    Receives keyword and have to return dictionary of proper tuples:
    filesList.append((
        int(weight),# Calculated global weight of sources
        int(seeds),# Seeds count
        str(title),# Title will be shown
        str(link),# Link to the torrent/magnet
        str(image),# Path/URL to image shown at the list
    ))
    '''

    def search(self, keyword):
        filesList = []
        coooo='__utma=77974087.1115476442.1359660126.1359838833.1363422053.6; __utmz=77974087.1359660126.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmb=77974087.9.10.1363422053; __utmc=77974087; /=; /login.php=; /index.php=; '

        if not sys.modules[ "__main__" ].__settings__.getSetting("btchat-auth"):
            cookie = self.login()
            if cookie:
                sys.modules[ "__main__" ].__settings__.setSetting("btchat-auth", cookie)
            else:
                print 'Auth attempt was failed1'
                return filesList

        response = self.makeRequest(
            'http://www.bt-chat.com/search.php?mode=simplesearch',
            {'name':keyword,'torrent':'Search'},
            headers=[('Cookie', coooo+sys.modules[ "__main__" ].__settings__.getSetting("btchat-auth")),('Referer','http://www.bt-chat.com/search.php?mode=simplesearch')])

        if re.search('Guest! Please', response):
            cookie = self.login()
            if cookie:
                sys.modules[ "__main__" ].__settings__.setSetting("btchat-auth", cookie)
            else:
                print 'Auth attempt was failed2'
                return filesList
            response = self.makeRequest(
                'http://www.bt-chat.com/search.php?mode=simplesearch',
                {'name':keyword, 'torrent':'Search'},
                headers=[('Cookie', coooo+sys.modules[ "__main__" ].__settings__.getSetting("btchat-auth")),('Referer','http://www.bt-chat.com/search.php?mode=simplesearch')]
            )

        if None != response and 0 < len(response):
            response = response.decode('latin1').encode('utf8')
        #print response
        for (link, title, seeds) in re.compile('style="text-align: left;"><a href=".+?id=(\d+)"><.+?hit=1">(.+?)</a>.+? style="width:60px; color:#129524;" .+?>(\d+)</td>', re.DOTALL).findall(response):
            torrentTitle = "%s [%s: %s]" % (title, Localization.localize('Seeds'), seeds)
            image = sys.modules[ "__main__"].__root__ + self.searchIcon
            link = 'http://www.bt-chat.com/download1.php?type=torrent&id=' + link
            #print int(seeds), self.unescape(self.stripHtml(torrentTitle)), link, image
            filesList.append((
                int(int(self.sourceWeight) * int(seeds)),
                int(seeds),
                self.unescape(self.stripHtml(torrentTitle)),
                self.__class__.__name__ + '::' + link,
                image,
            ))
        return filesList

    def getTorrentFile(self, url):

        if not sys.modules[ "__main__" ].__settings__.getSetting("btchat-auth"):
            cookie = self.login()
            if cookie:
                sys.modules[ "__main__" ].__settings__.setSetting("btchat-auth", cookie)
        cookie = sys.modules[ "__main__" ].__settings__.getSetting("btchat-auth")

        localFileName = tempfile.gettempdir() + os.path.sep + self.md5(url)
        content = self.makeRequest(
           url,
           headers=[('Cookie', cookie)]
        )
        localFile = open(localFileName, 'wb+')
        localFile.write(content)
        localFile.close()
        return 'file:///' + localFileName

    def login(self):
        pageContent = self.makeRequest('http://www.bt-chat.com/login.php')
        captchaMatch = reCaptcha().checkForReCaptcha(pageContent)
        data = {
            'username': 'myshows',
            'password': 'myshows',
            'login':'Login'
        }
        if captchaMatch:
            url, recaptcha_challenge_field =reCaptcha().getCaptcha(pageContent)
            captchaCode = self.askCaptcha(url)
            if captchaCode:
                data['recaptcha_challenge_field']=recaptcha_challenge_field
                data['recaptcha_response_field']=captchaCode
            else:
                return False
        i=self.makeRequest(
             'http://www.bt-chat.com/transact-user.php',
             data
        )
        for cookie in self.cookieJar:
            if cookie.name == 'passkey':
                return 'passkey=' + cookie.value
        return False


class reCaptcha():
    def __init__(self):
        import xbmc
        self.__datapath__ = xbmc.translatePath('special://temp')
        
        self.challengefile = os.path.join(self.__datapath__,'reCaptchachallengeToken')
        #pageurlfile   = os.path.join(self.__datapath__,'responseURL')
    
    def _open(self, filename):
        fh = open(filename, 'r')
        contents=fh.read()
        fh.close()
        return contents
    
    def _save(self, filename,contents):
        fh = open(filename, 'w')
        fh.write(contents)
        fh.close()
    
    def checkForReCaptcha(self, html):
        #check for recaptcha in the page source, and return true or false.
        if 'recaptcha_challenge_field' in html:
            return True
        else:
            return False
    
    
    def checkIfSuceeded(self, html):
        #reverse the boolean to check for success.
        if 'recaptcha_challenge_field' in html:
            return False
        else:
            return True
    
    def getCaptcha(self, html):
        #get the captcha image url and save the challenge token

        #try:
        token = (re.compile('src="http://api.recaptcha.net/challenge\?k\=(.+?)"').findall(html))[0]
        #except:
            #print "couldn't find the challenge token"
    
        #try:
        challengehtml = BTchatCom().makeRequest('http://api.recaptcha.net/challenge?k=' + token)
        #except:
            #print "couldn't load the challenge url"
    
    
        #try:
        challenge = (re.compile("challenge : '(.+?)'").findall(challengehtml))[0]
        #except:
            #print "couldn't get challenge code"
    
        imageurl = 'http://www.google.com/recaptcha/api/image?c=' + challenge
    
        #hacky method --- save challenge to file, to reopen in next step
        #self._save(self.challengefile, challenge)
    
        return imageurl, challenge