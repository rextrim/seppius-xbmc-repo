#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *      Copyright (C) 2011 Silen
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# */
import re, os, urllib, urllib2, cookielib, time, random
from time import gmtime, strftime
from urlparse import urlparse

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.seasonvar.ru')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'cookies.txt'))

# load XML library
try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from BeautifulSoup  import BeautifulSoup
except:
    try:
        sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
    except:
        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))

import xppod

import HTMLParser
hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

#---------- parameter/info structure -------------------------------------------
class Param:
    url             = ''
    genre           = ''
    genre_name      = ''
    country         = ''
    country_name    = ''
    is_season       = ''
    name            = ''
    img             = ''

class Info:
    img         = ''
    url         = '*'
    title       = ''
    text        = ''
    director    = ''
    actors      = ''
    year        = ''
    country     = ''
    genre       = ''

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    #-- url
    try:    p.url = urllib.unquote_plus(params['url'])
    except: p.url = ''
    #-- img
    try:    p.img = urllib.unquote_plus(params['img'])
    except: p.img = ''
    #-- is season flag
    try:    p.is_season = urllib.unquote_plus(params['is_season'])
    except: p.is_season = ''
    #-- name
    try:    p.name = urllib.unquote_plus(params['name'])
    except: p.name = ''
    #-- genre
    try:    p.genre = urllib.unquote_plus(params['genre'])
    except: p.genre = 'all'
    try:    p.genre_name = urllib.unquote_plus(params['genre_name'])
    except: p.genre_name = 'Все'
    #-- country
    try:    p.country = urllib.unquote_plus(params['country'])
    except: p.country = 'all'
    try:    p.country_name = urllib.unquote_plus(params['country_name'])
    except: p.country_name = 'Все'
    #-----
    return p

#----------- get Header string ---------------------------------------------------
def Get_Header(par, count):

    info  = 'Сериалов: ' + '[COLOR FF00FF00]'+ str(count) +'[/COLOR] | '
    info += 'Жанр: ' + '[COLOR FFFF00FF]'+ par.genre_name + '[/COLOR] | '
    info += 'Страна: ' + '[COLOR FFFFF000]'+ par.country_name + '[/COLOR]'

    if info <> '':
        #-- info line
        name    = info
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=EMPTY'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- genre
    if par.genre == 'all':
        name    = '[COLOR FFFF00FF]'+ '[Жанр]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=GENRE'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- genre
    if par.country == 'all':
        name    = '[COLOR FFFFF000]'+ '[Страна]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=COUNTRY'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

def Empty():
    return False

#---------- movie list ---------------------------------------------------------
def Movie_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #== get movie list =====================================================
    url = 'http://seasonvar.ru/index.php?onlyjanrnew='+par.genre+'&&sortto=name&country='+par.country+'&nocache='+str(random.random())

    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'seasonvar.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://seasonvar.ru')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()

    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    count = 1
    # -- get number of serials
    try:
        count = len(soup.findAll('div', {'class':'betterTip'}))
    except:
        return False

    #-- add header info
    Get_Header(par, count)

    #-- get movie info
    #try:
    for rec in soup.findAll('div', {'class':'betterTip'}):
        mi.url          = 'http://seasonvar.ru'+rec.find('a')['href']
        mi.title        = rec.find('span')['title'].encode('utf-8')
        mi.img          = 'http://cdn.seasonvar.ru/oblojka/'+rec['id'].replace('div','')+'.jpg'

        i = xbmcgui.ListItem(mi.title, iconImage=mi.img, thumbnailImage=mi.img)
        u = sys.argv[0] + '?mode=SERIAL'
        u += '&name=%s'%urllib.quote_plus(mi.title)
        u += '&url=%s'%urllib.quote_plus(mi.url)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    #except:
    #    pass

    xbmcplugin.endOfDirectory(h)

