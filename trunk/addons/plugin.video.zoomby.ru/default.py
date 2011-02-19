#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *	  Copyright (C) 2010 Kostynoy S. aka Seppius
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

import urllib2, re, string, xbmc, xbmcgui, xbmcplugin, os, urllib, cookielib, random

h = int(sys.argv[1])

PLUGIN_NAME   = 'ZOOMBY.RU'
SITE_HOSTNAME = 'www.zoomby.ru'
SITEPREF      = 'http://%s' % SITE_HOSTNAME
SITE_URL      = SITEPREF + '/'

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))
phpsessid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin_video_zoomby.sess')
thumb = os.path.join( os.getcwd(), "icon.png" )

def clean(name):
	remove=[('&nbsp;', ''), ('&mdash;', '-'), ('&hellip;', '.'), ('&ndash;', '-'), ('&laquo;', '"'), ('&ldquo;', '"'), ('&ldquo;', '"'), ('&raquo;', '"'), ('&quot;', '"')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def showMessage(heading, message, times = 3000):
	#heading = heading.encode('utf-8')
	#message = message.encode('utf-8')
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))



def Get(url, ref=None, post=None):
	xbmc.output('[%s] Get(url=%s, ref=%s)' % (PLUGIN_NAME, url, ref))
	url = SITEPREF + url
	cj = cookielib.CookieJar()
	h  = urllib2.HTTPCookieProcessor(cj)
	opener = urllib2.build_opener(h)
	urllib2.install_opener(opener)
	request = urllib2.Request(url, post)
	request.add_header('User-Agent', 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00')
	request.add_header('Host', SITE_HOSTNAME)
	request.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
	request.add_header('Accept-Language', 'ru,en;q=0.9')
	if post != None:
		request.add_header('Content-Type', 'application/x-www-form-urlencoded')
	if ref != None:
		request.add_header('Referer', ref)
	if os.path.isfile(phpsessid_file):
		fh = open(phpsessid_file, 'r')
		phpsessid = fh.read()
		fh.close()
		request.add_header('Cookie', 'CGISESSID=' + phpsessid)
	o = urllib2.urlopen(request)
	for index, cookie in enumerate(cj):
		cookraw = re.compile('<Cookie CGISESSID=(.*?) for.*/>').findall(str(cookie))
		if len(cookraw) > 0:
			fh = open(phpsessid_file, 'w')
			fh.write(cookraw[0])
			fh.close()
	http = o.read()
	o.close()
	return http


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

def GetAlphabetList(http):
	raw1 = re.compile('<ul class="afltr">(.*?)</ul>', re.DOTALL).findall(http)
	if len(raw1) != 0:
		raw2 = re.compile('<a href="(.*?)">(.*?)</a>').findall(raw1[0])
		if len(raw2) != 0:
			  for grp_url, grp_name in raw2:
				Title = '%s : %s' % ('Алфавитный указатель', grp_name)
				listitem = xbmcgui.ListItem(Title)
				listitem.setInfo(type = "Video", infoLabels = {"Title":Title} )
				url = sys.argv[0] + '?mode=OpenAlphabet&url=' + urllib.quote_plus(grp_url) + '&title=' + urllib.quote_plus(grp_name)
				xbmcplugin.addDirectoryItem(h, url, listitem, True)



def AddSearch(http):
	rs1 = re.compile('<\s*input\s*type\s*=\s*"hidden"\s*value\s*=\s*"(.+?)"\s*name\s*=\s*"token"\s*>').findall(http)
	if len(rs1) > 0:
		listitem = xbmcgui.ListItem('ПОИСК')
		url = sys.argv[0] + '?mode=SEARCH&token=' + urllib.quote_plus(rs1[0])
		xbmcplugin.addDirectoryItem(h, url, listitem, True)
	else:
		xbmc.executebuiltin('ПОИСК НЕ ДОБАВЛЕН', 'Не найден token в коде страницы')


def SEARCH(token):
	pass_keyboard = xbmc.Keyboard()
	pass_keyboard.setHeading('Что ищем?')
	pass_keyboard.doModal()
	if (pass_keyboard.isConfirmed()):
		SearchStr = pass_keyboard.getText()
		post = 'token=%s&q=%s&x=%d&y=%d'%(token, urllib.quote_plus(SearchStr), random.randint(0, 50), random.randint(0, 30))
		http = Get(url='/search', ref='http://www.zoomby.ru/search', post=post)
		if http == None:
			return False
		s3 = re.compile('<div class="preview01cont">(.*?)<div', re.DOTALL).findall(http)
		for RB in s3:
			hrf = re.compile('<a href="(.*?)"').findall(RB)[0]
			img = re.compile('<img src="(.*?)"').findall(RB)[0]
			txt = re.compile('title="(.*?)"').findall(RB)[0].replace('Смотреть ', '')
			i = xbmcgui.ListItem(txt, iconImage=img, thumbnailImage=img)
			u  = sys.argv[0] + '?mode=GetSeries'
			u += '&url=%s'   %urllib.quote_plus(hrf)
			u += '&genre=%s' %urllib.quote_plus('Поиск')
			u += '&studio=%s'%urllib.quote_plus(txt)
			xbmcplugin.addDirectoryItem(h, u, i, True)
		if len(s3) > 0:
			xbmcplugin.endOfDirectory(h)
	else:
		return False


def ShowRoot(url):
	http = Get(url)
	if http == None:
		return
	AddSearch(http)
	raw1 = re.compile('<ul id="mainmenucls" class="mainmenu">(.*?)</ul>', re.DOTALL).findall(http)
	if len(raw1) != 0:
		raw2 = re.compile('<a href="(.*?)">(.*?)</a>\s*<div class="msubmenu">(.*?)</div>', re.DOTALL).findall(raw1[0])
		if len(raw2) != 0:
			x = 1
			for grp_url, grp_name, grp_block in raw2:
				Title = '%s. %s (Все)' % (str(x), grp_name)
				listitem = xbmcgui.ListItem(Title) # , iconImage = Thumb, thumbnailImage = Thumb
				listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
				url = sys.argv[0] + '?mode=GetList&url=' + urllib.quote_plus(grp_url) + '&genre=' + urllib.quote_plus(grp_name)
				xbmcplugin.addDirectoryItem(h, url, listitem, True)
				raw3 = re.compile('<a href="(.*?)">(.*?)</a>').findall(grp_block)
				if len(raw3) != 0:
					y = 1
					for row_url, row_name in raw3:
						Title = '%s. %s. %s : %s' % (str(x), str(y), grp_name, row_name)
						listitem = xbmcgui.ListItem(Title) # , iconImage = Thumb, thumbnailImage = Thumb
						listitem.setInfo(type = "Video", infoLabels = {"Title":Title} )
						url = sys.argv[0] + '?mode=GetList&url=' + urllib.quote_plus(row_url) + '&genre=' + urllib.quote_plus(grp_name+' / '+row_name)
						xbmcplugin.addDirectoryItem(h, url, listitem, True)
						y = y + 1
				x = x + 1

	def AddTags(row):
		p1 = re.compile('<a href="(.+?)".+?</a>').findall(row)
		for p in p1:
			t = p[1:]
			t = t.replace('/',' : ')
			listitem = xbmcgui.ListItem(t) # , iconImage = Thumb, thumbnailImage = Thumb
			url = sys.argv[0] + '?mode=GetList&url=' + urllib.quote_plus(p) + '&genre=' + urllib.quote_plus(t)
			xbmcplugin.addDirectoryItem(h, url, listitem, True)

	raw1 = re.compile('<div id="channels-studios">(.+?)</div>', re.DOTALL).findall(http)
	if len(raw1) != 0:
		AddTags(raw1[0])
	raw1 = re.compile('<div id="tags">(.+?)</div>', re.DOTALL).findall(http)
	if len(raw1) != 0:
		AddTags(raw1[0])

	GetAlphabetList(http)
	xbmcplugin.endOfDirectory(h)

def OpenAlphabetList(url, title):
	http = GetList(url, genre)
	if http != None:
		GetAlphabetList(http)
	xbmcplugin.endOfDirectory(h)


def GetList(url, genre = 'Фильм'):
	xbmc.output('[%s] GetList(%s, %s)' % (PLUGIN_NAME, url, genre))
	CurPg = 1
	Fic = 1
	while Fic > 0:
			s3 = re.compile('<div class="preview01cont">(.*?)<div', re.DOTALL).findall(Get('%s?page=%s'%(url, CurPg)))
			if len(s3) == 0: Fic = 0
			else:
				for RB in s3:
					hrf = re.compile('<a href="(.*?)"').findall(RB)[0]
					img = re.compile('<img src="(.*?)"').findall(RB)[0]
					txt = re.compile('title="(.*?)"').findall(RB)[0].replace('Смотреть ', '')
					i = xbmcgui.ListItem(txt, iconImage=img, thumbnailImage=img)
					u  = sys.argv[0] + '?mode=GetSeries'
					u += '&url=%s'   %urllib.quote_plus(hrf)
					u += '&genre=%s' %urllib.quote_plus(genre)
					u += '&studio=%s'%urllib.quote_plus(txt)
					xbmcplugin.addDirectoryItem(h, u, i, True)
					Fic += 1
			CurPg += 1
	xbmcplugin.endOfDirectory(h)


def GetSeries(url, genre = 'Фильм', studio = 'http://www.zoomby.ru/'):
	xbmc.output('[%s] GetSeries(%s, %s, %s)' % (PLUGIN_NAME, url, genre, studio))
	if 'watch' in url:
		rID = re.compile('/(.[0-9]+)').findall(url)
		if len(rID) > 0:
			ID = rID[0]
			CurPg = 1
			Fic = 1
			while Fic > 0:
				try:
					Fic = 0
					http = Get('/get/series/%s?p=%s'%(ID, CurPg))
					http = http.replace('\n','').replace('\t','')
					s3 = re.compile('<li><div(.*?)</div></li>').findall(http)
					if len(s3) == 0: Fic = 0
					for CS in s3:
						hrf = re.compile('<a href="(.*?)"').findall(CS)[0]
						img = re.compile('<img src="(.*?)"').findall(CS)[0]
						tim = re.compile('<span class="lenth01">(.*?)</span>').findall(CS)[0]
						txt = re.compile('<span class="txttype0.">(.*?)</span>').findall(CS)[0]
						if len(txt) == 0: txt = studio
						i = xbmcgui.ListItem(txt, iconImage=img, thumbnailImage=img)
						i.setInfo(type='Video', infoLabels={'title':txt, 'duration':tim,'genre':genre,'studio':studio})
						i.setProperty('IsPlayable', 'true')
						u  = sys.argv[0] + '?mode=WATCH'
						u += '&url=%s'%urllib.quote_plus(hrf)
						xbmcplugin.addDirectoryItem(h, u, i)
						Fic += 1
					CurPg += 1
				except:
					Fic = 0
		else:
			xbmc.output('[%s] GetSeries ERR: Can not find digital ID code!' % (PLUGIN_NAME))
			showMessage('ОШИБКА', 'Не найден код сюжета в переданной URL')
	else:
		xbmc.output('[%s] GetSeries ERR: "watch" not found! ' % (PLUGIN_NAME))
		showMessage('ОШИБКА', 'Нет "watch" в переданной URL')
	xbmcplugin.endOfDirectory(h)






def WATCH(url):
	import xml.dom.minidom
	xbmc.output('[%s] WATCH(%s)' % (PLUGIN_NAME, url))

	http  = Get(url)
	embed = re.compile('<embed(.*?)</embed>', re.DOTALL).findall(http)[0]
	swf   = re.compile('src="(.*?)"').findall(embed)[0]
	getplaylist = re.compile('flashVars="video=(.*?)&.*"').findall(embed)[0]
	http2 = Get(getplaylist, swf)

	Dom     = xml.dom.minidom.parseString(http2)
	switchs = Dom.getElementsByTagName('switch')

	rtmp       = switchs[0].getAttribute('rtmp')
	start_time = switchs[0].getAttribute('start_time')
	title      = switchs[0].getAttribute('title').encode('utf8')
	descr      = switchs[0].getAttribute('descr').encode('utf8')
	rating     = switchs[0].getAttribute('rating')
	content_id = switchs[0].getAttribute('content_id')
	preview    = switchs[0].getAttribute('preview')
	#xbmc.output('switch -> rtmp       = %s' % rtmp)
	#xbmc.output('switch -> start_time = %s' % start_time)
	#xbmc.output('switch -> title      = %s' % title)
	#xbmc.output('switch -> descr      = %s' % descr)
	#xbmc.output('switch -> rating     = %s' % rating)
	#xbmc.output('switch -> content_id = %s' % content_id)
	#xbmc.output('switch -> preview    = %s' % preview)
	videos = switchs[0].getElementsByTagName('video')

	pda = []
	signa = []
	labela = []
	for video in videos:
		video_rtmp    = video.getAttribute('rtmp')
		video_pd      = video.getAttribute('pd')
		video_sysbit  = video.getAttribute('system-bitrate')
		video_sign    = video.getAttribute('sign')
		video_label   = video.getAttribute('label').encode('utf8')
		video_primary = video.getAttribute('primary')
		#xbmc.output('video_rtmp    = %s' % video_rtmp)
		#xbmc.output('video_pd      = %s' % video_pd)
		#xbmc.output('video_sysbit  = %s' % video_sysbit)
		#xbmc.output('video_sign    = %s' % video_sign)
		#xbmc.output('video_label   = %s' % video_label)
		#xbmc.output('video_primary = %s' % video_primary)
		pda.append(video_pd)
		signa.append(video_sign)
		labela.append(video_label)

	s = xbmcgui.Dialog().select('Качество?', labela)
	if s < 0:
		return False

	uri  = pda[s]
	uri += '|Referer=%s'    % urllib.quote_plus(swf)
	uri += '&User-Agent=%s' % urllib.quote_plus('Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00')

	#print uri

	i = xbmcgui.ListItem(path = uri)
	xbmcplugin.setResolvedUrl(h, True, i)



params = get_params()
mode   = None
url    = '/'
genre  = 'Фильм'
studio = 'ZOOMBY.RU'

try: mode    = urllib.unquote_plus(params['mode'])
except: pass
try: url     = urllib.unquote_plus(params['url'])
except: pass
try: genre   = urllib.unquote_plus(params['genre'])
except: pass
try: studio  = urllib.unquote_plus(params['studio'])
except: pass


if mode == None: ShowRoot('/')
elif mode == 'GetList':      GetList(url, genre)
elif mode == 'OpenAlphabet': OpenAlphabetList(url, genre)
elif mode == 'GetSeries':    GetSeries(url, genre, studio)
elif mode == 'WATCH':        WATCH(url)
elif mode == 'SEARCH':       SEARCH(urllib.unquote_plus(params['token']))

try:
	import adanalytics
	adanalytics.adIO(sys.argv[0], sys.argv[1], sys.argv[2])
except:
	xbmc.output(' === unhandled exception in adIO === ')
	pass
