#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2011 Muzunga.TV, http://muzunga.tv/
# Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com

import sys, xbmc, xbmcgui, xbmcplugin, xbmcaddon
import os, urllib, urllib2, datetime
import xml.dom.minidom
import time

addon_id       = 'plugin.video.xbmc.rus'
addon_name     = 'unknown addon'
addon_version  = '0.0.0'
addon_provider = 'unknown'

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))
adxf = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'addon.xml'))
if os.path.isfile(adxf):
	af = open(adxf, 'r')
	adom = xml.dom.minidom.parseString(af.read())
	af.close()
	areg = adom.getElementsByTagName('addon')
	addon_id       = areg[0].getAttribute('id')
	addon_name     = areg[0].getAttribute('name')
	addon_version  = areg[0].getAttribute('version')
	addon_provider = areg[0].getAttribute('provider-name')


__settings__ = xbmcaddon.Addon(id = addon_id)
__language__ = __settings__.getLocalizedString
h = int(sys.argv[1])

private_key = __settings__.getSetting('private_key')
private_login = __settings__.getSetting('username')
private_password = __settings__.getSetting('password')




def showMessage(heading, message, times = 3000, pics = icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics))
	except Exception, e:
		print '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e)
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			print '[%s]: showMessage: exec failed [%s]' % (addon_id, e)




def GET(targeturl):
	#print '[%s]: GET [%s]' % (addon_id, targeturl)
	try:
		req = urllib2.Request(targeturl)
		req.add_header(     'User-Agent','XBMC/ADDON (Python addon; XBMC)')
		f = urllib2.urlopen(req)
		CE = f.headers.get('content-encoding')
		if CE:
			if 'gzip' in CE:
				import io, gzip
				bindata = io.BytesIO(f.read())
				gzipf = gzip.GzipFile(fileobj = bindata, mode='rb')
				a = gzipf.read()
			else: a = f.read()
		else: a = f.read()
		f.close()
		return a
	except Exception, e:
		print '[%s]: GET EXCEPT [%s]' % (addon_id, e)
		showMessage('HTTP ERROR', href, 5000)


def showroot(params): # IMPLEMENTED
	key_status_url = 'http://muzunga.tv/stb/xml/key_status.php?device_type=xbmc'
	
	if len(private_key):
		key_status_url += '&private_key=%s' % private_key
		
	if len(private_login):
		key_status_url += '&login=%s' % private_login

	if len(private_password):
		key_status_url += '&password=%s' % private_password
	
	http = GET(key_status_url)
	if http:
		document = xml.dom.minidom.parseString(http)
		user_found = int(document.getElementsByTagName('user_found')[0].firstChild.data)
		
		if user_found==0:
			showMessage('Ошибка авторизации на сайте Muzunga.TV', 'Проверьте правильность логина и пароля', 10000)
			__settings__.openSettings() 
			return False

		try:
			new_key = document.getElementsByTagName('new_key')[0].firstChild.data
			if len(new_key):
				__settings__.setSetting('private_key', new_key)
				showMessage(u'Ключ: %s' % new_key, 'Пожалуйста привяжите его к вашему логину', 60000)
		except: 
			pass

	http = GET('http://muzunga.tv/stb/xml/category.php')
	if http:
		i = xbmcgui.ListItem('[ Поиск ]', iconImage = icon, thumbnailImage = icon)
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showsearch'})), i, True)
		
		i = xbmcgui.ListItem('[ Все категории ]', iconImage = icon, thumbnailImage = icon)
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showlist', 'id':0})), i, True)
		
		i = xbmcgui.ListItem('[ Сериалы ]', iconImage = icon, thumbnailImage = icon)
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showlist', 'id':0, 'video_type':2})), i, True)
		
		document = xml.dom.minidom.parseString(http)
		for item in document.getElementsByTagName('item'):
			i = xbmcgui.ListItem(item.getElementsByTagName('name')[0].firstChild.data, iconImage = icon, thumbnailImage = icon)
			xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showlist', 'id':item.getElementsByTagName('id')[0].firstChild.data})), i, True)
	xbmcplugin.endOfDirectory(h)


