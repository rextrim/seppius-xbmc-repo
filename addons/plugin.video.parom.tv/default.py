#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
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
import urllib,urllib2,re,sys,os,xbmc
import xbmcplugin,xbmcgui




pluginhandle = int(sys.argv[1])
fanart = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))
xbmcplugin.setPluginFanart(pluginhandle, fanart)

def showMessage(heading, message, times = 5000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)'%(heading, message, times))


def getURL(url):
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
	r1 = re.compile('<a class="channel" id=".*" href="(.*?)" data-channel_id=".*" data-starttime=".*" data-stoptime=".*">\s*<img alt=".*" class=".*" src="(.*?)" />\s*<div class=".*">\s*(.*?)\s*<div class=".*">').findall(http)
	for rURL, rIMG, rTITLE in r1:
		title = rTITLE
		rURL = 'http://www.parom.tv' + rURL
		rIMG = 'http://www.parom.tv' + rIMG
		uri = sys.argv[0] + '?mode=BIG'
		uri += "&url="       + urllib.quote_plus(rURL)
		uri += "&name="      + urllib.quote_plus(title)
		uri += "&thumbnail=" + urllib.quote_plus(rIMG)
		item=xbmcgui.ListItem(title,iconImage=rIMG,thumbnailImage=rIMG)
		item.setInfo(type="Video", infoLabels={"Title":title})
		item.setProperty('IsPlayable', 'true')
		item.setProperty('fanart_image',rIMG)
		xbmcplugin.addDirectoryItem(pluginhandle, uri, item)

	xbmcplugin.endOfDirectory(pluginhandle)

def playVideo(url, name, thumbnail):
	response = getURL(url)
	SWFObject = 'http://www.parom.tv/player.swf'
	mmm = re.compile('so.addParam(.*);').findall(response)


	ma = re.split('\&+', mmm[2])
	mm = re.split('\=+',ma[3])
	mm = mm[1]

	rtmp_file = ''

	rtmp_file = 'rtmp://ua.parom.tv:1935/stream/' + mm


	xbmc.output('SWFObject =%s'%SWFObject)
	#xbmc.output('flashvars =%s'%flashvars)
	xbmc.output('rtmp_file =%s'%rtmp_file)


	furl  = rtmp_file
	furl += ' swfurl='  + SWFObject
	furl += ' pageUrl=' + url
	furl += ' swfVfy='  + SWFObject

	xbmc.output('     furl = %s'%furl)

	item=xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail, path=furl)
	item.setInfo(type="Video", infoLabels={"Title": name})
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
url=''
name=''
thumbnail=fanart
mode=None


try:
    mode=params["mode"]
except:
    pass

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass

try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    thumbnail=urllib.unquote_plus(params["thumbnail"])
except:
    pass

if mode=='BIG':

	playVideo(url, name, thumbnail)
else:
	root('http://www.parom.tv/')

