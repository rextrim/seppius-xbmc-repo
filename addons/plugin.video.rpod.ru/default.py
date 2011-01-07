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
import urllib2, re, xbmc, xbmcgui, xbmcplugin, os, urllib, urllib2, socket
import xml.dom.minidom

socket.setdefaulttimeout(12)

h = int(sys.argv[1])
icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

def strip_html(text):
	def fixup(m):
		text = m.group(0)
		if text[:1] == "<":
			if text[1:3] == 'br':
				return '\n'
			else:
				return ""
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

def GET(url):
	try:
		print 'def GET(%s):'%url
		req = urllib2.Request(url)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		return a
	except:
		showMessage('Не могу открыть URL', url)
		return None

def ROOT():

	def add_podcast(name, url):
		i = xbmcgui.ListItem(name, iconImage = icon, thumbnailImage = icon)
		u  = '%s?mode=podcasts&url=%s&name=%s' % (sys.argv[0], urllib.quote_plus(url), urllib.quote_plus(name))
		xbmcplugin.addDirectoryItem(h, u, i, True)

	def add_xmlpodcast(name, url):
		i = xbmcgui.ListItem(name, iconImage = icon, thumbnailImage = icon)
		u  = '%s?mode=xmlpodcasts&url=%s&name=%s' % (sys.argv[0], urllib.quote_plus(url), urllib.quote_plus(name))
		xbmcplugin.addDirectoryItem(h, u, i, True)

	add_podcast('Подкасты : Личные (по популярности)',        'http://rpod.ru/podcasts/?sortby=subscribers')
	add_podcast('Подкасты : Личные (по дате обновления)',     'http://rpod.ru/podcasts/?sortby=last')
	add_podcast('Подкасты : Личные (по дате основания)',      'http://rpod.ru/podcasts/?sortby=first')
	add_podcast('Подкасты : Сообщества (по популярности)',    'http://rpod.ru/communities/?sortby=subscribers')
	add_podcast('Подкасты : Сообщества (по дате обновления)', 'http://rpod.ru/communities/?sortby=last')
	add_podcast('Подкасты : Сообщества (по дате основания)',  'http://rpod.ru/communities/?sortby=first')
	add_podcast('Подкасты : Каналы (по популярности)',        'http://rpod.ru/channels/?sortby=subscribers')
	add_podcast('Подкасты : Каналы (по дате обновления)',     'http://rpod.ru/channels/?sortby=last')
	add_podcast('Подкасты : Каналы (по дате основания)',      'http://rpod.ru/channels/?sortby=first')

	add_xmlpodcast('Свежие аудиоподкасты','http://rpod.ru/audio/rss.xml')
	add_xmlpodcast('Свежие видеоподкасты','http://rpod.ru/video/rss.xml')

	xbmcplugin.endOfDirectory(h)


def podcasts(params):
	url  = urllib.unquote_plus(params['url'])
	name = urllib.unquote_plus(params['name'])
	http = GET(url)
	if http == None: return False
	rows = re.compile('<a\s*amber\s*=\s*"(.+?)"\s*href\s*=\s*"(.+?)"\s*>(.+?)</a>').findall(http)
	for amber, href, name in rows:
		thumb = icon
		rimg = re.compile('<img\s*src\s*=\s*"(.+?)".+?amber\s*=\s*"%s"\s*class\s*=\s*"avatar"\s*>'%amber).findall(http)
		if len(rimg) > 0: thumb = rimg[0]
		i = xbmcgui.ListItem(name, iconImage = thumb, thumbnailImage = thumb)
		u  = '%s?mode=xmlpodcasts&url=%s&name=%s' % (sys.argv[0], urllib.quote_plus(href + 'rss.xml'), urllib.quote_plus(name))
		xbmcplugin.addDirectoryItem(h, u, i, True)
	xbmcplugin.endOfDirectory(h)