def showsearch(params):
	try:    params['page'] = int(params['page'])
	except: params['page'] = 0
	uparam = {'private_key':private_key, 'view_limit':25, 'detail_info':0}

	qstr = None
	try: 
		qstr = params['qstr']
	except:
		KB = xbmc.Keyboard()
		KB.setHeading('Поиск по Muzunga.TV')
		KB.doModal()
		if KB.isConfirmed():
			qstr = KB.getText()
		else: 
			return False

	uparam['search'] = qstr
	uparam['view_start'] = 25 * params['page']
	params['page'] += 1
	
	target = 'http://muzunga.tv/stb/xml/search.php?%s'
	http = GET(target % urllib.urlencode(uparam))
	
	if http:
		document = xml.dom.minidom.parseString(http)
		
		for item in document.getElementsByTagName('item'):
			mdata = {'title': item.getElementsByTagName('name')[0].firstChild.data}
			mdata['tvshowtitle'] = mdata['title']
			
			gg = ''
			for dg in item.getElementsByTagName('category'):
				gg += u', %s' % dg.getElementsByTagName('name')[0].firstChild.data #.encode('utf-8','replace')
			if len(gg) > 2: 
				gg = gg[2:]
				
			try: 
				video_type = int(item.getElementsByTagName('video_type')[0].firstChild.data)
			except: 
				video_type = 0
				
			if video_type == 1: 
				gg2 = u'Фильм, '
			elif video_type == 2: 
				gg2 = u'Cериал, '
			elif video_type == 3: 
				gg2 = u'Развлечение, '
			elif video_type == 4: 
				gg2 = u'Мультфильмы, '
			else: 
				gg2 = ''
				
			mdata['genre'] = gg2 + gg
			
			try:
				year = int(item.getElementsByTagName('year')[0].firstChild.data)
				mdata['year'] = year
			except: 
				year = None

			if year:
				mdata['title'] += u' (%s)' % (year)

			try:
				production = item.getElementsByTagName('production')[0].firstChild.data #.encode('utf-8','replace')
				mdata['studio'] = production
			except: 
				production = None
			
			try:
				duration = int(item.getElementsByTagName('duration')[0].firstChild.data)
				mdata['duration'] = '%d:%d:00' % (int(duration / 60), int(duration % 60))
			except:
				pass

			try:
				mdata['rating'] = float(item.getElementsByTagName('rating_kinopoisk')[0].firstChild.data)
			except: 
				pass
				
			try:
				added = int(item.getElementsByTagName('added')[0].firstChild.data)
				pdb = datetime.datetime.fromtimestamp(added)
				mdata['date'] = str(pdb.strftime('%d.%m.%Y'))
			except: 
				pass

			item_id = item.getElementsByTagName('id')[0].firstChild.data
			img = 'http://muzunga.tv/thumbs/%s/thumb/1.jpg' % (item_id)

			i = xbmcgui.ListItem(mdata['title'], iconImage = img, thumbnailImage = img)
			i.setInfo(type = 'video', infoLabels = mdata)
			i.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'play', 'id':item_id, 'season':0, 'episode':0})), i, True)

	i = xbmcgui.ListItem('[ ЕЩЕ! ]', iconImage = icon, thumbnailImage = icon)
	xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode(params)), i, True)

	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_UNSORTED)
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



