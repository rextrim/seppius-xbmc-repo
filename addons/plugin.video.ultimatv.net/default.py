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
import re, os, urllib, urllib2, cookielib, time, random, sys
from time import gmtime, strftime
import urlparse

import demjson3 as json

import subprocess, ConfigParser

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.ultimatv.net')
xbmcplugin.setContent(int(sys.argv[1]), 'movies')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'cookies.txt'))

# load XML library
lib_path = os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib')

sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
from BeautifulSoup  import BeautifulSoup

import HTMLParser
hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

#---------- HTPP interface -----------------------------------------------------
def get_HTML(url, post = None, ref = None, get_url = False):
    request = urllib2.Request(url, post)

    host = urlparse.urlsplit(url).hostname
    if ref==None:
        ref='http://'+host

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',   host)
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',             ref)

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
           print 'We failed to reach a server.'
        elif hasattr(e, 'code'):
           print 'The server couldn\'t fulfill the request.'

    if get_url == True:
        html = f.geturl()
    else:
        html = f.read()

    return html

#---------- parameter/info structure -------------------------------------------
class Param:
    url             = ''
    name            = ''
    img             = ''

def Empty():
    return False

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    #-- url
    try:    p.url = urllib.unquote_plus(params['url'])
    except: p.url = ''
    #-- img
    try:    p.img = urllib.unquote_plus(params['img'])
    except: p.img = ''
    #-- name
    try:    p.name = urllib.unquote_plus(params['name'])
    except: p.name = ''
    #-----
    return p

def Empty():
    return False

#---------- channel list ---------------------------------------------------------
def Channel_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    post = None
    url = 'http://ultimatv.net/index.php'
    html = get_HTML(url, post)
    soup = BeautifulSoup(html, fromEncoding="utf-8")

    channels = soup.find('div', {'id':'div-main-c'})

    #-- get channels
    for rec in channels.findAll(re.compile('h2|div')):
        c_name = rec.name
        try:
            c_type = rec['class']
        except:
            c_type = ''

        if c_name == 'h2' or (c_name == 'div' and c_type == 'channel_logo'):
            if c_name == 'h2':
                name = '[COLOR FFFFF000]'+rec.find('a').text.encode('utf-8')+'[/COLOR]'

                i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
                u = sys.argv[0] + '?mode=EMPTY'
                xbmcplugin.addDirectoryItem(h, u, i, True)
            else:
                name = rec.find('img')['alt'].encode('utf-8')
                url  = 'http://ultimatv.net/'+rec.find('a')['href']
                img  = 'http://ultimatv.net/'+rec.find('img')['src']

                i = xbmcgui.ListItem('[COLOR FF00FF00]   '+name+'[/COLOR]', path = urllib.unquote(url), thumbnailImage=img) # iconImage=mi.img
                u = sys.argv[0] + '?mode=PLAY'
                u += '&url=%s'%urllib.quote_plus(url)
                u += '&name=%s'%urllib.quote_plus(name)
                u += '&img=%s'%urllib.quote_plus(img)
                i.setProperty('fanart_image', img)
                #i.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

def PLAY(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- assemble video link
    post = None
    html = get_HTML(par.url, post)
    soup = BeautifulSoup(html, fromEncoding="utf-8")

    url = soup.find('iframe')['src']

    html = get_HTML(url, post)
    soup = BeautifulSoup(html, fromEncoding="utf-8")

    f_str = soup.find('param',{'name':'flashVars'})['value']
    for rec in f_str.split('&'):
        if rec.split('=')[0] == 'videoid':
            varsideoid = rec.split('=')[1]
        if rec.split('=')[0] == 'sessid':
            sessid = rec.split('=')[1]

    url = 'http://clients.cdnet.tv/flashplayer/instruction.php?' + soup.find('object').find('param',{'name':'flashVars'})['value'].replace('videotype=','type=')
    html = get_HTML(url, post)
    soup = BeautifulSoup(html, fromEncoding="utf-8")
    if Addon.getSetting('HQ') == 'true':
        stream_sd = soup.find('root')['stream_hd']
        chanel_sd = soup.find('root')['chanel_hd']
    else:

        stream_sd = soup.find('root')['stream_sd']
        chanel_sd = soup.find('root')['chanel_sd']

    video = '%s/%s swfUrl=http://clients.cdnet.tv/flashplayer/player.swf pageUrl=http://clients.cdnet.tv/flashbroadcast.php?channel=%s token=%s live=true swfVfy=true' % (stream_sd, chanel_sd, varsideoid, 'Ys#QBn%3O0@l1')

    #-- play TV
    i = xbmcgui.ListItem(par.name, path = urllib.unquote(video), thumbnailImage=par.img)
    i.setProperty('IsPlayable', 'true')
    #xbmcplugin.setResolvedUrl(h, True, i)
    xbmc.Player( xbmc.PLAYER_CORE_MPLAYER).play(video, i)

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

mode = None

#---------------------------------

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	mode = '$'

if mode == '$':
    mode = 'LIST'

if mode == 'LIST':
	Channel_List(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY':
	PLAY(params)



