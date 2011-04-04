#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *   Copyright (с) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# *   Writer (C) 06/03/2011, Kostynoy S.A., E-mail: seppius2@gmail.com
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

import os
sys.path.append(os.path.join(os.getcwd().replace(';', ''), 'resources', 'lib'))

import urllib, urllib2, re, sys, os, httplib, time
import xbmcplugin, xbmcgui, xbmcaddon, xbmc, base64
import socket
socket.setdefaulttimeout(15)

import Cookie
import demjson
#import oauth2 as oauth
import xmlrpc2scgi


API_SERV = 'api.kinobaza.tv'


headers = { 'Content-Type' : 'application/x-www-form-urlencoded',
			'User-Agent'   : 'XBMC/10-series (Python addon; XBMC-Russia; HD-lab Team; 2011; http://www.xbmc.ru)' }

h = int(sys.argv[1])

icon     = xbmc.translatePath(os.path.join(os.path.join(os.getcwd().replace(';', '')), 'icon.png'))

img_base = os.path.join(os.getcwd().replace(';', ''), 'resources', 'icons')
ifilms   = xbmc.translatePath(os.path.join(img_base, 'films.png'))
ifriends = xbmc.translatePath(os.path.join(img_base, 'friends.png'))
icon0    = xbmc.translatePath(os.path.join(img_base, 'icon0.png'))
irecom   = xbmc.translatePath(os.path.join(img_base, 'recom.png'))
iseries  = xbmc.translatePath(os.path.join(img_base, 'series.png'))
rtorimg  = xbmc.translatePath(os.path.join(img_base, 'rtorrent.png'))

__settings__ = xbmcaddon.Addon(id = 'plugin.video.kinobaza.tv')
__language__ = __settings__.getLocalizedString

rtc_uri             = __settings__.getSetting('rtc_uri')
rtc_basepath        = __settings__.getSetting('rtc_basepath')
rtc_select          = __settings__.getSetting('rtc_select').lower()

print 'initial info...'
print 'INIT rtc_uri             = [%s]' % rtc_uri
print 'INIT rtc_basepath        = [%s]' % rtc_basepath
print 'INIT rtc_select          = [%s]' % rtc_select


def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))



rtc = xmlrpc2scgi.RTorrentXMLRPCClient(rtc_uri)
if (len(rtc_uri) < 4) or (rtc == None):
	showMessage('Ошибка подключения', 'Проверьте rTorrent URI', 5000)
	#return False
try:
	rtc_version = rtc.system.client_version()
	print 'Версия rTorrent [%s]' % rtc_version
except:
	showMessage('rTorrent не подключен!', rtc_uri, 5000)
	#return False





def KBREQUEST(target, post_params = None):

	print 'KBREQUEST -> URL         = [%s]' % target
	print 'KBREQUEST -> post_params = [%s]' % params

	if post_params == None:
		method = 'GET'
		post = None
	else:
		method = 'POST'
		post = urllib.urlencode(post_params)

	connection = httplib.HTTPConnection(API_SERV)

	PHPSESSID = __settings__.getSetting('PHPSESSID')
	if PHPSESSID != '': headers['Cookie'] = 'PHPSESSID='+PHPSESSID

	connection.request(method, target, post, headers = headers)
	response = connection.getresponse()

	try:
		sc = Cookie.SimpleCookie()
		sc.load(response.msg.getheader('Set-Cookie'))
		__settings__.setSetting('PHPSESSID', sc['PHPSESSID'].value)
	except: pass

	http = response.read()

	if response.status != 200:
		print 'response.status != 200, response.reason = %s' % response.reason
		showMessage('oops', 'response.reason = %s' % response.reason, 5000)
		print http
		return None

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
	return param



# Главное меню. Установка переходов во все функции.

def showroot(params):

#	if (access_token == '') or (access_token_secret == '') or (username == '') or (user_id == ''):
#		if (len(consumer_key) != 41) or (len(consumer_secret) != 32) or (email == '') or (password == ''):
#			showMessage('Проверьте настройки', 'Ключи consumer, e-mail и пароль')
#		else: KBAUTH()

#	li = xbmcgui.ListItem('Список доступных жанров', iconImage=icon, thumbnailImage=icon)
#	xbmcplugin.addDirectoryItem(h, '%s?mode=showgenres'%sys.argv[0], li, True)

#	li = xbmcgui.ListItem('Список доступных стран', iconImage=icon, thumbnailImage=icon)
#	xbmcplugin.addDirectoryItem(h, '%s?mode=showcountries'%sys.argv[0], li, True)

#	li = xbmcgui.ListItem('Список известных языков', iconImage=icon, thumbnailImage=icon)
#	xbmcplugin.addDirectoryItem(h, '%s?mode=showlanguages'%sys.argv[0], li, True)

#	li = xbmcgui.ListItem('Список поддерживаемых трекеров', iconImage=icon, thumbnailImage=icon)
#	xbmcplugin.addDirectoryItem(h, '%s?mode=showtrackers'%sys.argv[0], li, True)

	li = xbmcgui.ListItem('Фильмы >', iconImage=icon, thumbnailImage=icon)
	xbmcplugin.addDirectoryItem(h, '%s?mode=filmsbrowse&fields_mask=63&limit=50&offset=0&type=movie&href=%s'%(sys.argv[0], urllib.quote_plus('http://%s/films/browse'%API_SERV)), li, True)

	li = xbmcgui.ListItem('Сериалы >', iconImage=icon, thumbnailImage=icon)
	xbmcplugin.addDirectoryItem(h, '%s?mode=filmsbrowse&fields_mask=63&limit=50&offset=0&type=series&href=%s'%(sys.argv[0], urllib.quote_plus('http://%s/films/browse'%API_SERV)), li, True)

	li = xbmcgui.ListItem('Поиск фильмов', iconImage=icon, thumbnailImage=icon)
	xbmcplugin.addDirectoryItem(h, '%s?mode=filmssearch&fields_mask=63&limit=50&offset=0&type=movie&href=%s'%(sys.argv[0], urllib.quote_plus('http://%s/films/search'%API_SERV)), li, True)

	li = xbmcgui.ListItem('Поиск сериалов', iconImage=icon, thumbnailImage=icon)
	xbmcplugin.addDirectoryItem(h, '%s?mode=filmssearch&fields_mask=63&limit=50&offset=0&type=series&href=%s'%(sys.argv[0], urllib.quote_plus('http://%s/films/search'%API_SERV)), li, True)