def showlist(params):
	try:    params['page'] = int(params['page'])
	except: params['page'] = 0
	
	try:    params['video_type'] = int(params['video_type'])
	except: params['video_type'] = 0
	
	uparam = {'private_key':private_key, 'view_limit':25, 'detail_info':0}

	target = 'http://muzunga.tv/stb/xml/list.php?%s'
	uparam['category_id'] = params['id']
	uparam['video_type'] = params['video_type']
	uparam['view_start'] = 25 * params['page']
	params['page'] += 1
	
	http = GET(target % urllib.urlencode(uparam))
	
	if http:
		document = xml.dom.minidom.parseString(http)
		
		for item in document.getElementsByTagName('item'):
			mdata = {'title': item.getElementsByTagName('name')[0].firstChild.data}
			mdata['tvshowtitle'] = mdata['title']
			
			gg = ''
			for dg in item.getElementsByTagName('category'):
				gg += u', %s' % dg.getElementsByTagName('name')[0].firstChild.data #.encode('utf-8','replace')
			if len(gg) > 2: 
				gg = gg[2:]
				
			try: 
				video_type = int(item.getElementsByTagName('video_type')[0].firstChild.data)
			except: 
				video_type = 0
				
			if video_type == 1: 
				gg2 = u'Фильм, '
			elif video_type == 2: 
				gg2 = u'Cериал, '
			elif video_type == 3: 
				gg2 = u'Развлечение, '
			elif video_type == 4: 
				gg2 = u'Мультфильмы, '
			else: 
				gg2 = ''
				
			mdata['genre'] = gg2 + gg
			
			try:
				year = int(item.getElementsByTagName('year')[0].firstChild.data)
				mdata['year'] = year
			except: 
				year = None

			if year:
				mdata['title'] += u' (%s)' % (year)

			try:
				production = item.getElementsByTagName('production')[0].firstChild.data #.encode('utf-8','replace')
				mdata['studio'] = production
			except: 
				production = None
			
			try:
				duration = int(item.getElementsByTagName('duration')[0].firstChild.data)
				mdata['duration'] = '%d:%d:00' % (int(duration / 60), int(duration % 60))
			except:
				pass
				
			try:
				mdata['rating'] = float(item.getElementsByTagName('rating_kinopoisk')[0].firstChild.data)
			except: 
				pass
				
			try:
				added = int(item.getElementsByTagName('added')[0].firstChild.data)
				pdb = datetime.datetime.fromtimestamp(added)
				mdata['date'] = str(pdb.strftime('%d.%m.%Y'))
			except: 
				pass

			item_id = item.getElementsByTagName('id')[0].firstChild.data
			img = 'http://muzunga.tv/thumbs/%s/thumb/1.jpg' % (item_id)
			
			i = xbmcgui.ListItem(mdata['title'], iconImage = img, thumbnailImage = img)
			i.setInfo(type = 'video', infoLabels = mdata)
			i.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'play', 'id':item_id, 'season':0, 'episode':0})), i, True)

	i = xbmcgui.ListItem('[ ЕЩЕ! ]', iconImage = icon, thumbnailImage = icon)
	xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode(params)), i, True)

	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_UNSORTED)
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




def showseasons(params):
	uparam = {'id':params['id'], 'private_key':private_key}
	http = GET('http://muzunga.tv/stb/xml/movie.php?%s' % urllib.urlencode(uparam))

	if http:
		document = xml.dom.minidom.parseString(http)

		season_list = document.getElementsByTagName('season');
		if season_list.length==1:
			season_id = int(season_list[0].getElementsByTagName('id')[0].firstChild.data)
			params['season_id'] = season_id
			showepisodes(params)
		else:
			for season in season_list:
				season_id = int(season.getElementsByTagName('id')[0].firstChild.data)
				season_episode_count = int(season.getElementsByTagName('episode_count')[0].firstChild.data)
				
				mdata = {}
				mdata['title'] = 'Сезон %d (%d серий)' % (season_id, season_episode_count)
				mdata['season'] = season_id
				
				img = 'http://muzunga.tv/thumbs/%s/thumb/1.jpg?%s' % (params['id'], params['id'])				

				i = xbmcgui.ListItem(mdata['title'], iconImage = img, thumbnailImage = img)
				i.setInfo(type = 'video', infoLabels = mdata)
				xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showepisodes', 'id':params['id'], 'season_id':season_id})), i, True)	
	
			xbmcplugin.endOfDirectory(h)
	

def showepisodes(params):
	season_id = int(params['season_id']) 
	uparam = {'id':params['id'], 'season':season_id, 'detail_info':0, 'private_key':private_key}
	http = GET('http://muzunga.tv/stb/xml/movie.php?%s' % urllib.urlencode(uparam))

	if http:
		document = xml.dom.minidom.parseString(http)

		for season in document.getElementsByTagName('season'):
			cur_season_id = int(season.getElementsByTagName('id')[0].firstChild.data)
			
			if season_id==cur_season_id:
				for episode in season.getElementsByTagName('episode'):
					episode_id = int(episode.getElementsByTagName('id')[0].firstChild.data)
					
					try:
						name = episode.getElementsByTagName('name')[0].firstChild.data
					except:
						name = '';
						
					mdata = {}
					mdata['title'] = '%d. %s' % (episode_id, name)
					mdata['season']  = season_id
					mdata['episode'] = episode_id
					
					img = 'http://muzunga.tv/thumbs/%s/thumb/1.jpg?%s' % (params['id'], params['id'])				
					
					i = xbmcgui.ListItem(mdata['title'], iconImage = img, thumbnailImage = img)
					i.setInfo(type = 'video', infoLabels = mdata)
					i.setProperty('IsPlayable', 'true')
					xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'play', 'id':params['id'], 'season':season_id, 'episode':episode_id})), i, True)

		xbmcplugin.endOfDirectory(h)





