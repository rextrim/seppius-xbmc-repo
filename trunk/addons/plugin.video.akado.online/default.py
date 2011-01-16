#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *      Copyright (C) 2010 Kostynoy S. aka Seppius
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
import urllib,urllib2,re,sys,os
import xbmcplugin,xbmcgui

pluginhandle = int(sys.argv[1])
fanart = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))
xbmcplugin.setPluginFanart(pluginhandle, fanart)

def getURL( url ):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
	req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
	req.add_header('Accept-Language', 'ru,en;q=0.9')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

def root(url):
	http = getURL(url)
	r1 = re.compile('<div class="canal-frame"><a href="(.*?)"><img src="(.*?)" width="(.*?)" height="(.*?)"/></a></div><h1><a href="(.*?)">(.*?)</a>').findall(http)
	for rURL, rTHUMB, rD1, rD2, rURL2, rTITLE in r1:
		thumbnail = 'http://tv.akado.ru' + rTHUMB
		target = url + rURL
		uri = sys.argv[0] + '?mode=BIG'
		uri += "&url="       + urllib.quote_plus(target)
		uri += "&name="      + urllib.quote_plus(rTITLE)
		uri += "&thumbnail=" + urllib.quote_plus(thumbnail)
		item=xbmcgui.ListItem(rTITLE, iconImage=thumbnail, thumbnailImage=thumbnail)
		item.setInfo( type="Video", infoLabels={ "Title": rTITLE})
		item.setProperty('IsPlayable', 'true')
		item.setProperty('fanart_image',thumbnail)
		xbmcplugin.addDirectoryItem(pluginhandle,uri,item)
	xbmcplugin.endOfDirectory(pluginhandle)

def playVideo(url, name, thumbnail):
	response = getURL(url)
	SWFObject = 'http://tv.akado.ru/i/online/player.swf'
	rtmp_path = re.compile('ShowPlayer4ot\(\'(.*?)\'').findall(response)[0]

	rtmp = rtmp_path
	rtmp += ' swfUrl='  + urllib.unquote_plus(SWFObject)
	rtmp += ' pageUrl=' + urllib.unquote_plus(url)
	rtmp += ' tcUrl='   + urllib.unquote_plus(rtmp_path.replace('/stream',''))
	rtmp += ' swfVfy=true'
	rtmp += ' live=true'
	xbmc.output('rtmp = %s'%rtmp)
	#xbmc.output('rtmpdump -r "%s" --swfUrl="%s" --pageUrl="%s" --tcUrl="%s" --swfVfy="%s"'%(rtmp_path, SWFObject, SWFObject, rtmp_path.replace('/stream',''), SWFObject))
	item=xbmcgui.ListItem(name, thumbnailImage=thumbnail, path=rtmp)
	item.setInfo( type="Video", infoLabels={"Title": name})
	xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
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

params=get_params()
url=None
name=''
mode=None
thumbnail=fanart

import adanalytics
adanalytics.main(sys.argv[0], pluginhandle, sys.argv[2])

try: mode=params["mode"]
except: pass
try: url=urllib.unquote_plus(params["url"])
except: pass
try: name=urllib.unquote_plus(params["name"])
except: pass
try: thumbnail=urllib.unquote_plus(params["thumbnail"])
except: pass

if mode=='BIG':
    playVideo(url, name, thumbnail)
else:
	root('http://tv.akado.ru/online/')
