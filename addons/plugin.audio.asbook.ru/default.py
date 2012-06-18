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
#import json
import simplejson as json

Addon = xbmcaddon.Addon(id='plugin.audio.asbook.ru')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'cookies.txt'))

# load XML library
try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from BeautifulSoup  import BeautifulSoup
    lib_path = os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib')
except:
    try:
        sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        lib_path = os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib')
    except:
        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))
        lib_path = os.path.join(os.getcwd(), r'resources', r'lib')

import HTMLParser
hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

#---------- parameter/info structure -------------------------------------------
class Param:
    url             = ''
    genre           = ''
    page            = '1'
    name            = ''
    img             = ''
    bcount          = ''
    pcount          = ''
    track           = ''

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    #-- url
    try:    p.url = urllib.unquote_plus(params['url'])
    except: p.url = ''
    #-- track
    try:    p.track = urllib.unquote_plus(params['track'])
    except: p.track = ''
    #-- img
    try:    p.img = urllib.unquote_plus(params['img'])
    except: p.img = ''
    #-- name
    try:    p.name = urllib.unquote_plus(params['name'])
    except: p.name = ''
    #-- genre
    try:    p.genre = urllib.unquote_plus(params['genre'])
    except: p.genre = ''
    #-- page
    try:    p.page = urllib.unquote_plus(params['page'])
    except: p.page = '1'
    #-- bcount
    try:    p.bcount = urllib.unquote_plus(params['bcount'])
    except: p.bcount = ''
    #-- pcount
    try:    p.pcount = urllib.unquote_plus(params['pcount'])
    except: p.pcount = ''
    #-----
    return p

#-- get page source ------------------------------------------------------------
def get_URL(url):
    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'asbook.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://asbook.ru')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            print 'Err 1'
            #xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            print 'Err 2'
            #xbmc.log('The server couldn\'t fulfill the request. Error code: '+ str(e.code))

    html = f.read()

    return html

#----------- get Header string ---------------------------------------------------
def Get_Header(par):

    info  = '' #'Книг: ' + '[COLOR FF00FF00]' + par.bcount + '[/COLOR]'

    if int(par.pcount) > 1:
        info += ' | Pages: ' + '[COLOR FF00FF00]'+ par.page + '/' + par.pcount +'[/COLOR]'

    if par.genre <> '':
        info += ' | Жанр: ' + '[COLOR FF00FFF0]'+ par.genre + '[/COLOR]'

    if info <> '':
        #-- info line
        name    = info
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=EMPTY'
        #-- filter parameters
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #--- page navigation
    #-- first page link
    if int(par.page) > 1 :
        name    = '[FIRST PAGE]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=BOOK_LIST'
        u += '&name=%s'%urllib.quote_plus(par.name)
        u += '&url=%s'%urllib.quote_plus(par.url)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&page=%s'%urllib.quote_plus('1')
        u += '&pcount=%s'%urllib.quote_plus(par.pcount)
        #u += '&bcount=%s'%urllib.quote_plus(par.bcount)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    #-- previous page link
    if int(par.page) > 1 :
        name    = '[PREVIOUS PAGE]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=BOOK_LIST'
        u += '&name=%s'%urllib.quote_plus(par.name)
        u += '&url=%s'%urllib.quote_plus(par.url)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&page=%s'%urllib.quote_plus(str(int(par.page)-1))
        u += '&pcount=%s'%urllib.quote_plus(par.pcount)
        #u += '&bcount=%s'%urllib.quote_plus(par.bcount)
        xbmcplugin.addDirectoryItem(h, u, i, True)

#----------- get Footer string ---------------------------------------------------
def Get_Footer(par):
    #--- page navigation
    #-- next page link
    if int(par.page) < int(par.pcount) :
        name    = '[NEXT PAGE]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=BOOK_LIST'
        u += '&name=%s'%urllib.quote_plus(par.name)
        u += '&url=%s'%urllib.quote_plus(par.url)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&page=%s'%urllib.quote_plus(str(int(par.page)+1))
        u += '&pcount=%s'%urllib.quote_plus(par.pcount)
        #u += '&bcount=%s'%urllib.quote_plus(par.bcount)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    #-- last page link
    if int(par.page) < int(par.pcount) :
        name    = '[LAST PAGE]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=BOOK_LIST'
        u += '&name=%s'%urllib.quote_plus(par.name)
        u += '&url=%s'%urllib.quote_plus(par.url)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&page=%s'%urllib.quote_plus(par.pcount)
        u += '&pcount=%s'%urllib.quote_plus(par.pcount)
        #u += '&bcount=%s'%urllib.quote_plus(par.bcount)
        xbmcplugin.addDirectoryItem(h, u, i, True)

