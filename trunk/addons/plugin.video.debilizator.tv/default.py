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
TVShowTitle='South Park'


def getURL( url ):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
    req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
    req.add_header('Accept-Language', 'ru,en;q=0.9')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link


def root():
	url = 'http://debilizator.tv/'
	xbmcplugin.setContent(pluginhandle, 'tvshows')
	xbmcplugin.setPluginCategory(pluginhandle, 'debilizator.tv')
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_EPISODE)
	http = getURL(url)

	r1 = re.compile('<div class="chlogo"><a href=(.*?)><img src="(.*?)" alt="(.*?)" title="(.*?)"></a></div>\s*<div class="chdesc"><h2>(.*?)</h2></div>').findall(http)
	for rURL, rTHUMB, rALT, rTITLE, rDESCR in r1:
		title = rTITLE
		description = rDESCR
		thumbnail = rTHUMB.replace('./', 'http://debilizator.tv/')

		u = sys.argv[0] + '?mode=BIG'
		u += "&url="+urllib.quote_plus('http://debilizator.tv/' + rURL)
		u += "&name="+urllib.quote_plus(title)
		u += "&plot="+urllib.quote_plus(description)
		u += "&thumbnail="+urllib.quote_plus(thumbnail)
		liz=xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
		liz.setInfo( type="Video", infoLabels={ "Title": title,
							"Plot":description,
							"TVShowTitle": 'Debilizator.TV: '+ title
							})
		liz.setProperty('IsPlayable', 'true')
		liz.setProperty('fanart_image',thumbnail)
		xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz)
	xbmcplugin.endOfDirectory(pluginhandle)

def playVideo(url, name, thumbnail, plot):
	response = getURL(url)
	SWFObject = 'http://debilizator.tv/' + re.compile('new SWFObject\(\'(.*?)\'').findall(response)[0]
	flashvars = re.compile('so.addParam\(\'flashvars\',\'(.*?)\'\);').findall(response)[0] + '&'
	flashparams = flashvars.split('&')

	param={}
	for i in range(len(flashparams)):
	    splitparams={}
	    splitparams=flashparams[i].split('=')
	    if (len(splitparams))==2:
		param[splitparams[0]]=splitparams[1]

	rtmp_file     = param['file']
	rtmp_streamer = param['streamer']
	rtmp_plugins  = param['plugins']

	#print '            param =%s'%param
	#print '      flashparams =%s'%flashparams
	#print '        SWFObject =%s'%SWFObject
	#print '        rtmp_file =%s'%rtmp_file
	#print '    rtmp_streamer =%s'%rtmp_streamer
	#print '     rtmp_plugins =%s'%rtmp_plugins

	furl  = rtmp_streamer + '/' + rtmp_file
	furl += ' swfurl='  + SWFObject
	furl += ' pageUrl=' + url
	furl += ' tcUrl='   + rtmp_streamer
	furl += ' swfVfy='  + SWFObject

	xbmc.output('furl = %s'%furl)

	item=xbmcgui.ListItem(name, thumbnailImage=thumbnail, path=furl)
	item.setInfo( type="Video", infoLabels={"Title": name})
	item.setProperty('IsPlayable', 'true')
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
name=None
mode=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass

try:
    name=urllib.unquote_plus(params["name"])
except:
    name=''

try:
    mode=params["mode"]
except:
    pass

try:
    thumbnail=urllib.unquote_plus(params["thumbnail"])
except:
    thumbnail=''

try:
    season=int(params["season"])
except:
    season=0

try:
    episode=int(params["episode"])
except:
    episode=0

try:
    premiered=urllib.unquote_plus(params["premiered"])
except:
    premiered=''

try:
    plot=urllib.unquote_plus(params["plot"])
except:
    plot=''

#print "Mode: "+str(mode)
#print "URL: "+str(url)
#print "Name: "+str(name)

if mode=='BIG':
    playVideo(url, name, thumbnail, plot)
else:
	root()





