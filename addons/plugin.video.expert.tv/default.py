#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *	  Copyright (C) 2010 Kostynoy S. aka Seppius
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

import urllib, urllib2, re, sys, os, httplib
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
import socket
socket.setdefaulttimeout(50)

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, 'http://www.expert.ru/d/expert.ru/img/logo.png'))

def strip_html(text):
	def fixup(m):
		text = m.group(0)
		if text[:1] == "<":
			if text[1:3] == 'br':
				return '\n'
			else:
				return "" # ignore tags
		if text[:2] == "&#":
			try:
				if text[:3] == "&#x":
					return chr(int(text[3:-1], 16))
				else:
					return chr(int(text[2:-1]))
			except ValueError:
				pass
		elif text[:1] == "&":
			import htmlentitydefs
			if text[1:-1] == "mdash":
				entity = " - "
			elif text[1:-1] == "ndash":
				entity = "-"
			elif text[1:-1] == "hellip":
				entity = "-"
			else:
				entity = htmlentitydefs.entitydefs.get(text[1:-1])
			if entity:
				if entity[:2] == "&#":
					try:
						return chr(int(entity[2:-1]))
					except ValueError:
						pass
				else:
					return entity
		return text
	ret =  re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)
	return re.sub("\n+", '\n' , ret)


def GET(target):
	targeturl = 'http://www.expert.ru' + target
	#xbmc.output('targeturl='+targeturl)
	try:
		req = urllib2.Request(targeturl)
		req.add_header(     'User-Agent','Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00')
		req.add_header(           'Host','www.expert.ru')
		req.add_header(         'Accept','text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*')
		req.add_header('Accept-Language','ru-RU,ru;q=0.9,en;q=0.8')
		req.add_header( 'Accept-Charset','utf-8, utf-16, *;q=0.1')
		req.add_header('Accept-Encoding','identity, *;q=0')
		req.add_header(     'Connection','Keep-Alive')
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		#xbmc.output(a)
		return a
	except Exception, e:
		showMessage(targeturl, e, 5000)
		return None


def getitems(params):
	http = GET('/tv/')
	if http == None: return False
	s1 = re.compile('<ul class="program-guide">(.*?)</ul>', re.DOTALL).findall(http)
	if len(s1) > 0:
		s2 = re.compile('<a href="(.*?)">(.*?)</a>').findall(s1[0])
		for href, name in s2:
			name = strip_html(name)
			li = xbmcgui.ListItem(name, iconImage = icon, thumbnailImage = icon)
			uri = sys.argv[0] + '?mode=getprogram'
			uri += '&href='+urllib.quote_plus(href)
			uri += '&name='+urllib.quote_plus(name)
			xbmcplugin.addDirectoryItem(h, uri, li, True)
		xbmcplugin.endOfDirectory(h)
	else:
		showMessage('ОШИБКА ДИЗАЙНА', 'Нет <ul class="program-guide">', 3000)
		return False


def getprogram(params):
	try:
		name = urllib.unquote_plus(params['name'])
	except:
		name = ''
	try:
		href = urllib.unquote_plus(params['href'])
		http = GET(href)
		if http == None: return False
	except: return False
	s1 = re.compile('<li class="clearfix">(.*?)</li>', re.DOTALL).findall(http)
	if len(s1) == 0:
		showMessage('ОШИБКА ДИЗАЙНА', 'Нет <li class="clearfix">', 3000)
		return False
	for curli in s1:
		try:
			img1 = re.compile('<img src="(.*?)" ').findall(curli)
			thumb = 'http://www.expert.ru' + img1[0]
		except: thumb = icon
		try:
			dat1 = re.compile('<div class="tl-date">(.*?)</div>').findall(curli)
			date = dat1[0]
		except: date = ''
		try:
			plo1 = re.compile('<p>(.*?)</p>', re.DOTALL).findall(curli)
			plot = plo1[0]
		except: plot = ''
		try:
			(href, title) = re.compile('<h4><a href="(.*?)">(.*?)</a></h4>').findall(curli)[0]
			title = strip_html(title)
			plot  = strip_html(plot)
			date  = strip_html(date)
			#xbmc.output('--------------------------')
			#xbmc.output(' href = %s'%href)
			#xbmc.output('title = %s'%title)
			#xbmc.output(' plot = %s'%plot)
			#xbmc.output(' date = %s'%date)
			#xbmc.output('thumb = %s'%thumb)
			#xbmc.output('--------------------------')
			uri = sys.argv[0] + '?mode=play'
			uri += '&href='+urllib.quote_plus(href)
			item = xbmcgui.ListItem(title, iconImage=thumb, thumbnailImage=thumb)
			item.setInfo(type='video', infoLabels={'title':title,'genre':name,'plot':plot,'studio':'TV.EXPERT.RU / %s'%date,'plotoutline':date})
			item.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem(h,uri,item)
		except Exception, e:
			xbmc.output('ERROR insert element: %s' % e)

	try:
		snav = re.compile('<span class="previous_pages">(.*?)</span>', re.DOTALL).findall(http)
		if len(snav) != 0:
			(navhref, navtitle) = re.compile('<a href="(.*?)">(.*?)</a>').findall(snav[0])[0]
			li = xbmcgui.ListItem(navtitle, iconImage = icon, thumbnailImage = icon)
			uri = sys.argv[0] + '?mode=getprogram'
			uri += '&href='+urllib.quote_plus(navhref)
			uri += '&name='+urllib.quote_plus(name)
			xbmcplugin.addDirectoryItem(h, uri, li, True)
	except:
		pass

	xbmcplugin.endOfDirectory(h)




def play(params):
	try:
		http = GET(urllib.unquote_plus(params['href']))
		u = re.compile('files.push\("(.*?)"\);').findall(http)[0]
		i = xbmcgui.ListItem(path = 'http://www.expert.ru' + u)
		xbmcplugin.setResolvedUrl(h, True, i)
	except Exception, e:
		showMessage('НЕ МОГУ ВОСПРОИЗВЕСТИ', e, 3000)
		return False


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

params = get_params(sys.argv[2])

mode   = None
func   = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	getitems(params)

if (mode != None):
	try:
		func = globals()[mode]
	except:
		pass
	if func: func(params)

try:
	import adanalytics
	adanalytics.adIO(sys.argv[0], sys.argv[1], sys.argv[2])
except Exception, e:
	xbmc.output('Exception in adIO: %s' % e)
