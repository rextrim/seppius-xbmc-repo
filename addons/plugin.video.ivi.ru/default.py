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
import xbmc, xbmcgui, xbmcplugin, urllib2, urllib, re, string, sys, os, traceback, random
from urllib import urlretrieve, urlcleanup

Header_UserAgent = "Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60"
Header_Host      = "www.ivi.ru"
Header_AccLang   = "ru, *"

swfplayer_url    = 'http://www.ivi.ru/video/player/'
ivihomepage_url  = 'http://www.ivi.ru'
FlashAuth_key    = 'Basic Zmxhc2hfcGxheWVyOmZsYXNoX3BsYXllcg=='
parser_api	 = 'http://api.digitalaccess.ru/api/json/'
parser_host	 = 'api.digitalaccess.ru'

thumb = os.path.join(os.getcwd(), 'icon.png')


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

def clean(name):
	remove=[('<strong>',' '),('</strong>',' '),('<span>',' '),('</span>',' '),('&amp;','&'),('&quot;','"'),('&#39;','\''),('&nbsp;',' '),('&laquo;','"'),('&raquo;', '"'),('&#151;','-'),('<nobr>',''),('</nobr>',''),('<P>',''),('</P>','')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

########################################


def ShowRoot():
	http = GET(ivihomepage_url, [('Host', Header_Host)])
	if http == None:
		return
	raw_1 = re.compile('<li class="clearfix">(.*?)</div>', re.DOTALL).findall(http)
	x = 1
	for lev1 in raw_1:
		raw_2 = re.compile('<a href="(.*?)" title=".*" class="clearfix">(.*?)<span class="white">', re.DOTALL).findall(lev1)
		if len(raw_2) > 0:
			(gu, gn) = raw_2[0]
			gn = gn.replace('\n', '').replace(' ', '')
			listitem = xbmcgui.ListItem('%s. %s'%(x, gn))
			url = '%s?mode=ShowList&url=%s&name=%s'%(sys.argv[0], urllib.quote_plus(ivihomepage_url + gu), urllib.quote_plus(gn))
			xbmcplugin.addDirectoryItem(handle, url, listitem, True)
			y = 1
			raw_2 = re.compile('<li>\s*<a href="(.*?)" title="">(.*?)</a>\s*</li>').findall(lev1)
			for rurl, subname in raw_2:
				cgn = '%s : %s'%(gn,subname)
				listitem = xbmcgui.ListItem('%s.%s. %s'%(str(x),str(y),cgn))
				url = '%s?mode=ShowList&url=%s&name=%s'%(sys.argv[0], urllib.quote_plus(ivihomepage_url + rurl), urllib.quote_plus(cgn))
				xbmcplugin.addDirectoryItem(handle, url, listitem, True)
				y += 1
		x += 1


def ShowList(work_url, genre):
	http = GET(work_url, [('Referer', ivihomepage_url)])
	if http == None:
		return False
	r1 = re.compile('<div class="preview">(.*?)<div class="clearfix py024">', re.DOTALL).findall(http)
	if len(r1) == 0:
		r1 = re.compile('<div class="preview">(.*?)</p>', re.DOTALL).findall(http)
	x = 1
	if len(r1) == 0:
		return False
	for l1 in r1:
		#xbmc.output(l1)
		rate = 0
		rrate = re.compile('<span class="rate png">(.*?)</span>').findall(l1)
		if len(rrate) > 0: rate = int(rrate[0])
		pupt = re.compile('<a href="(.*?)" title="">(.*?)</a>').findall(l1)
		if len(pupt) == 0:
			pupt = re.compile('<a href="(.*?)" title="(.*?)" class="clearfix">').findall(l1)
		(pu, pt) = pupt[0]
		if len(pt) == 0:
			pupt2 = re.compile('<span class="title clearfix">(.*?)</span>').findall(l1)
			pt = pupt2[0]
		duration = '0'
		rduration = re.compile('<span class="duration">(.*?)</span>').findall(l1)
		if len(rduration) > 0: duration = rduration[0]
		img = thumb
		rimg = re.compile('<img src="(.*?)"').findall(l1)
		if len(rimg) > 0: img = rimg[0]
		countyear = None
		rcountyear = re.compile('<span class="info-county-year">(.*?)</span>').findall(l1)
		if len(rcountyear) > 0: countyear = rcountyear[0]
		plot = ''
		rplot = re.compile('<span class="description clearfix">(.*?)</span>').findall(l1)
		if len(rplot) > 0: plot = rplot[0]
		#xbmc.output('     rate = %s'%rate)
		#xbmc.output('       pu = %s'%pu)
		#xbmc.output('       pt = %s'%pt)
		#xbmc.output(' duration = %s'%duration)
		#xbmc.output('      img = %s'%img)
		#xbmc.output('countyear = %s'%countyear)
		#xbmc.output('     plot = %s'%plot)
		pt = clean(pt)
		Title = '%s. %s (%s)'%(x,pt,countyear)
		if countyear == None: Title = '%s. %s'%(x,pt)
		Plot = '%s "%s"\n%s'%(genre,pt,plot)
		listitem = xbmcgui.ListItem(Title, iconImage = img, thumbnailImage = img)
		listitem.setInfo(type = 'Video', infoLabels = {
			'genre':	genre,
			'playcount':	rate,
			'director':	'IVI.RU',
			'title':	Title,
			'duration':	duration,
			'studio':	countyear,
			'premiered':	countyear,
			'aired':	countyear,
			'plotoutline':	pt,
			'plot':		Plot })
		if (pu.find('/collection/') == -1):
			mode = 'PlayURL'
			isDir = False
		else:
			mode = 'ShowList'
			isDir = True
		url = '%s?mode=%s&url=%s&name=%s&img=%s'%(sys.argv[0], mode, urllib.quote_plus(ivihomepage_url + pu), urllib.quote_plus(Title), urllib.quote_plus(img))
		xbmcplugin.addDirectoryItem(handle, url, listitem, isDir)
		x = x+1

	try:
		pages_block = re.compile('<ul class="pages">(.*?)</ul>', re.DOTALL).findall(http)
		raw_pg = re.compile('<li><a href="(.+?)">(.+?)</a></li>').findall(pages_block[0])
		for pg_URL, pg_NAME in raw_pg:
				pg_URL   = pg_URL.replace('amp;', '')
				pg_NAME  = '> Страница ' + pg_NAME
				listitem = xbmcgui.ListItem(pg_NAME)
				url = sys.argv[0] + "?mode=showroot&url=" + urllib.quote_plus(pg_URL)
				url = '%s?mode=ShowList&url=%s&name=%s'%(sys.argv[0], urllib.quote_plus(ivihomepage_url + pg_URL), urllib.quote_plus(genre))
				xbmcplugin.addDirectoryItem(handle, url, listitem, True)
	except:
		xbmc.output('get_root -> Except in add pages!')
	return True


def fnkeys(fnkeys_data):
	return re.compile('{"url": "(.*?)", "content_format": "(.*?)", "id": (.*?)}').findall(fnkeys_data)

def REDIR(target_url, target_header):
	try:
		req = urllib2.Request(target_url)
		req.add_header('User-Agent',      Header_UserAgent)
		req.add_header('Accept-Language', Header_AccLang)
		for headkey, headval in target_header:
			req.add_header(headkey, headval)
		opener = urllib2.build_opener()
		f = opener.open(req)
		real_url = f.url
		f.close()
		return real_url
	except:
		dialog = xbmcgui.Dialog()
		dialog.ok('WARNING', 'Using a "SWF_Player" of emergency. Attempt...')
		return 'http://www.ivi.ru/images/da/player1.53.swf'

def GET(target_url, target_header, postdata = None):
	try:
		req = urllib2.Request(target_url, postdata)
		req.add_header('User-Agent',      Header_UserAgent)
		req.add_header('Accept-Language', Header_AccLang)
		for headkey, headval in target_header:
			req.add_header(headkey, headval)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		return a
	except:
		dialog = xbmcgui.Dialog()
		dialog.ok('ERROR on GET', 'Cannot GET URL %s' % target_url)
		return None

def PlayURL(wurl, img, name):
	print 'PlayURL(%s, %s, %s)'%(wurl, img, name)
	dialog = xbmcgui.Dialog()
	http = GET(wurl, [('Host', Header_Host)])
	#print http
	if http == None:
		dialog.ok('ERROR in GET', 'http == None. Sorry.')
		return
	raw_vid = re.compile('"videoId": (.[0-9]*)').findall(http)
	if len(raw_vid) == 0:
		dialog.ok('ERROR in DATA', 'len(raw_vid) == 0. Sorry.')
		return
	parser_videoId = raw_vid[0]
	if parser_videoId == None:
		dialog.ok('ERROR in DATA', '"videoId" - not found. Sorry.')
	post_data   = '{"method":"da.content.get","params":["' + parser_videoId + '",{"site":1}]}'
	acc_workurl = parser_api + '?r=' + str(random.uniform(1, 840))
	real_swf_url = REDIR(swfplayer_url, [('Referer', ivihomepage_url), ('Host', Header_Host)])
	headata = [('Referer', real_swf_url),('Host',parser_host),('Content-Type','application/x-www-form-urlencoded'),('FlashAuth',FlashAuth_key)]
	a = GET(acc_workurl, headata, post_data)
	if a == None:
		return
	raw_filesdata = fnkeys(re.compile('"files"\: \[(.*?)\],').findall(a)[0])

	selected = -1
	spcn = len(raw_filesdata)
	for x in range(spcn):
		if raw_filesdata[x][1] == 'FLV-hi':
			selected = x
	if selected == -1:
		for x in range(spcn):
			if raw_filesdata[x][1] == 'FLV-lo':
				selected = x

	if selected < 0:
		return

	#list = []
	#spcn = len(raw_filesdata)
	#if spcn == 1:
	#	selected = 0
	#else:
	#	for x in range(spcn):
	#		list.append(raw_filesdata[x][1])
	#	selected = dialog.select('Quality?', list)
	#if selected < 0:
	#	return
	video_mp4url  = raw_filesdata[selected][0]
	video_quality = raw_filesdata[selected][1]
	video_id      = raw_filesdata[selected][2]

	#print('video_mp4url  = %s' % video_mp4url)
	#print('video_quality = %s' % video_quality)
	#print('video_id      = %s' % video_id)

	listitem = xbmcgui.ListItem(name, iconImage = img, thumbnailImage = img)

	h_1 = '|Referer=' + urllib.quote_plus(real_swf_url)
	h_2 = '&User-Agent=' + urllib.quote_plus('Opera/9.80 (X11; Linux i686; U; ru) Presto/2.6.30 Version/10.70')
	h_3 = '&Accept=' + urllib.quote_plus('text/html, application/xml, application/xhtml+xml, */*')
	h_4 = '&Accept-Language=' + urllib.quote_plus('ru,en;q=0.9')
	h_5 = '&Accept-Charset=' + urllib.quote_plus('iso-8859-1, utf-8, utf-16, *;q=0.1')
	h_6 = '&Accept-Encoding=' + urllib.quote_plus('deflate, gzip, x-gzip, identity, *;q=0')
	h_7 = '&Connection=' + urllib.quote_plus('Keep-Alive')

	xbmc.Player().play(video_mp4url + h_1 + h_2 + h_3 + h_4 + h_5 + h_6 + h_7, listitem)

def AddSearch():
	listitem = xbmcgui.ListItem('* ПОИСК *')
	url = '%s?mode=Search&name=%s'%(sys.argv[0], 'Поиск')
	xbmcplugin.addDirectoryItem(handle, url, listitem, True)

handle = int(sys.argv[1])
params = get_params()

mode = 'ShowRoot'
url  = 'http://www.ivi.ru/videos/'
name = 'None'


try:
	mode  = urllib.unquote_plus(params["mode"])
except:
	pass
try:
	url   = urllib.unquote_plus(params["url"])
except:
	pass
try:
	name  = urllib.unquote_plus(params["name"])
except:
	pass

if mode == 'ShowRoot':
	ShowRoot()
	AddSearch()
	xbmcplugin.endOfDirectory(handle)

elif mode == 'ShowList':
	ShowList(url, name)
	AddSearch()
	xbmcplugin.endOfDirectory(handle)

elif mode == 'PlayURL':
	img = thumb
	try:
		img  = urllib.unquote_plus(params["img"])
	except:
		pass
	PlayURL(url, img, name)

elif mode == 'Search':

	pass_keyboard = xbmc.Keyboard()
	pass_keyboard.setHeading('Что ищем?')
	pass_keyboard.doModal()
	if (pass_keyboard.isConfirmed()):
		SearchStr = pass_keyboard.getText()
		dialog = xbmcgui.Dialog()
		r = ShowList('http://www.ivi.ru/search/simple/?q=' + urllib.quote_plus(SearchStr), 'Поиск')
		if r: xbmcplugin.endOfDirectory(handle)
	else:
		exit

try:
	import adanalytics
	adanalytics.adIO(sys.argv[0], sys.argv[1], sys.argv[2])
except:
	xbmc.output(' === unhandled exception in adIO === ')
	pass