def Empty():
    return False

#---------- movie list ---------------------------------------------------------
def Book_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #== get book list =====================================================
    url = par.url+'page/'+par.page+'/'

    html = get_URL(url)
    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    #-- get number of pages
    if par.pcount == '0':
        pc = 1
        try:
            for rec in soup.find('div', {'class':'navigation'}).findAll('a'):
                try:
                    if pc < int(rec.text):
                        pc = int(rec.text)
                except:
                    pass
            par.pcount = str(pc)
        except:
            par.pcount = '1'

    #-- add header info
    Get_Header(par)

    #-- get book info
    #try:
    for rec in soup.findAll('div', {'class':'short'}):
        b_name  = unescape(rec.find('div', {'class':'title'}).find('a').text).encode('utf-8')

        b_name_s = b_name.split('"')
        try:
            if b_name_s[0] == '':
                b_name   = b_name_s[2].strip()+' "'+b_name_s[1].strip()+'"'
                b_name_f = '[COLOR FFFFF000]'+b_name_s[2].strip()+'[/COLOR] [COLOR FF00FFF0]"'+b_name_s[1].strip()+'"[/COLOR]'
            elif b_name_s[2] == '':
                b_name = b_name_s[0].strip()+' "'+b_name_s[1].strip()+'"'
                b_name_f = '[COLOR FFFFF000]'+b_name_s[0].strip()+'[/COLOR] [COLOR FF00FFF0]"'+b_name_s[1].strip()+'"[/COLOR]'
        except:
            b_name_s = b_name.split('-')
            try:
                b_name = b_name_s[0].strip()+' "'+b_name_s[1].strip()+'"'
                b_name_f = '[COLOR FFFFF000]'+b_name_s[0].strip()+'[/COLOR] [COLOR FF00FFF0]"'+b_name_s[1].strip()+'"[/COLOR]'
            except:
                b_name_f = '[COLOR FF00FFF0]"'+b_name+'"[/COLOR]'
        #---
        b_url   = rec.find('div', {'class':'title'}).find('a')['href']
        b_img   = rec.find('img')['src']
        b_descr = '' #unescape(rec.find('div', {'class':'post_text clearfix'}).text).encode('utf-8')

        i = xbmcgui.ListItem(b_name_f, iconImage=b_img, thumbnailImage=b_img)
        u = sys.argv[0] + '?mode=BOOK'
        u += '&name=%s'%urllib.quote_plus(b_name)
        u += '&url=%s'%urllib.quote_plus(b_url)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&pcount=%s'%urllib.quote_plus(par.pcount)
        #u += '&bcount=%s'%urllib.quote_plus(par.bcount)
        i.setInfo(type='music', infoLabels={    'title':       b_name,
                        						'plot':        b_descr,
                        						'genre':       par.genre})
        xbmcplugin.addDirectoryItem(h, u, i, True)
    #except:
    #    pass

    #-- add footer info
    Get_Footer(par)

    xbmcplugin.endOfDirectory(h)