def xmlpodcasts(params):
	url  = urllib.unquote_plus(params['url'])
	name = urllib.unquote_plus(params['name'])
	xbmc.output('xmlpodcasts ->  url = %s'%url)
	xbmc.output('xmlpodcasts -> name = %s'%name)
	http = GET(url)
	if http == None: return False
	document = xml.dom.minidom.parseString(http)
	for item in document.getElementsByTagName('item'):
		try:
			title = item.getElementsByTagName('title')[0].firstChild.data
		except:
			title = None
		if title != None:
			info = {'title':title}
			riimg = item.getElementsByTagName('itunes:image')
			if len(riimg) > 0:
				try:    thumb = riimg[0].getAttribute('href')
				except: thumb = icon
			i = xbmcgui.ListItem(title, iconImage = thumb, thumbnailImage = thumb)
			try:
				link = item.getElementsByTagName('link')[0].firstChild.data
				link = link.encode('utf-8','replace')
			except: link = None
			try:
				guid = item.getElementsByTagName('guid')[0].firstChild.data
				guid = guid.encode('utf-8','replace')
			except: guid = None
			try:
				author = item.getElementsByTagName('author')[0].firstChild.data
				author = author.encode('utf-8','replace')
			except: author = None
			try:
				pubDate = item.getElementsByTagName('pubDate')[0].firstChild.data
				pubDate = pubDate.encode('utf-8','replace')
			except: pubDate = None
			try:
				description = item.getElementsByTagName('description')[0].firstChild.data
				description = strip_html(description.encode('utf-8','replace'))
			except: description = None
			try:
				iduration = item.getElementsByTagName('itunes:duration')[0].firstChild.data
				iduration = iduration.encode('utf-8', 'replace')
			except: iduration = None
			try:
				bitrate = item.getElementsByTagName('bitrate')[0].firstChild.data
				bitrate = bitrate.encode('utf-8', 'replace')
			except: bitrate = None
			enclosure = item.getElementsByTagName('enclosure')
			if len(enclosure) > 0:
				try:
					media_length = enclosure[0].getAttribute('length')
					info['size'] = int(media_length)
				except: pass
				item_type = 'video'
				try:
					media_type = enclosure[0].getAttribute('type')
					media_type = media_type.encode('utf-8', 'replace')
					i.setProperty('mimetype',     media_type)
					if 'audio' in media_type: item_type = 'music'
				except:
					media_type = None
					item_type = 'video'
				if item_type == 'video':
					info['genre'] = 'ВИДЕО-ПОДКАСТ'
					info['title'] = '[V] %s'%(info['title'])
					if        link != None: info['studio']   = link
					if        guid != None: info['writer']   = guid
					if      author != None: info['director'] = author
					if     pubDate != None: info['date']     = pubDate
					if description != None: info['plot']     = description
					if   iduration != None: info['duration'] = iduration
					if     bitrate != None:
						info['plotoutline'] = 'Битрейт %skbps '%bitrate
					if  media_type != None:
						info['plotoutline'] = 'Формат: %s '%media_type
				else:
					info['genre'] = 'АУДИО-ПОДКАСТ'
					info['title'] = '[A] %s'%(info['title'])
					if description != None: info['lyrics'] = description
					if      author != None: info['artist'] = author
					if        link != None: info['album']  = link
					if description != None: info['lyrics'] = description
					try:
						(mins, secs) = iduration.split(':')
						info['duration'] = int(secs) + int(mins)*60
					except: pass
				if bitrate != None:
					info['title'] = '%s [%skbps]'%(info['title'], bitrate)
				try:
					media_url    = enclosure[0].getAttribute('url')
					i = xbmcgui.ListItem(title, iconImage = thumb, thumbnailImage = thumb)
					i.setInfo(type = item_type, infoLabels = info)
					xbmcplugin.addDirectoryItem(h, media_url.encode('utf-8','replace'), i)
				except: pass

	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_UNSORTED)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DURATION)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_GENRE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(h)


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

params=get_params(sys.argv[2])

mode = None
ifac = None

try:
	mode = urllib.unquote_plus(params['mode'])
	xbmc.output('### INITIAL MODE = %s' % mode)
except:
	ROOT()
	exit

if mode != None:
	f = None
	try:
		f = globals()[mode]
	except:
		showMessage('ERROR','НЕТ ФУНКЦИИ [%s]' % mode,5000)
		xbmc.output('### ERROR. НЕ НАЙДЕНА ФУНКЦИЯ [%s]' % mode)
		pass
	if f: f(params)
else:
	ROOT()