#---------- serial info ---------------------------------------------------------
def Serial_Info(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    #== get serial details =================================================
    url = par.url
    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'seasonvar.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://seasonvar.ru')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()
    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    # -- check if serial has seasons and provide season list
    if par.is_season == '' and len(soup.findAll('div', {'class':'full-news-2-content'})) > 0:
        #-- generate list of seasons
        for rec in soup.find('div', {'class':'full-news-2-content'}).findAll('a'):
            s_url   = 'http://seasonvar.ru'+rec['href']
            s_name  = rec.text.replace('>>>', '').replace(u'Сериал ', '')
            if s_name.find(u'сезон(') > -1:
                s_name = s_name.split(u'сезон(')[0]+u'сезон'
            s_name = s_name.encode('utf-8')
            s_id    = rec['href'].split('-')[1]
            s_image = 'http://cdn.seasonvar.ru/oblojka/'+s_id+'.jpg'

            i = xbmcgui.ListItem(s_name, iconImage=s_image, thumbnailImage=s_image)
            u = sys.argv[0] + '?mode=SERIAL'
            #-- filter parameters
            u += '&name=%s'%urllib.quote_plus(s_name)
            u += '&url=%s'%urllib.quote_plus(s_url)
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&country=%s'%urllib.quote_plus(par.country)
            u += '&country_name=%s'%urllib.quote_plus(par.country_name)
            u += '&is_serial=%s'%urllib.quote_plus('*')
            xbmcplugin.addDirectoryItem(h, u, i, True)
    else:
        #-- generate list of movie parts
        # -- get movie info
        for rec in soup.find('td', {'class':'td-for-content'}).findAll('p'):
            if len(rec.findAll('span', {'class':'videl'})) > 0:
                for j in str(rec).split('<br />'):
                    r = re.compile('<span class="videl">(.+?)<\/span>(.+?)<\/br>', re.MULTILINE|re.DOTALL).findall(str(j)+'</br>')
                    for s in r:
                        if s[0] == 'Жанр:':     mi.genre        = s[1].replace('</p>', '')
                        if s[0] == 'Страна:':   mi.country      = s[1].replace('</p>', '')
                        if s[0] == 'Вышел:':    mi.year         = s[1].replace('</p>', '')
                        if s[0] == 'Режисёр:':  mi.director     = s[1].replace('</p>', '')
                        if s[0] == 'Роли:':     mi.actors       = s[1].replace('</p>', '')
            else:
                mi.text = rec.text.encode('utf-8')


        mi.img = soup.find('td', {'class':'td-for-content'}).find('img')['src']

        # -- get serial parts info
        # -- mane of season
        i = xbmcgui.ListItem(par.name, iconImage=mi.img, thumbnailImage=mi.img)
        u = sys.argv[0] + '?mode=EMPTY'
        xbmcplugin.addDirectoryItem(h, u, i, True)

        # -- get list of season parts
        s_url = ''
        s_num = 0
        for rec in Get_PlayList(soup, url):
            for par in rec.replace('"','').split(','):
                if par.split(':')[0]== 'comment':
                    name = str(s_num+1) + ' серия' #par.split(':')[1]+' '
                if par.split(':')[0]== 'file':
                    s_url = par.split(':')[1]+':'+par.split(':')[2]
            s_num += 1

            i = xbmcgui.ListItem(name, path = urllib.unquote(s_url), thumbnailImage=mi.img) # iconImage=mi.img
            u = sys.argv[0] + '?mode=PLAY'
            u += '&url=%s'%urllib.quote_plus(s_url)
            u += '&name=%s'%urllib.quote_plus(name)
            u += '&img=%s'%urllib.quote_plus(mi.img)
            i.setInfo(type='video', infoLabels={    'title':       mi.title,
                                                    'cast' :       mi.actors,
                            						'year':        int(mi.year),
                            						'director':    mi.director,
                            						'plot':        mi.text,
                            						'genre':       mi.genre})
            i.setProperty('fanart_image', mi.img)
            #i.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

