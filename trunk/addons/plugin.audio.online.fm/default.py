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
thumb = os.path.join(os.getcwd().replace(';', ''), "icon.png" )


def showMessage(heading, message, times = 3000):
	heading = heading.encode('utf-8')
	message = message.encode('utf-8')
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, thumb))


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

def getURL(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
	req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
	req.add_header('Accept-Language', 'ru,en;q=0.9')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

def get_root():
	def ParsePage(target):
		http = getURL(target)
		r1 = re.compile('<div class="public">(.*?)div class="clear">', re.DOTALL).findall(http)
		if len(r1) > 0:
			for r2 in r1:
				(img, alt)         = re.compile('<img src="(.*?)" alt="(.*?)" />').findall(r2)[0]
				(upf, alt2, Title) = re.compile('<a href="(.*?)" title="(.*?)">(.*?)</a>').findall(r2)[0]
				img = img.replace(' ', '%20')
				upf = upf.replace(' ', '%20')
				uri = sys.argv[0] + '?mode=PlayStation'
				uri += '&url='  + urllib.quote_plus('http://online.fm' + upf)
				uri += '&name=' + urllib.quote_plus(alt)
				uri += '&img='  + urllib.quote_plus(img)
				item = xbmcgui.ListItem(alt, iconImage = img, thumbnailImage = img)
				xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
		else:
			showMessage('ERROR', 'No items found "public"')
	ParsePage('http://online.fm/ru/')
	ParsePage('http://online.fm/ru/fmradio/')
	xbmcplugin.endOfDirectory(pluginhandle)

def PlayStation(url, name, img):
	http = getURL(url)
	r1 = re.compile('<div class="tape"><a href="(.*?)">m3u</a></div>').findall(http)
	if len(r1) > 0:
		item = xbmcgui.ListItem(name, iconImage = img, thumbnailImage = img)
		xbmc.Player().play('http://online.fm' + r1[0])
	else:
		showMessage('ERROR', 'No playlist found')

params = get_params()
mode =	None
url  =	None
name =	''
img = thumb

try:    mode = urllib.unquote_plus(params["mode"])
except: pass

try:    url = urllib.unquote_plus(params["url"])
except: pass

try:    name = urllib.unquote_plus(params["name"])
except: pass

try:    img = urllib.unquote_plus(params["img"])
except: pass


if mode == None: get_root()
elif mode == 'PlayStation': PlayStation(url, name, img)





