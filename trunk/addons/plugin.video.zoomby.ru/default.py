#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *   Copyright (с) 2011 Khrysev Dmitry, x86demon@gmail.com
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
# *  http://www.gnu.org/licenses/gpl.html
# */

import urllib2, re, string, xbmc, xbmcgui, xbmcplugin, os, urllib, random
import binascii
import xml.dom.minidom

h = int(sys.argv[1])

PLUGIN_NAME   = 'ZOOMBY.RU'
SITE_HOSTNAME = 'www.zoomby.ru'
SITEPREF      = 'http://%s' % SITE_HOSTNAME
SITE_URL      = SITEPREF + '/'

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))


def clean(name):
	remove=[('&nbsp;', ''), ('&mdash;', '-'), ('&hellip;', '.'), ('&ndash;', '-'), ('&laquo;', '"'), ('&ldquo;', '"'), ('&ldquo;', '"'), ('&raquo;', '"'), ('&quot;', '"')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))


def Get(url, ref=None, post=None):
	xbmc.output('[%s] Get(url=%s, ref=%s)' % (PLUGIN_NAME, url, ref))
	if url.find('http://') == -1:
		url = SITEPREF + url
	request = urllib2.Request(url, post)
	request.add_header('User-Agent', 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00')
	request.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
	request.add_header('Accept-Language', 'ru,en;q=0.9')
	if post != None:
		request.add_header('Content-Type', 'application/x-www-form-urlencoded')
	if ref != None:
		request.add_header('Referer', ref)
	o = urllib2.urlopen(request)
	http = o.read()
	o.close()
	return http


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
	if len(param) > 0:
		for cur in param:
			param[cur] = urllib.unquote_plus(param[cur])
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


def decrypt(hex_arg1, hex_arg2):
	def bin_add(_arg1, _arg2, _arg3):
		_local7 = 0
		_local6 = 0
		_local4 = ''
		while _local7 < len(_arg1):
			_local8 = int(_arg1[_local7]) + int(_arg2[_local6])
			if _local8 == 2: _local4 += '0'
			else: _local4 += str(_local8)
			_local6 += 1
			if _local6 > _arg3: _local6 = 0
			_local7 += 1
		return _local4
	def unpack_B8(_arg1):
		def Denary2Binary(n): # convert denary integer n to binary string bStr
			bStr = ''
			if n < 0:  raise ValueError, "must be a positive integer"
			if n == 0: return '00000000'
			i = 8
			while i > 0:
				bStr = str(n % 2) + bStr
				n = n >> 1
				i = i-1
			return bStr
		return Denary2Binary(_arg1)
	def splitCount(s, count):
		return [''.join(x) for x in zip(*[list(s[z::count]) for z in range(count)])]
	chr_arg1 = binascii.unhexlify(hex_arg1)
	bin_arg1 = ''
	for cur_chr in chr_arg1: bin_arg1 += unpack_B8(ord(cur_chr))
	bin_arg2 = ''
	for cur_chr in hex_arg2: bin_arg2 += unpack_B8(ord(cur_chr))
	_local7 = bin_add(bin_arg1, bin_arg2, len(hex_arg2))
	_local5 = ""
	x_loc = splitCount(_local7, 8)
	for cur_loc in x_loc: _local5 += chr(int(cur_loc, 2))
	return _local5


def WATCH(url):
	xbmc.output('[%s] WATCH(%s)' % (PLUGIN_NAME, url))
	http  = Get(url)
	flashvars = re.compile('video: "(.*?)",').findall(http)[0]
	keys = flashvars.split('/')
	cur_key = keys[len(keys)-2]
	SMILPATH = 'http://www.zoomby.ru' + flashvars
	REFE     = 'http://www.zoomby.ru' + url
	http2 = decrypt(Get(SMILPATH, REFE), cur_key)
	http2 = re.compile('(<smil.*?</smil>)', re.DOTALL).findall(http2)[0]

	print http2

	Dom     = xml.dom.minidom.parseString(http2.replace('&','&amp;'))
	switchs = Dom.getElementsByTagName('switch')
	videos = switchs[0].getElementsByTagName('video')
	pda = []
	labela = []
	for video in videos:
		video_pd      = video.getAttribute('stream')
		video_sysbit  = video.getAttribute('system-bitrate').encode('utf8')
		video_label   = video.getAttribute('label').encode('utf8')
		pda.append(video_pd.split('?')[0])
		labela.append('%s (%s)' % (video_label, video_sysbit))
	s = xbmcgui.Dialog().select('Качество?', labela)
	if s < 0:
		return False
	uri  = pda[s]

	if uri.find('http://') != -1:


		uri += '|Referer=%s'    % urllib.quote_plus(REFE)
		uri += '&User-Agent=%s' % urllib.quote_plus('Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00')
		i = xbmcgui.ListItem(path = uri)
		xbmcplugin.setResolvedUrl(h, True, i)



params = get_params(sys.argv[2])
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