def play(params):
	uparam = {'id':params['id'], 'private_key':private_key}

	try:
		season_id = int(params['season'])
		uparam['season'] = season_id
	except: 
		season_id = 0

	try:
		episode_id = int(params['episode'])
		uparam['episode'] = episode_id
	except: 
		episode_id = 0

	#try:
	#	audio_id = int(params['audio'])
	#except: 
	#	audio_id = -1
    #
	#try:
	#	subtitle_id = int(params['subtitle'])
	#except: 
	#	subtitle_id = -1
		
	try:
		asselect = int(params['asselect'])
	except:
		asselect = 0

	http = GET('http://muzunga.tv/stb/xml/movie.php?%s' % urllib.urlencode(uparam))
	if http:
		document = xml.dom.minidom.parseString(http)
		
		use_episode = 0
		
		season_list = document.getElementsByTagName('season');
		if season_list and season_list.length:
			use_episode = 1
			if episode_id==0:
				showseasons(params)
				return False

		mdata = {}
		
		try:
			year = int(document.getElementsByTagName('year')[0].firstChild.data)
			mdata['year'] = year
		except: 
			year = None
		
		if use_episode:
			mdata['title'] = document.getElementsByTagName('episode_name')[0].firstChild.data
			
			try: mdata['season'] = int(document.getElementsByTagName('season_id')[0].firstChild.data)
			except: pass
			
			try: mdata['episode'] = int(document.getElementsByTagName('episode_id')[0].firstChild.data)
			except: pass
			
			try: mdata['plot'] = document.getElementsByTagName('episode_description')[0].firstChild.data
			except: pass
			
			try:
				duration = int(document.getElementsByTagName('episode_duration')[0].firstChild.data)
				mdata['duration'] = '%d:%d:00' % (int(duration / 60), int(duration % 60))
			except:
				pass
		else:
			mdata['title'] = document.getElementsByTagName('name')[0].firstChild.data
			if year:
				mdata['title'] += u' (%s)' % (year)
				
			try: mdata['plot'] = document.getElementsByTagName('description')[0].firstChild.data
			except: pass
			
			try:
				duration = int(document.getElementsByTagName('duration')[0].firstChild.data)
				mdata['duration'] = '%d:%d:00' % (int(duration / 60), int(duration % 60))
			except:
				pass

		mdata['tvshowtitle'] = mdata['title']
		
		gg = ''
		for dg in document.getElementsByTagName('category'):
			gg += u', %s' % dg.getElementsByTagName('name')[0].firstChild.data #.encode('utf-8','replace')
		if len(gg) > 2: 
			gg = gg[2:]
			
		#mdata['genre'] = gg
		
		try: 
			video_type = int(document.getElementsByTagName('video_type')[0].firstChild.data)
		except: 
			video_type = 0
			
		if video_type == 1: 
			gg2 = u'Фильм, '
		elif video_type == 2: 
			gg2 = u'Cериал, '
		elif video_type == 3: 
			gg2 = u'Развлечение, '
		elif video_type == 4: 
			gg2 = u'Мультфильмы, '
		else: 
			gg2 = ''
			
		mdata['genre'] = gg2 + gg
		
		try:
			production = document.getElementsByTagName('production')[0].firstChild.data #.encode('utf-8','replace')
			mdata['studio'] = production
		except: 
			production = None
		
		try: 
			mdata['director'] = document.getElementsByTagName('director')[0].firstChild.data
		except: 
			pass

		try: 
			mdata['writer'] = document.getElementsByTagName('screenwriter')[0].firstChild.data
		except: 
			pass

		try: 
			mdata['cast'] = document.getElementsByTagName('actor')[0].firstChild.data.split(', ')
		except: 
			pass
						
		try:
			mdata['rating'] = float(document.getElementsByTagName('rating_kinopoisk')[0].firstChild.data)
		except: 
			pass
			
		try:
			added = int(document.getElementsByTagName('added')[0].firstChild.data)
			pdb = datetime.datetime.fromtimestamp(added)
			mdata['date'] = str(pdb.strftime('%d.%m.%Y'))
		except: 
			pass
			
		audio_list_id = None
		audio_list_name = None
		
		audio_list = document.getElementsByTagName('audio')
		if audio_list and audio_list.length:
			audio_list_id = []
			audio_list_name = []
			
			for cur_audio in audio_list:
				audio_list_id.append(int(cur_audio.getElementsByTagName('id')[0].firstChild.data))
				audio_list_name.append(cur_audio.getElementsByTagName('name')[0].firstChild.data)
				
		subtitle_list_filename = None
		subtitle_list_name = None
		
		subtitle_list = document.getElementsByTagName('subtitle')
		if subtitle_list and subtitle_list.length:
			subtitle_list_filename = []
			subtitle_list_name = []
			
			subtitle_list_filename.append('')
			subtitle_list_name.append('Без субтитров')
			
			for cur_subtitle in subtitle_list:
				subtitle_list_filename.append(cur_subtitle.getElementsByTagName('filename')[0].firstChild.data)
				subtitle_list_name.append(cur_subtitle.getElementsByTagName('name')[0].firstChild.data)
				
		#view_location = int(document.getElementsByTagName('view_location')[0].firstChild.data)
		#view_completed = int(document.getElementsByTagName('view_completed')[0].firstChild.data)
		
		
		item_id = document.getElementsByTagName('id')[0].firstChild.data
		img = 'http://muzunga.tv/thumbs/%s/thumb/1.jpg' % (item_id)

		try:
			queue = int(document.getElementsByTagName('queue')[0].firstChild.data)
		except:
			queue = 0
			
		if queue:
			showMessage('Ожидание бесплатного подключения к серверу, повторите попытку немного позже', 'Место в очереди на подключение: %d' % queue, 10000)
			return False
			
		try:
			streamer = document.getElementsByTagName('streamer')[0].firstChild.data
			file_hd = document.getElementsByTagName('file_hd')[0].firstChild.data
		except:
			streamer = None
			file_hd = None
			
		if streamer and file_hd:
			movie_url = '%s app=%s playpath=%s' % (streamer, streamer.split('/')[-1], file_hd)
			
			audio_id = -1
			subtitle_filename = ''
			
			if asselect:
				if audio_list_name:
					s = xbmcgui.Dialog().select('Выбор звуковой дорожки', audio_list_name)
					if s < 0: 
						return False
					audio_id = audio_list_id[s]
				if subtitle_list_name:
					s = xbmcgui.Dialog().select('Выбор субтитров', subtitle_list_name)
					if s < 0: 
						return False
					subtitle_filename = subtitle_list_filename[s]
					#subtitle_filename = '/subtitles/555/4.srt'
					#showMessage('Субтитры1', 'http://www.muzunga.tv%s' % subtitle_filename, 10000)			

			if audio_id!=-1:
				movie_url += '_%d' % audio_id
				
			i = xbmcgui.ListItem(label = 'Начать воспроизведение', path = movie_url)
  			i.setInfo(type = 'video', infoLabels = mdata)
			i.setProperty('IsPlayable', 'true')
			i.setPath(movie_url)
			
			if asselect:
				xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(movie_url, i)
				time.sleep(2)
				if len(subtitle_filename):
					xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).setSubtitles('http://www.muzunga.tv%s' % subtitle_filename)
				return False

			xbmcplugin.addDirectoryItem(h, movie_url, i, False)
			#xbmcplugin.setResolvedUrl(h, True, i)
  			
  			asname = ''
  			if audio_list_name and subtitle_list_name:
  				asname = 'Выбор звуковых дорожек и субтитров'
  			elif audio_list_name:
  				asname = 'Выбор звуковых дорожек'
  			elif subtitle_list_name:
  				asname = 'Выбор субтитров'
  			
  			if len(asname):
				i = xbmcgui.ListItem(label = asname)
	  			i.setInfo(type = 'video', infoLabels = mdata)
				i.setProperty('IsPlayable', 'true')
  				
				xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'play', 'id':params['id'], 'season':params['season'], 'episode':params['episode'], 'asselect':1})), i, True)
				
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
	if len(param) > 0:
		for cur in param:
			param[cur] = urllib.unquote_plus(param[cur])
	return param


def addon_main():
	params = get_params(sys.argv[2])
	try:
		func = params['func']
	except:
		func = None
		showroot(params)

	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			print '[%s]: Function "%s" not found' % (addon_id, func)
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