#---------- serial info ---------------------------------------------------------
def Book_Info(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    #== get book details =================================================
    url = par.url
    html = get_URL(url)

    # ----------------------------------------------------------------------
    b_name      = ''
    b_score     = ''
    b_img       = ''
    b_descr     = ''
    b_year      = 0
    b_autor     = ''
    b_genre     = ''
    b_actor     = ''
    b_publisher = ''
    b_bitrate   = ''
    b_duration  = 0

    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    b_name      = urllib.unquote(soup.find('h1', {'class':'fulltitle'}).text)
    b_score     = str(int(int(soup.find('li' ,{'class':'current-rating'}).text)/160.00))
    b_img       = soup.find('div', {'class':'fullstory'}).find('img')['src']
    b_descr     = urllib.unquote(soup.find('div', {'class':'tab_content tab_descr'}).find('div', {'class':'text'}).text)

    for rec in soup.find('table', {'class':'data'}).findAll('td'):
        if rec['class'] == 'e':
            b_year = int(rec.find('span').text)
        if rec['class'] == 'a':
            b_autor = rec.find('a').text
        if rec['class'] == 'b':
            b_actor = rec.find('a').text
        if rec['class'] == 'c':
            b_publisher = rec.find('a').text
        if rec['class'] == 'd':
            b_duration = int(rec.find('span').text.split(':')[0])*60*60+int(rec.find('span').text.split(':')[1])*60+int(rec.find('span').text.split(':')[2])

    for j in soup.findAll('script', {'type':'text/javascript'}):
        if 'var flashvars = {' in j.text:
            pl = re.compile('var flashvars = {(.+?)}', re.MULTILINE|re.DOTALL).findall(j.text)
            b_url = pl[0].split(',')[1].replace('pl:','').replace('"','')

    # -- parsing web page --------------------------------------------------
    html = get_URL(b_url)

    playlist = json.loads(html)
    for rec in playlist['playlist']:
        s_name = rec['comment'].encode('utf-8')
        s_url  = rec['file']

        i = xbmcgui.ListItem(s_name, path = urllib.unquote(s_url), thumbnailImage=b_img)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&url=%s'%urllib.quote_plus(b_url)
        u += '&name=%s'%urllib.quote_plus(s_name)
        u += '&img=%s'%urllib.quote_plus(b_img)
        u += '&track=%s'%urllib.quote_plus(s_url)
        i.setInfo(type='music', infoLabels={    'album':       b_name,
                                                'title' :      s_name,
                        						'year':        b_year,
                        						'artist':      b_actor,
                        						'comment':     b_descr,
                        						'genre':       b_genre,
                                                'rating':      b_score})
        i.setProperty('fanart_image', b_img)
        i.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

#---------- get genre list -----------------------------------------------------
def Genre_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://asbook.ru/'

    html = get_URL(url)
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    for rec in soup.find('ul', {'class':'menu'}).findAll('li'):
        try:
            if rec['class'] == 'search': continue
        except:
            pass

        is_parent = (rec.find('ul', {'class':'sub'}) != None)


        if is_parent:
            name = rec.find('a').text
            mode = 'EMPTY'
        else:
            name = '  [COLOR FF00FF00]'+rec.find('a').text +'[/COLOR]' # [COLOR FF00FFF0]'+rec.find('span').text+'[/COLOR]'
            mode = 'BOOK_LIST'

        url = 'http://asbook.ru/'+rec.find('a')['href']
        genre  = rec.find('a').text.encode('utf-8')
        bcount = 0 #rec.find('span').text.replace('(','').replace(')','')

        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode='+mode
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(genre)
        #u += '&bcount=%s'%urllib.quote_plus(bcount)
        u += '&url=%s'%urllib.quote_plus(url)
        u += '&page=%s'%urllib.quote_plus('1')
        u += '&pcount=%s'%urllib.quote_plus('0')

        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

def PLAY(params):
    # create play list
    pl=xbmc.PlayList(1)
    pl.clear()

    # -- parameters
    url  = urllib.unquote_plus(params['url'])
    name = urllib.unquote_plus(params['name'])
    img = urllib.unquote_plus(params['img'])
    track = urllib.unquote_plus(params['track'])

    header = {  'Host'                  :urlparse(track).hostname,
                'Referer'               :'http://asbook.ru/player/uppod.swf',
                'User-Agent'            :'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7'
             }

    html = get_URL(url)
    is_load = 0

    n = 0
    playlist = json.loads(html)
    for rec in playlist['playlist']:
        n += 1
        if track == rec['file']:
            is_load = 1
            s_name = rec['comment'].encode('utf-8')
            s_url  = rec['file']+'|'+urllib.urlencode(header)

            i = xbmcgui.ListItem(s_name, path = urllib.unquote(s_url), thumbnailImage=img)
            i.setInfo(type='music', infoLabels={    'title' :     s_name,
                                                    'track':      str(n)})
            pl.add(s_url, i)

        if is_load == 1:
            s_name = rec['comment'].encode('utf-8')
            s_url  = rec['file']+'|'+urllib.urlencode(header)

            i = xbmcgui.ListItem(s_name, path = urllib.unquote(s_url), thumbnailImage=img)
            i.setInfo(type='music', infoLabels={    'title' :     s_name,
                                                    'track':      str(n)})
            pl.add(s_url, i)

    xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(pl)

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
mode = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	Genre_List(params)

if mode == 'BOOK_LIST':
	Book_List(params)
elif mode == 'GENRE':
    Genre_List(params)
elif mode == 'BOOK':
    Book_Info(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY':
	PLAY(params)