#	user_image = 'http://media.kinobaza.tv/users/%s/avatar/150.png' % user_id
#	li = xbmcgui.ListItem('%s / %s [%s]'%(username, email, user_id), iconImage = user_image, thumbnailImage = user_image)
#	xbmcplugin.addDirectoryItem(h, '%s?mode=openuserprofile'%(sys.argv[0]), li, True)

	li = xbmcgui.ListItem('Ваши загрузки', iconImage = rtorimg, thumbnailImage = rtorimg)
	xbmcplugin.addDirectoryItem(h, '%s?mode=rtcshowdl'%(sys.argv[0]), li, True)

	xbmcplugin.endOfDirectory(h)






def openuserprofile(params):

	xbmc.output('=== def openuserprofile(%s): ==='%(params))

	try:    action = info['action']
	except: action = None

	if action == None:
		# GET /my/series/seen 						Список сериалов, которые пользователь когда-либо смотрел
		li = xbmcgui.ListItem('Список просмотренных сериалов', iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=showgenres'%sys.argv[0], li, True)

		# GET /my/subscriptions 					Возвращает список подписок на фильмы/сериалы
		li = xbmcgui.ListItem('Ваши подписки (фильмы и сериалы)', iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=showgenres'%sys.argv[0], li, True)

		# GET /my/subscriptions/films 				Возвращает список подписок на фильмы
		li = xbmcgui.ListItem('Ваши подписки на фильмы', iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=showgenres'%sys.argv[0], li, True)

		# GET /my/subscriptions/films/unreaded 		Возвращает список подписок на фильмы, которые пользователь еще не отметил просмотренными
		li = xbmcgui.ListItem('Ваши подписки на фильмы (не просмотренные)', iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=showgenres'%sys.argv[0], li, True)

		# GET /my/subscriptions/series 				Возвращает список подписок на сериалы
		li = xbmcgui.ListItem('Ваши подписки на сериалы', iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=showgenres'%sys.argv[0], li, True)

		# GET /my/trackers 							Список отслеживаемых пользователем трекеров
		li = xbmcgui.ListItem('Список отслеживаемых вами трекеров', iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=showgenres'%sys.argv[0], li, True)

		xbmcplugin.endOfDirectory(h)



def rtcshowdl(params):

	xbmc.output('=== def rtcshowdl(%s): ==='%(params))

	try:    action = params['action']
	except: action = None

	if action == None:

		dlds = []
		dlds = rtc.d.multicall('main', "d.get_name=", "d.get_hash=", "d.get_completed_chunks=", "d.get_size_chunks=", "d.get_size_files=", \
			"d.get_directory=", "d.is_active=", "d.get_complete=", "d.get_priority=", "d.is_multi_file=", "d.get_size_bytes=", \
			"d.get_custom=", "d.get_custom1=", "d.get_custom2=", "d.get_custom3=", "d.get_custom4=", "d.get_custom5=", "d.get_custom=kbmeta" )

		dlds_len = len(dlds)

		for dld in dlds:
			dld_name = dld[0]
			dld_hash = dld[1]
			dld_completed_chunks = dld[2]
			dld_size_chunks = dld[3]
			dld_percent_complete = dld_completed_chunks*100/dld_size_chunks
			dld_size_files = dld[4]
			dld_directory = dld[5]
			dld_is_active = dld[6]
			dld_complete = dld[7]
			dld_priority = dld[8]
			dld_is_multi_file = dld[9]
			dld_size_bytes = int(dld[10])
			dld_custom = dld[11]
			dld_custom1 = dld[12] # kinobaza
			dld_custom2 = dld[13] # Comment (metadata)
			dld_custom3 = dld[14]
			dld_custom4 = dld[15]
			dld_custom5 = dld[16]
			dld_kbmeta = dld[17]

			if dld_custom1 == 'kinobaza':
				#print 'dld_custom  [%s]' % dld_custom
				#print 'dld_custom1 [%s]' % dld_custom1
				#print 'dld_custom2 [%s]' % dld_custom2
				#print 'dld_custom3 [%s]' % dld_custom3
				#print 'dld_custom4 [%s]' % dld_custom4
				#print 'dld_custom5 [%s]' % dld_custom5

				#dld_kbmeta = dld_kbmeta.replace('custom_value="','').replace('"','')

				#print 'kbmeta: %s' % dld_kbmeta

				info = get_params(dld_kbmeta)
				for curi in info: info[curi] = urllib.unquote_plus(info[curi])

				def key_to_int(arr, keyname):
					try: arr[keyname] = int(arr[keyname])
					except:
						try: del info[keyname]
						except: pass
				key_to_int(info, 'count')
				key_to_int(info, 'year')
				key_to_int(info, 'episode')
				key_to_int(info, 'season')
				key_to_int(info, 'top250')
				key_to_int(info, 'tracknumber')
				key_to_int(info, 'playcount')
				key_to_int(info, 'overlay')
				try:
					info['rating'] = float(info['rating'])
				except:
					try: del info['rating']
					except: pass

				info['size'] = dld_size_bytes
				info['title'] = '%s (%s%%)'%(info['title'],dld_percent_complete)

				if dld_is_active == 1: cm_action = 'СТОП', 'xbmc.runPlugin(%s?mode=rtcshowdl&action=dlstop&hash=%s)'  % (sys.argv[0], dld_hash)
				else:                  cm_action = 'СТАРТ','xbmc.runPlugin(%s?mode=rtcshowdl&action=dlstart&hash=%s)' % (sys.argv[0], dld_hash)

				fdc = 'xbmc.runPlugin(%s?mode=rtcshowdl&action=setprio&hash=%s&prio=%s)'
				cm = [cm_action, ('УДАЛИТЬ', 'xbmc.runPlugin(%s?mode=rtcshowdl&action=erase&hash=%s)'%(sys.argv[0],dld_hash)),\
					('Приоритет: высокий',     fdc % (sys.argv[0], dld_hash, 3)),\
					('Приоритет: нормальный',  fdc % (sys.argv[0], dld_hash, 2)),\
					('Приоритет: низкий',      fdc % (sys.argv[0], dld_hash, 1)),\
					('Приоритет: не загружать',fdc % (sys.argv[0], dld_hash, 0)) ]

				li = xbmcgui.ListItem(label = info['title'], label2 = dld_name, iconImage=info['iconImage'], thumbnailImage=info['thumbnailImage'])
				li.addContextMenuItems(items = cm, replaceItems = True)
				li.setInfo(type = 'video', infoLabels = info)

				if dld_size_files > 1:
					uri = '%s?mode=rtcshowdl&action=showfiles&hash=%s&numfiles=%s'%(sys.argv[0], dld_hash, dld_size_files)
					if not xbmcplugin.addDirectoryItem(h, uri, li, isFolder = True, totalItems = dlds_len): break
				else:
					li.setProperty('IsPlayable', 'true')
					uri = '%s?mode=rtcshowdl&action=playfile&film_id=%s'%(sys.argv[0], info['film_id'])
					if not xbmcplugin.addDirectoryItem(h, uri, li,totalItems=dlds_len): break

		xbmcplugin.addSortMethod(h, sortMethod = xbmcplugin.SORT_METHOD_TITLE )
		xbmcplugin.addSortMethod(h, sortMethod = xbmcplugin.SORT_METHOD_SIZE )
		xbmcplugin.endOfDirectory(h, cacheToDisc = False)

	elif action == 'setprio':
		rtc.d.set_priority('%s' % params['hash'], int(params['prio']))
		xbmc.executebuiltin('Container.Refresh')
	elif action == 'erase':
		#rtc.d.set_priority('%s' % params['hash'], int(params['prio']))

		rtc.d.erase(params['hash'])
		showMessage('Удален торрент', 'Сами файлы остались на месте', 5000)
		xbmc.executebuiltin('Container.Refresh')

	elif action == 'showfiles':




		#print 'Воспроизводим %s' % dhash
		pfile = os.path.join(rtc.d.get_directory(params['hash']),rtc.d.get_name(params['hash']))
		#print 'Файл %s' % pfile
		#i = xbmcgui.ListItem(path = pfile)
		#xbmcplugin.setResolvedUrl(h, True, i)
		#return True



		files = []
		files = rtc.f.multicall(params['hash'],1,"f.get_path=","f.get_completed_chunks=","f.get_size_chunks=","f.get_priority=","f.get_size_bytes=")
		i=0
		for f in files:
			f_name = f[0]
			f_completed_chunks = int(f[1])
			f_size_chunks = int(f[2])
			f_size_bytes = int(f[4])
			f_percent_complete = f_completed_chunks*100/f_size_chunks
			f_priority = f[3]
			if f_percent_complete==100:
				f_complete = 1
			else:
				f_complete = 0
			#tbn=getIcon(0,1,f_complete,f_priority)
			if f_percent_complete<100:
				li_name = f_name+' ('+str(f_percent_complete)+'%)'
			else:
				li_name = f_name
			li = xbmcgui.ListItem( \
				label=li_name, \
				iconImage=icon, thumbnailImage=icon)
			#cm = [(g.__lang__(30120),"xbmc.runPlugin(%s?mode=action&method=f.set_priority&arg1=%s&arg2=%s&arg3=2)" % ( sys.argv[0], hash,i)), \
			#	(g.__lang__(30121),"xbmc.runPlugin(%s?mode=action&method=f.set_priority&arg1=%s&arg2=%s&arg3=1)" % ( sys.argv[0], hash,i)), \
			#	(g.__lang__(30124),"xbmc.runPlugin(%s?mode=action&method=f.set_priority&arg1=%s&arg2=%s&arg3=0)" % ( sys.argv[0], hash,i))]
			#li.addContextMenuItems(items=cm,replaceItems=True)
			li.setInfo('video',{'title':li_name,'size':f_size_bytes})

			#uri = '%s?mode=rtcshowdl&action=playfile&hash=%s&file_id=%s'%(sys.argv[0], params['hash'], i)

			uri = os.path.join(pfile, rtc.f.get_frozen_path(params['hash'], i))
			if not xbmcplugin.addDirectoryItem(h,uri,li,totalItems=len(files)): break
			i=i+1
		xbmcplugin.addSortMethod(h, sortMethod=xbmcplugin.SORT_METHOD_TITLE )
		xbmcplugin.addSortMethod(h, sortMethod=xbmcplugin.SORT_METHOD_SIZE )
		xbmcplugin.endOfDirectory(h, cacheToDisc=False)



	elif action == 'playfile':
		print 'playfile....'
		openfilm({'film_id': params['film_id']})





def filmssearch(params):
	KB = xbmc.Keyboard()
	KB.setHeading('Что ищем?')
	KB.doModal()
	if (KB.isConfirmed()):
		params['query'] = urllib.quote_plus(KB.getText())
		params['mode'] = 'filmsbrowse'
		filmsbrowse(params)
	else: return False



def showgenres(params):
	http = KBREQUEST('http://%s/genres/'%API_SERV)
	djson = demjson.decode(http)
	for cur in djson:
		genre_id   = cur['id']
		genre_name = cur['name'].encode('utf-8')
		li = xbmcgui.ListItem('Жанр "%s"'%genre_name, iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=opengenre&genre_id=%s&genre_name=%s'%(sys.argv[0],genre_id,urllib.quote_plus(genre_name)), li, True)
	xbmcplugin.endOfDirectory(h)


def showcountries(params):
	http = KBREQUEST('http://%s/countries/'%API_SERV)
	djson = demjson.decode(http)
	for cur in djson:
		country_id   = cur['id']
		country_name = cur['name'].encode('utf-8')
		country_iso  = cur['iso']
		li = xbmcgui.ListItem('Страна "%s"'%country_name, iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=opencountry&country_id=%s&country_name=%s&country_iso=%s'%(sys.argv[0],country_id,urllib.quote_plus(country_name),country_iso), li, True)
	xbmcplugin.endOfDirectory(h)


def showlanguages(params):
	http = KBREQUEST('http://%s/languages'%API_SERV)
	djson = demjson.decode(http)
	for cur in djson:
		lang_id   = cur['id']
		lang_name = cur['name'].encode('utf-8')
		li = xbmcgui.ListItem('Язык "%s"'%lang_name, iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=openlanguage&lang_id=%s&lang_name=%s'%(sys.argv[0],lang_id,urllib.quote_plus(lang_name)), li, True)
	xbmcplugin.endOfDirectory(h)


def showtrackers(params):
	http = KBREQUEST('http://%s/trackers'%API_SERV)
	djson = demjson.decode(http)
	for cur in djson:
		tracker_id   = cur['id']
		tracker_name = cur['url'].encode('utf-8')
		li = xbmcgui.ListItem('Трекер %s'%tracker_name, iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=openlantracker&tracker_id=%s&tracker_name=%s'%(sys.argv[0],tracker_id,urllib.quote_plus(tracker_name)), li, True)
	xbmcplugin.endOfDirectory(h)


# -------------------------------------------------------------------------------------- #



def getmetadata(data, film_id):
	info = {}
	#info = {'count': int(data['id'])}

	try:    info['title'] = data['name'].encode('utf-8')
	except: info['title'] = 'Название не указано'

	#original_name = data['original_name']
	try:
		if (data['original_name'] != None):
			if len(data['original_name']) > 0:
				info['plotoutline'] = 'Оригинальное название: "%s"' % data['original_name'].encode('utf-8')
	except: pass
	try:    info['year'] = int(data['year'])
	except: pass
	try:
		film_duration = int(data['duration'])
		if (film_duration > 0):
			if film_duration > 59: tstr = '%s:%s:00' % (film_duration/60, film_duration%60)
			else: tstr = '%s:00' % film_duration
			info['duration'] = tstr
	except: pass

	try:    info['plot'] = data['description'].encode('utf-8')
	except: info['plot'] = ''

	try:
		if data['budget'] == None: plo_budget = ''
		else: plo_budget = 'Бюджет: %s $\n' % data['budget']
	except: plo_budget = ''

	try:
		if data['revenue_usa'] == None: plo_rev_usa = ''
		else: plo_rev_usa = 'Доход в США: %s $\n' % data['revenue_usa']
	except: plo_rev_usa = ''

	try:
		if data['revenue_world'] == None: plo_rev_world = ''
		else: plo_rev_world = 'Доход в мире: %s $\n' % data['revenue_world']
	except: plo_rev_world = ''

	try:
		if data['revenue_russia'] == None: plo_rev_russia = ''
		else: plo_rev_russia = 'Доход в России: %s $\n' % data['revenue_russia']
	except: plo_rev_russia = ''

	try:
		film_countries = data['countries']
	except: film_countries = None
	if film_countries != None:
		scountry = ''
		for country in film_countries:
			country_id   = country['id']
			country_name = country['name'].encode('utf-8')
			scountry += ', %s'%country_name
		if len(scountry) > 0:
			scountry = 'Страна:%s' % (scountry[1:])
			info['plot'] = scountry + '\n' + info['plot']

	a4 = ''
	a5 = ''
	a6 = ''

	try:
		film_participants = data['participants']
	except: film_participants = None

	if film_participants != None:


		if film_participants['actor'] != None:
			a1 = []
			for actor in film_participants['actor']: a1.append(actor['name'].encode('utf-8'))
			info['cast'] = a1

		if film_participants['director'] != None:
			if len(film_participants['director']) > 0:
				a2 = ''
				for director in film_participants['director']: a2 += ', %s' % director['name'].encode('utf-8')
				info['director'] = a2[2:]

		if film_participants['writer'] != None:
			if len(film_participants['writer']) > 0:
				a3 = ''
				for writer in film_participants['writer']: a3 += ', %s' % writer['name'].encode('utf-8')
				info['writer'] = a3[2:]

		if film_participants['producer'] != None:
			if len(film_participants['producer']) > 0:
				for producer in film_participants['producer']: a4 += ', %s'%producer['name'].encode('utf-8')
				a4 = 'Продюсер: %s\n' % a4[2:]

		if film_participants['operator'] != None:
			if len(film_participants['operator']) > 0:
				for operator in film_participants['operator']: a5 += ', %s'%operator['name'].encode('utf-8')
				a5 = 'Оператор: %s\n' % a5[2:]

		if film_participants['composer'] != None:
			if len(film_participants['composer']) > 0:
				for composer in film_participants['composer']: a6 += ', %s'%composer['name'].encode('utf-8')
				a6 = 'Композитор: %s\n' % a6[2:]

	info['credits'] = a6

	try:
		genres = data['genres']
	except: genres = None

	if genres != None:
		genre = ''
		for gArray in genres:
			genre_name = gArray['name'].encode('utf-8')
			genre += ', %s'%(genre_name)
		if len(genre) > 0:
			info['genre'] = genre[2:]
			info['tagline'] = info['genre'].replace(',','')

	fbtqs = ''
	try:
		fbtq = data['best_torrent_quality']
	except: fbtq = None
	if fbtq != None:
		fbtq = fbtq.encode('utf-8')
		fbtq = fbtq.replace('low','Низкое')
		fbtq = fbtq.replace('medium','Среднее')
		fbtq = fbtq.replace('high','Высокое')
		fbtq = fbtq.replace('hd','HD 720 или выше')
		fbtq = fbtq.replace('unknown','Неизвестно')
		fbtqs = 'Качество: %s, ' % fbtq


	info['plot'] = fbtqs + info['plot'] + plo_budget + plo_rev_usa + plo_rev_world + plo_rev_russia + a4 + a5 + a6

	try:
		film_ratings = data['ratings'] # array
	except: film_ratings = None
	if film_ratings != None:

		arates = []
		avotes = []

		rstring = ''

		imdb_com     = film_ratings['imdb.com']
		if imdb_com != None:
			arates.append(imdb_com['rate'])
			avotes.append(imdb_com['votes'])
			rstring += 'Рейтинг imdb.com: %s, голосов: %s\n'%(imdb_com['rate'], imdb_com['votes'])

		kinopoisk_ru = film_ratings['kinopoisk.ru']
		if imdb_com != None:
			arates.append(kinopoisk_ru['rate'])
			avotes.append(kinopoisk_ru['votes'])
			rstring += 'Рейтинг kinopoisk.ru: %s, голосов: %s\n'%(kinopoisk_ru['rate'], kinopoisk_ru['votes'])

		tv_com       = film_ratings['tv.com']
		if imdb_com != None:
			arates.append(tv_com['rate'])
			avotes.append(tv_com['votes'])
			rstring += 'Рейтинг tv.com: %s, голосов: %s\n'%(tv_com['rate'], tv_com['votes'])

		rstring = rstring.replace('None','Нет')
		info['votes'] = str(max(avotes))
		try: info['rating'] = float(max(arates))
		except: pass
		if rstring != '': info['plot'] = info['plot'] + '\n' + rstring

	info['iconImage'] = 'http://media.kinobaza.tv/films/%s/poster/60.jpg'%film_id
	info['thumbnailImage'] = 'http://media.kinobaza.tv/films/%s/poster/207.jpg'%film_id

	return info




#===============================================================#



def filmsbrowse(params):
	xbmc.output('=== def filmsbrowse(%s): ==='%(params))

	try:
		href = urllib.unquote_plus(params['href'])
		params['href'] = href
	except: href = ''
	try: params['query'] = urllib.unquote_plus(params['query'])
	except: pass

	GL = params.copy()
	del GL['mode']
	del GL['href']

	#url =
	http = KBREQUEST('%s?%s'%(href,urllib.urlencode(GL)))

	djson = demjson.decode(http)

	#print djson

	for cur in djson:

		info = getmetadata(cur, cur['id'])

		base_dl_path = rtc.get_directory()
		#print 'rTorrent base dir (rtpath) = %s' % base_dl_path


		dpa = []
		if (rtc_select == 'true'):
			for ddir in os.listdir(base_dl_path): dpa.append(os.path.join(base_dl_path, ddir, str(cur['id'])))
		else: dpa.append(os.path.join(base_dl_path, str(cur['id'])))

		#print 'DPA %s' % dpa

		for chkdir in dpa:
			#print 'check dir %s' % chkdir
			if os.path.exists(chkdir):
				info['title'] = '[DL] %s'%info['title']



		li = xbmcgui.ListItem(label = info['title'], iconImage = info['iconImage'], thumbnailImage = info['thumbnailImage'])
		li.setInfo(type = 'video', infoLabels = info)

		if cur['type'] == 'movie':
			li.setProperty('IsPlayable', 'true')
			uri = '%s?mode=openfilm&film_id=%s'%(sys.argv[0], cur['id'])
			if not xbmcplugin.addDirectoryItem(h, uri, li, isFolder=False): break
		elif cur['type'] == 'series':
			uri = '%s?mode=openseasons&series_id=%s'%(sys.argv[0], cur['id'])
			if not xbmcplugin.addDirectoryItem(h, uri, li, isFolder=True): break
		else:
			showMessage('Ой, "%s"' % film_type, 'Не могу добавить этот тип фильма')


	if len(djson) == int(params['limit']):
		li = xbmcgui.ListItem('Далее >', iconImage=icon, thumbnailImage=icon)
		params['offset'] = str(int(params['offset'])+int(params['limit']))
		uri  = '%s?%s'%(sys.argv[0],urllib.urlencode(params))
		xbmcplugin.addDirectoryItem(h, uri, li, True)

	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_UNSORTED)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_ALBUM)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DURATION)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_GENRE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_RATING)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)

	xbmcplugin.endOfDirectory(h)

# --------------------------------------------------------------
def openseasons(params):
	xbmc.output('=== def openseasons(%s): ==='%(params))

	mtarget = 'http://%s/films/%s?fields_mask=63' % (API_SERV, params['series_id'])
	http0 = KBREQUEST(mtarget)
	mdjson = demjson.decode(http0)
	minfo = getmetadata(mdjson, params['series_id'])


	target = 'http://%s/films/%s/seasons' % (API_SERV, params['series_id'])
	http1 = KBREQUEST(target)
	djson = demjson.decode(http1)

	series_id     = djson['series_id'] # int
	seasons       = djson['seasons'] # array
	if len(seasons) == 0:
		showMessage('Ой', 'Нет сезонов :)')
		return False

	for season in seasons:
		info = minfo.copy()

		season_num     = season['num']            # int 1
		episodes_count = season['episodes_count'] # int 29
		start_date     = season['start_date'] #.encode('utf-8')     # str 2003-02-01
		end_date       = season['end_date'] #.encode('utf-8')       # str 2004-03-16

		if start_date == None: start_date = ''
		else: start_date = start_date.encode('utf-8')
		if end_date == None: end_date = ''
		else: end_date = end_date.encode('utf-8')
		#info['tvshowtitle'] = info['title']

		info['title'] = info['title'] + ' / Сезон %d (%s_%s)'%(season_num,start_date,end_date)
		info['premiered'] = start_date
		info['season'] = int(season_num)

	#	info = {'title': ''%season_num, 'premiered': start_date, 'plot':'Сезон закрыт %s'%end_date}

		series_img = 'http://media.kinobaza.tv/films/%d/poster/207.jpg' % series_id

		li = xbmcgui.ListItem(info['title'], iconImage=series_img, thumbnailImage=series_img)
		li.setInfo(type='video', infoLabels = info)

		uri = '%s?mode=openepisodes&series_id=%s&season_num=%s'%(sys.argv[0],series_id,season_num)

		if not xbmcplugin.addDirectoryItem(h, uri, li, isFolder=True, totalItems=episodes_count): break


	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TITLE)

	xbmcplugin.endOfDirectory(h)



#-------------------------------------------------------------------------------------------------------
#GET /films/<series_id>/seasons/<season_num>/episodes
#http://api.kinobaza.tv/films/357767/seasons/1/episodes
#{"series_id":357767,"season_num":1,"episodes":[{"num":1,"name":"Role Play","release_date":"2003-02-01"}


def openepisodes(params):
	xbmc.output('=== def openepisodes(%s): ==='%(params))

	mtarget = 'http://%s/films/%s?fields_mask=63' % (API_SERV, params['series_id'])
	http0 = KBREQUEST(mtarget)
	mdjson = demjson.decode(http0)
	minfo = getmetadata(mdjson, params['series_id'])

	target = 'http://%s/films/%s/seasons/%s/episodes' % (API_SERV, params['series_id'], params['season_num'])


	#print target

	http1 = KBREQUEST(target)
	djson = demjson.decode(http1)

	#print djson

	series_id      = djson['series_id']   # int 1
	season_num     = djson['season_num'] # int 1
	episodes       = djson['episodes']   # array
	if len(episodes) == 0:
		showMessage('Ой', 'Нет эпизодов :)')
		return False

	for episode in episodes:

		info = minfo.copy()

		episode_num  = episode['num']          # int 1
		episode_name = episode['name'].encode('utf-8')         # str Role Play
		release_date = episode['release_date'] #3.encode('utf-8') # str 2003-02-01

		print 'openepisodes -> series_id=%s season_num=%s episode_num=%s episode_name=%s release_date=%s' % (series_id, season_num, episode_num, episode_name, release_date)


		#info['tvshowtitle'] = info['title']

		info['title'] = '%d. %s'%(episode_num, episode_name)

		if release_date != None:
			info['premiered'] = release_date
			info['premiered'] = release_date

		info['episode'] = int(episode_num)
		info['season']  = int(season_num)


		series_img = 'http://media.kinobaza.tv/films/%d/poster/207.jpg' % series_id

		li = xbmcgui.ListItem(info['title'], iconImage=series_img, thumbnailImage=series_img)
		li.setInfo(type='video', infoLabels = info)

		uri = '%s?mode=openfilm&series_id=%d&season_num=%d&episode_num=%d'%(sys.argv[0],series_id,season_num,episode_num)
		if not xbmcplugin.addDirectoryItem(h, uri, li, isFolder=False): break


	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TITLE)

	xbmcplugin.endOfDirectory(h)


#openfilm
#GET 'http://api.kinobaza.tv/films/%s/seasons/%s/episodes/%s/torrents'%(series_id,season_num,episode_num)

#---------------------------------------------------------------------------------------------------------------------
def openfilm(params):
	xbmc.output('=== def openfilm(%s): ==='%(params))

	target = None
	series_dl_append = ''

	try:
		# Если сериал
		series_id   = params['series_id']
		season_num  = params['season_num']
		episode_num = params['episode_num']
		print '====== СЕРИАЛ ======'
		print 'openfilm -> series_id   = [%s]' % series_id
		print 'openfilm -> season_num  = [%s]' % season_num
		print 'openfilm -> episode_num = [%s]' % episode_num
		target = 'http://%s/films/%s/seasons/%s/episodes/%s/torrents' % (API_SERV, series_id, season_num, episode_num)
		print 'openfilm -> target      = [%s]' % target
		dlpath = os.path.join(series_id, season_num, episode_num)
		print 'openfilm -> dlpath      = [%s]' % dlpath
		meta_id = series_id
		series_dl_append = ' (s%se%s)'%(season_num,episode_num)
	except:
		print '====== NOT СЕРИАЛ (EXCEPT) ======'
		target = None

	if target == None:
		try:
			print '====== ФИЛЬМ ======'
			film_id = params['film_id']
			print 'openfilm -> film_id     = [%s]' % film_id
			target = 'http://%s/films/%s/torrents?all_trackers=true'%(API_SERV, film_id)
			print 'openfilm -> target      = [%s]' % target
			dlpath = os.path.join(film_id)
			print 'openfilm -> dlpath      = [%s]' % dlpath
			meta_id = film_id
		except:
			print '====== NOT ФИЛЬМ (EXCEPT) ======'
			return False

	http2 = KBREQUEST(target)
	djson = demjson.decode(http2)

	#print djson

	film_id  = djson['film_id']
	filters  = djson['filters']
	torrents = djson['torrents']

	exa = []
	exb = []

	fxa = []
	fxb = []
	fxc = []
	fxd = []

	for torrent in torrents:
		t_id              = torrent['id']
		print 't_id          = [%s]' % t_id
		t_is_approved     = torrent['is_approved']
		print 't_is_approved = [%s]' % t_is_approved
		t_name            = torrent['name'].encode('utf-8')
		print 't_name        = [%s]' % t_name
		#t_url             = torrent['url']
		#print 't_url         = [%s]' % t_url
		#t_description_url = torrent['description_url']
		#print 't_description_url = [%s]' % t_description_url
		t_tracker_url     = torrent['tracker_url'].encode('utf-8').replace('http:','').replace('/','')
		print 't_tracker_url = [%s]' % t_tracker_url
		t_size            = torrent['size'].encode('utf-8')
		print 't_size     = [%s]' % t_size
		t_filetype        = torrent['filetype']
		print 't_filetype = [%s]' % t_filetype
		t_quality         = torrent['quality'].encode('utf-8')
		print 't_quality  = [%s]' % t_quality
		t_seeders         = torrent['seeders']
		print 't_seeders  = [%s]' % t_seeders
		t_leechers        = torrent['leechers']
		print 't_leechers = [%s]' % t_leechers
		t_hash            = torrent['hash'].encode('utf-8')
		print 't_hash     = [%s]' % t_hash
		#t_files           = torrent['files']
		#print 't_files    = [%s]' % t_files


		try:
			f_percent_complete = (int(rtc.f.get_completed_chunks(t_hash, 0))*100)/int(rtc.f.get_size_chunks(t_hash, 0))
		except:
			f_percent_complete = 0

		if f_percent_complete == 100:
			print 'Есть загруженный файл %s' % t_hash
			exa.append('Трекер:%s, Качество:%s, Размер:%s' % (t_tracker_url, t_quality, t_size))
			exb.append(t_hash)
		elif f_percent_complete == 0:
			fxas = 'S:%s L:%s Q:%s [%s]' % (t_seeders, t_leechers, t_quality, t_tracker_url)
			fxa.append(fxas)
			fxb.append(t_hash)
			fxc.append(t_id)
			fxd.append(0)
		else:
			fxas = '%d%% S:%s L:%s Q:%s [%s]' % (f_percent_complete, t_seeders, t_leechers, t_quality, t_tracker_url)
			fxa.append(fxas)
			fxb.append(t_hash)
			fxc.append(t_id)
			fxd.append(f_percent_complete)

	dl_select = False

	if len(exa) > 0:
		exa.append('Загрузить другую раздачу...')
		s = xbmcgui.Dialog().select('Что воспроизвести?', exa)
		if s < 0:
			return True
		if s == len(exa)-1:
			print 'Выбрано загрузить другую раздачу...'
			dl_select = True
		else:
			phash = exb[s]
			print 'Воспроизводим %s' % phash
			pfile = os.path.join(rtc.d.get_directory(phash),rtc.d.get_name(phash))
			#print 'Файл %s' % pfile
			i = xbmcgui.ListItem(path = pfile)
			xbmcplugin.setResolvedUrl(h, True, i)
			return True
	else:
		dl_select = True

	if dl_select:
		if len(fxa) == 0:
			#showMessage('Извините. Не выйдет!', 'Кинобазе пока не известно ни одного торрента.', 5000)
			#№вввввввввввввввввввв
			ret = xbmcgui.Dialog().yesno('Кинобаза',
				'Пока не известно ни одной раздачи этого',
				'файла. Но рано или поздно она появится.',
				'Пометить файл как ожидаемый вами?')
			if ret:
				print 'Ожидать...'
				showMessage('Ой', 'Эта штука не работает пока')
				return True
			else:
				print 'Не ждать...'
				#showMessage('Ой', 'Эта штука не работает пока')
				return True

			#TODO Добавить ожидание раздачи
		print 'Выбираем раздачу'
		s = xbmcgui.Dialog().select('Выбрать раздачу?', fxa)
		if s < 0:
			print 'Не выбрано, выход...'
			return True
		dhash = fxb[s]
		torid = fxc[s]
		dpercent = fxd[s]
		print 'Выбрана раздача %s' % dhash


		if dpercent > 0:
			is_active = int(rtc.d.is_active(dhash))

			if is_active == 1:
				ans0 = ['Остановить загрузку','Поставить на паузу','Удалить', 'Попытаться воспроизвести']
				s = xbmcgui.Dialog().select('Раздача загружается. Готово: %d%%'%dpercent, ans0)
				if s < 0:
					print 'Не выбрано, выход...'
					return True
				if s == 0:
					rtc.d.close(dhash)
					return True
				elif s == 1:
					rtc.d.pause(dhash)
					return True
				elif s == 2:
					rtc.d.erase(dhash)
					return True
				elif s == 3:
					print 'Воспроизводим %s' % dhash
					pfile = os.path.join(rtc.d.get_directory(dhash),rtc.d.get_name(dhash))
					#print 'Файл %s' % pfile
					i = xbmcgui.ListItem(path = pfile)
					xbmcplugin.setResolvedUrl(h, True, i)
					return True
			else:
				ans0 = ['Продолжить','Удалить','Попытаться воспроизвести']
				s = xbmcgui.Dialog().select('Раздача на паузе. Готово: %d%%'%dpercent, ans0)
				if s < 0:
					print 'Не выбрано, выход...'
					return True
				if s == 0:
					rtc.d.start(dhash)
					return True
				elif s == 1:
					rtc.d.erase(dhash)
					return True
				elif s == 2:
					print 'Воспроизводим %s' % dhash
					pfile = os.path.join(rtc.d.get_directory(dhash),rtc.d.get_name(dhash))
					#print 'Файл %s' % pfile
					i = xbmcgui.ListItem(path = pfile)
					xbmcplugin.setResolvedUrl(h, True, i)
					return True



		#############

#		try:
#			f_percent_complete = (int(rtc.f.get_completed_chunks(dhash, 0))*100)/int(rtc.f.get_size_chunks(dhash, 0))
#			percs = '%d% '%f_percent_complete
#		except:
#			percs = ''


		rtpath = rtc.get_directory()
		print 'rTorrent base dir (rtpath) = %s' % rtpath
		dpath = rtpath

		if rtc_select == 'true':
			print 'Указан выбор каталога загрузки...'
			dpa = []
			#dpb = []
			for ddir in os.listdir(rtpath):
				dpa.append(ddir)
				#dpb.append(os.path.join(ddir, rtpath))

			s = xbmcgui.Dialog().select('Куда качать?', dpa)
			if s < 0:
				print 'Не выбрано, выход...'
				return True
			else:
				dpath = os.path.join(rtpath, dpa[s])

		dpath = os.path.join(dpath, dlpath)

		print 'Download path [%s]' % dpath

		if not os.path.exists(dpath):
			os.makedirs(dpath)
			print 'Path %s created...' % dpath
		else:
			print 'Path %s exists...' % dpath

		url_gt = 'http://%s/torrents/%s/direct-link'%(API_SERV,dhash)
		print 'url_gt GET: %s' % url_gt
		http3 = KBREQUEST(url_gt)
		djson2 = demjson.decode(http3)



		try:
			code = djson['code']
			message = djson['message']
			showMessage('Ошибка %d'%code, message.encode('utf-8'), 5000)
			print 'ERROR %s MESSAGE %s ' % (code, message.encode('utf-8'))
			return True
		except: pass

		#print djson2
		tf_url  = djson2['url']

		print 'Direct Link = %s' % tf_url

		t_id              = torrent['id']
		print 't_id          = [%s]' % t_id
		t_is_approved     = torrent['is_approved']
		print 't_is_approved = [%s]' % t_is_approved
		t_name            = torrent['name'].encode('utf-8')
		print 't_name        = [%s]' % t_name
		#t_url             = torrent['url']
		#print 't_url         = [%s]' % t_url
		#t_description_url = torrent['description_url']
		#print 't_description_url = [%s]' % t_description_url
		t_tracker_url     = torrent['tracker_url'].encode('utf-8').replace('http:','').replace('/','')
		print 't_tracker_url = [%s]' % t_tracker_url
		t_size            = torrent['size'].encode('utf-8')
		print 't_size     = [%s]' % t_size
		t_filetype        = torrent['filetype']
		print 't_filetype = [%s]' % t_filetype
		t_quality         = torrent['quality'].encode('utf-8')
		print 't_quality  = [%s]' % t_quality
		t_seeders         = torrent['seeders']
		print 't_seeders  = [%s]' % t_seeders
		t_leechers        = torrent['leechers']
		print 't_leechers = [%s]' % t_leechers
		t_hash            = torrent['hash'].encode('utf-8')
		print 't_hash     = [%s]' % t_hash
		#t_files           = torrent['files']
		#print 't_files    = [%s]' % t_files


		mtarget = 'http://%s/films/%s?fields_mask=63' % (API_SERV, meta_id)
		http4 = KBREQUEST(mtarget)
		mdjson = demjson.decode(http4)
		minfo = getmetadata(mdjson, film_id)

		minfo['title'] = minfo['title'] + series_dl_append

		try: del minfo['cast']
		except: pass
		try: del minfo['castandrole']
		except: pass

		custom2 = '&film_id=%s'%film_id
		for cinfo in minfo:
			custom2 += '&%s=%s'%(cinfo, urllib.quote_plus(str(minfo[cinfo])))

		custom2 = custom2[1:]

		#custom2 = 'film_id=%s&torid=%s' % (film_id, torid)
		#custom2 = test_data + '\n' + test_data + '\n' + test_data + '\n' + test_data + '\n'
		# TORRENT_URL | DIR | LABEL | COMMENT
		#rtc.load_start(tf_url, 'd.set_directory="%s"'%dpath, 'd.set_custom1="kinobaza"', 'd.set_custom2="%s"'%custom2)
		#rtc.load_start(tf_url, 'd.set_directory="%s"'%dpath, 'd.set_custom1="kinobaza"', 'd.set_custom2="%s"'%custom2)

		rtc.load_start(tf_url, 'd.set_directory="%s"'%dpath, 'd.set_custom1="kinobaza"', 'd.set_custom=kbmeta,%s'%custom2)

		return True








params = get_params(sys.argv[2])

mode   = None
func   = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	showroot(params)

if (mode != None):
	try:
		func = globals()[mode]
	except:
		pass
	if func: func(params)