#---------- get play list ------------------------------------------------------
def Get_PlayList(soup, parent_url):
    #-- get play list url
    for rec in soup.findAll('script', {'type':'text/javascript'}):
        if rec.text.find('$.post("encode.php') > -1:
            # $.post("encode.php?ko=587ce161a992d24084d628b0c001f951", {"getCodeMark":"955"}
            z = rec.text.replace('$.post("','[').replace('", {',']')
            urlx = re.compile('\$\.post\("(.+?)", \{"(.+?)":"(.+?)"\}', re.MULTILINE|re.DOTALL).findall(rec.text)
            url = 'http://seasonvar.ru/'+urlx[0][0]
            code1 = urlx[0][1]
            code2 = urlx[0][2]
            break

    values = {code1 : code2}
    post = urllib.urlencode(values)

    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'seasonvar.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	parent_url)
    request.add_header('Content-Type',	'application/x-www-form-urlencoded')
    request.add_header('Cookie',	'sva=lVe324Pqsl24') # TejndE37EDj8790=MTMzMzk3Njg1ODIxNTg3OTA3NDM=; p_r8790=; d_s8790=2; MG_8790=2; TejndE37EDj3064=MTMzMzk3Njg1OTc3OTMwNjQ5NDU=; p_r3064=; d_s3064=2; MG_3064=2')
    request.add_header('X-Requested-With',	'XMLHttpRequest')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()
    url = 'http://seasonvar.ru/' + xppod.Decode(html)

    # -- get play list
    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'seasonvar.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://seasonvar.ru')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()
    html = xppod.Decode(html)

    return re.compile('{(.+?)}', re.MULTILINE|re.DOTALL).findall(html.replace('{"playlist":[', ''))

#---------- get genre list -----------------------------------------------------
def Genre_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://seasonvar.ru'

    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'seasonvar.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://seasonvar.ru')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    for rec in soup.find('select', {'id':'chkonlyjanr'}).findAll('option'):
        par.genre       = rec['value']
        par.genre_name  = rec.text.capitalize().encode('utf-8')

        i = xbmcgui.ListItem(par.genre_name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#---------- get country list -----------------------------------------------------
def Country_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://seasonvar.ru'

    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'seasonvar.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://seasonvar.ru')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    for rec in soup.find('select', {'id':'chkonlycountry'}).findAll('option'):
        par.country       = rec['value']
        par.country_name  = rec.text.capitalize().encode('utf-8')

        i = xbmcgui.ListItem(par.country_name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

def PLAY(params):
    # -- parameters
    url  = urllib.unquote_plus(params['url'])
    name = urllib.unquote_plus(params['name'])
    img = urllib.unquote_plus(params['img'])

    i = xbmcgui.ListItem(name, path = urllib.unquote(url), thumbnailImage=img)
    i.setProperty('IsPlayable', 'true')
    xbmc.Player().play(url, i)

#-------------------------------------------------------------------------------

def unescape(text):
    try:
        text = hpar.unescape(text)
    except:
        text = hpar.unescape(text.decode('utf8'))

    try:
        text = unicode(text, 'utf-8')
    except:
        text = text

    return text

def get_url(url):
    return "http:"+urllib.quote(url.replace('http:', ''))

#-------------------------------------------------------------------------------
def get_params(paramstring):
	param=[]
	if len(paramstring)>=2:
		params=paramstring
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param
#-------------------------------------------------------------------------------
params=get_params(sys.argv[2])

# get cookies from last session
cj = cookielib.FileCookieJar(fcookies)
hr  = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)

p  = Param()
mi = Info()

mode = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	Movie_List(params)

if mode == 'MOVIE':
	Movie_List(params)
elif mode == 'GENRE':
    Genre_List(params)
elif mode == 'COUNTRY':
    Country_List(params)
elif mode == 'SERIAL':
	Serial_Info(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY':
	PLAY(params)


