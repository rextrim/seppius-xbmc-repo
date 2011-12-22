#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 ivi media. All rights reserved.
# Copyright (c) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com

import sys, xbmc, xbmcgui, xbmcplugin, xbmcaddon
import os, urllib, urllib2, cookielib, base64
import sha

__addon__ = xbmcaddon.Addon( id = 'plugin.video.ivi.ru' )
__language__ = __addon__.getLocalizedString

addon_icon    = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path    = __addon__.getAddonInfo('path')
addon_type    = __addon__.getAddonInfo('type')
addon_id      = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name    = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')


UA = '%s/%s %s/%s/%s' % (addon_type, addon_id, urllib.quote_plus(addon_author), addon_version, urllib.quote_plus(addon_name))

show_len = 50


xbmc.log('[%s] Starting version [%s] "%s"' % (addon_id, addon_version, addon_name), 1)

h = int(sys.argv[1])

try:
	import json
except ImportError:
	try:
		import simplejson as json
		xbmc.log( '[%s]: Error import json. Uses module simplejson' % addon_id, 2 )
	except ImportError:
		try:
			import demjson3 as json
			xbmc.log( '[%s]: Error import simplejson. Uses module demjson3' % addon_id, 3 )
		except ImportError:
			xbmc.log( '[%s]: Error import demjson3. Sorry.' % addon_id, 4 )



def showMessage(heading, message, times = 3000, pics = addon_icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )


def GET(target, post=None):
	print target
	headers = {'User-Agent':UA}
	try:
		req = urllib2.Request(url = target, data = post, headers = headers)
		resp = urllib2.urlopen(req)
		CE = resp.headers.get('content-encoding')
		http = resp.read()
		resp.close()
		return http
	except Exception, e:
		xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
		showMessage('HTTP ERROR', e, 5000)



genres_dat_file = os.path.join(addon_path, 'genres.dat')
genres_data = {}
if os.path.isfile(genres_dat_file):
	try:
		gdf = open(genres_dat_file, 'r')
		genres_data = json.loads(gdf.read())
		gdf.close()
	except: pass

countries_dat_file = os.path.join(addon_path, 'countries.dat')
countries_data = {}
if os.path.isfile(countries_dat_file):
	try:
		cdf = open(countries_dat_file, 'r')
		countries_data = json.loads(cdf.read())
		cdf.close()
	except: pass

years_dat_file = os.path.join(addon_path, 'years.dat')
years_data = []
if os.path.isfile(years_dat_file):
	try:
		ydf = open(years_dat_file, 'r')
		years_data = json.loads(ydf.read())
		ydf.close()
	except: pass


def genre2name(gid):
	try:
		reti = genres_data[str(gid)].encode('utf-8')
		return reti
	except: return None

def countrie2name(cid):
	try:
		reti = countries_data[str(cid)].encode('utf-8')
		return reti
	except: return None


def root(params):
	genres = {}
	basep = {'from':0, 'to':show_len-1, 'sort':'new', 'func':'browse'} # TODO new/pop
	http = GET('http://www.ivi.ru/mobileapi/categories/')
	if http:

		i = xbmcgui.ListItem('[ Поиск ]', iconImage = addon_icon, thumbnailImage = addon_icon)
		i.setProperty('fanart_image', addon_fanart)
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'from':0, 'to':show_len-1, 'func':'search'}))
		xbmcplugin.addDirectoryItem(h, uri, i, True)

		i = xbmcgui.ListItem('[ Выбрать год ]', iconImage = addon_icon, thumbnailImage = addon_icon)
		i.setProperty('fanart_image', addon_fanart)
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'from':0, 'to':show_len-1, 'func':'yselector'}))
		xbmcplugin.addDirectoryItem(h, uri, i, True)

		i = xbmcgui.ListItem('[ Выбрать страну ]', iconImage = addon_icon, thumbnailImage = addon_icon)
		i.setProperty('fanart_image', addon_fanart)
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'from':0, 'to':show_len-1, 'func':'cselector'}))
		xbmcplugin.addDirectoryItem(h, uri, i, True)


		for categoryes in json.loads(http):
			if categoryes['title'] != u'Музыка':
				i = xbmcgui.ListItem(categoryes['title'], iconImage = addon_icon, thumbnailImage = addon_icon)
				i.setProperty('fanart_image', addon_fanart)
				basep['category'] = categoryes['id']
				uri = '%s?%s' % (sys.argv[0], urllib.urlencode(basep))
				del basep['category']
				xbmcplugin.addDirectoryItem(h, uri, i, True)
				for genre in categoryes['genres']:
					genres[genre['id']] = categoryes['title']
					i = xbmcgui.ListItem('%s : %s' % (categoryes['title'], genre['title']), iconImage = addon_icon, thumbnailImage = addon_icon)
					i.setProperty('fanart_image', addon_fanart)
					basep['genre'] = genre['id']
					uri = '%s?%s' % (sys.argv[0], urllib.urlencode(basep))
					del basep['genre']
					xbmcplugin.addDirectoryItem(h, uri, i, True)




		gf = open(genres_dat_file, 'w')
		gf.write(json.dumps(genres))
		gf.close()

		xbmcplugin.endOfDirectory(h)

	countries = GET('http://www.ivi.ru/mobileapi/countries/')
	if countries:
		cf = open(countries_dat_file, 'w')
		cf.write(countries)
		cf.close()

	yearsl = GET('http://www.ivi.ru/mobileapi/videos/years/')
	if yearsl:
		yf = open(years_dat_file, 'w')
		yf.write(yearsl)
		yf.close()


def yselector(params):
	for yy in years_data:
		i = xbmcgui.ListItem(str(yy), iconImage = addon_icon, thumbnailImage = addon_icon)
		i.setProperty('fanart_image', addon_fanart)
		params['year_from'] = yy
		params['year_to']   = yy
		params['func']   = 'browse'
		print params
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode(params))
		xbmcplugin.addDirectoryItem(h, uri, i, True)
	xbmcplugin.endOfDirectory(h)


def cselector(params):
	for cc in countries_data:
		i = xbmcgui.ListItem(countries_data[cc], iconImage = addon_icon, thumbnailImage = addon_icon)
		i.setProperty('fanart_image', addon_fanart)
		params['country'] = cc
		params['func']   = 'browse'
		print params
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode(params))
		xbmcplugin.addDirectoryItem(h, uri, i, True)
	xbmcplugin.endOfDirectory(h)


def search(params):
	kbd = xbmc.Keyboard()
	kbd.setDefault('')
	kbd.setHeading('Поиск по IVI')
	kbd.doModal()
	if kbd.isConfirmed():
		params['query'] = kbd.getText()
		params['url'] = 'http://www.ivi.ru/mobileapi/search/?%s'
		browse(params)



def get_metadata(video):
	try:    v_id = video['id'] # идентификатор контента
	except: v_id = None
	try:    v_title = video['title'].encode('utf-8') # название контента
	except: v_title = None
	try:    v_cats = video['categories'] # список идентификаторов категории []
	except: v_cats = None
	try:    v_genres = video['genres'] # список идентификаторов жанров []
	except: v_genres = None
	try:    v_thumbnails = video['thumbnails'] # список изображений контента []
	except: v_thumbnails = None
	try:    v_country = video['country'] # Идентификатор страны
	except: v_country = None
	try:    v_descr = video['descrtiption'].encode('utf-8') # описание контента
	except: v_descr = None
	try:    v_years = video['year'] # год выхода контента []
	except: v_years = None
	try:    v_ivi_rating = video['ivi_rating'] # рейтинг рассчитанный на основании голосов пользователей ivi
	except: v_ivi_rating = None
	try:    v_kp_rating = video['kp_rating'] # рейтинг ресурса КиноПоиск
	except: v_kp_rating = None
	try:    v_imdb_rating = video['imdb_rating'] # рейтинг ресурса рейтинг ресурса IMDB
	except: v_imdb_rating = None
	try:    v_compilation = video['compilation'] # Название сборника
	except: v_compilation = None
	try:    v_total_contents = video['total_contents'] # число контента в сборнике
	except: v_total_contents = None
	try:    v_hru = video['hru'].encode('utf-8') # хру для показа сборника
	except: v_hru = None
	try:    v_seasons_count = video['seasons_count'] # количество сезонов
	except: v_seasons_count = None
	try:    v_seasons = video['seasons'] # список сезонов
	except: v_seasons = None
#	print '=============================================================================='
#	print '             идентификатор контента = [%s]' % v_id
#	print '                  название контента = [%s]' % v_title
#	print 'список идентификаторов категории [] = [%s]' % v_cats
#	print '   список идентификаторов жанров [] = [%s]' % v_genres
#	print '     список изображений контента [] = [%s]' % v_thumbnails
#	print '               Идентификатор страны = [%s]' % v_country
#	print '                  описание контента = [%s]' % v_descr
#	print '             год выхода контента [] = [%s]' % v_years
#	print '                        рейтинг IVI = [%s]' % v_ivi_rating
#	print '                  рейтинг КиноПоиск = [%s]' % v_kp_rating
#	print '                       рейтинг IMDB = [%s]' % v_imdb_rating
#	print ''
#	print '                  Название сборника = [%s]' % v_compilation
#	print '          число контента в сборнике = [%s]' % v_total_contents
#	print '            хру для показа сборника = [%s]' % v_hru
#	print '                 количество сезонов = [%s]' % v_seasons_count
#	print '                     список сезонов = [%s]' % v_seasons
#	print '=============================================================================='
	if v_id and v_title:
		info = {}
		#if v_hru:
		#	info['plotoutline'] = v_hru
		lth = 0
		ltw = 0
		ltu = addon_icon
		for thumbnail in v_thumbnails:
			try:
				if int(thumbnail['height']) > lth:
					ltu = thumbnail['path']
					lth = int(thumbnail['height'])
					ltw = int(thumbnail['width'])
			except:
				try: ltu = thumbnail['path']
				except: pass



		plotoutline_arr = []

		if v_descr: info['plot'] = str(v_descr)

		years = []

		if v_years:
			try:
				for yy in v_years:
					if yy:
						years.append(int(yy))
			except:
				try:
					years.append(int(v_years))
					info['year'] = min(years)
				except: pass

		tname = ''
		# v_cats - ?
		if v_seasons_count:
			if int(v_seasons_count) == 1:
				tname = '. Многосерийный.'
				plotoutline_arr.append('Тип: Многосерийный фильм')
			elif int(v_seasons_count) > 1:
				tname = '. Сериал.'
				plotoutline_arr.append('Тип: Сериал')


		# ------------ Ratings -------------------- #
		#v_ivi_rating,v_kp_rating,v_imdb_rating
		rates = []
		if v_ivi_rating:  rates.append(float(v_ivi_rating))
		if v_kp_rating:   rates.append(float(v_kp_rating))
		if v_imdb_rating: rates.append(float(v_imdb_rating))
		if len(rates):
			info['rating'] = max(rates)

		# ------------ формовка жанров ------------ #
		glist = []
		if v_genres:
			for gid in v_genres:
				g_name = genre2name(gid)
				if g_name:
					try: glist.index(g_name)
					except: glist.append(g_name)
		if len(glist):
			info['genre'] = ', '.join(glist)
		# ----------------------------------------- #
		clist = []
		if v_country:
			#for cid in v_country:
			c_name = countrie2name(v_country)
			if c_name:
				clist.append(c_name)
				plotoutline_arr.append('Страна: %s' % c_name)

		if len(years):
			#years_l = ', '.join(years)

			max_y = max(years)
			min_y = min(years)
			clist.append(str(min_y))
			if max_y == min_y:
				plotoutline_arr.append('Год: %s' % max_y)
			else:
				plotoutline_arr.append('Годы: %s-%s' % (min_y, max_y))

		if len(clist):
			#clists =
			#if not (v_total_contents and v_seasons_count and v_seasons):
			v_title = '%s (%s)%s' % (v_title, ', '.join(clist), tname)



		if len(plotoutline_arr):
			info['plotoutline'] = ', '.join(plotoutline_arr)
		# ----------------------------------------- #

		if ltw > lth:
			info['season'] = 0
			info['episode'] = 0

		info['title'] = v_title
		reti = {'infoLabels': info, 'id': v_id, 'image': ltu, 'tc': v_total_contents, 'sc': v_seasons_count}
		return reti

	else:
		return False


def browse(params):
	try:
		target = params['url']
		del params['url']
	except: target = 'http://www.ivi.ru/mobileapi/catalogue/?%s'

	http = GET(target % urllib.urlencode(params))
	if http == None: return False
	jsdata = json.loads(http)

	if jsdata:
		if len(jsdata):
			i = xbmcgui.ListItem('[ Поиск в этом разделе ]', iconImage = addon_icon, thumbnailImage = addon_icon)
			i.setProperty('fanart_image', addon_fanart)
			params['url']  = target
			params['func'] = 'search'
			#params['from'] = int(params['to']) + 1
			#params['to'] = params['from'] + show_len
			uri = '%s?%s' % (sys.argv[0], urllib.urlencode(params))
			xbmcplugin.addDirectoryItem(h, uri, i, True)

	for video in jsdata:
		data = get_metadata(video)
		if data:
			i = xbmcgui.ListItem(data['infoLabels']['title'], iconImage = data['image'], thumbnailImage = data['image'])
			if data['tc'] or data['sc']:
				isFolder = True
				if data['sc'] > 1:
					osp = {'func':'seasons', 'id': data['id'], 'seasons_count': data['sc']}
					uri = '%s?%s' % (sys.argv[0], urllib.urlencode(osp))
				elif data['sc'] == 1:
					osp = {'func':'browse', 'id': data['id'], 'url': 'http://www.ivi.ru/mobileapi/videofromcompilation/?%s'}
					uri = '%s?%s' % (sys.argv[0], urllib.urlencode(osp))
				else: xbmc.log( '[%s]: unexpected value v_seasons_count=%s' % (addon_id, data['sc']), 2 )
			else:
				isFolder = False
				#i.setProperty('IsPlayable', 'true')
				uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'play', 'id': data['id']}))
			i.setInfo(type = 'video', infoLabels = data['infoLabels'])
			i.setProperty('fanart_image', addon_fanart)
			xbmcplugin.addDirectoryItem(h, uri, i, isFolder)

	if len(jsdata) == show_len:
		i = xbmcgui.ListItem('Еще!', iconImage = addon_icon, thumbnailImage = addon_icon)
		i.setProperty('fanart_image', addon_fanart)
		params['url']  = target
		params['func'] = 'browse'
		params['from'] = int(params['to']) + 1
		params['to'] = params['from'] + show_len
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode(params))
		xbmcplugin.addDirectoryItem(h, uri, i, True)

	xbmcplugin.endOfDirectory(h)

def seasons(params):
	v_seasons_count = int(params['seasons_count'])
	v_id = int(params['id'])
	while v_seasons_count > 0:
		i = xbmcgui.ListItem('Сезон %s' % v_seasons_count, iconImage = addon_icon, thumbnailImage = addon_icon)
		i.setProperty('fanart_image', addon_fanart)
		osp = {'func':'browse', 'id': v_id, 'url': 'http://www.ivi.ru/mobileapi/videofromcompilation/?%s', 'season':v_seasons_count}
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode(osp))
		i.setInfo(type = 'video', infoLabels = {'season': v_seasons_count})
		xbmcplugin.addDirectoryItem(h, uri, i, True)
		v_seasons_count -= 1
	xbmcplugin.endOfDirectory(h)


# =============================== Заствка плеера =============================== #
#class iviSplash(xbmcgui.Window):
#	def __init__(self):
#		self.setCoordinateResolution(1) # 0 for 1080
#		self.addControl(xbmcgui.ControlImage(0, 0, 1280, 720, os.path.join(os.getcwd().replace(';', ''), 'fanart.jpg')))
#		self.strCopyrightOverlay = xbmcgui.ControlLabel(25, 25, 1000, 50, '', 'font18', '0xFFFFFFFF')
#		self.addControl(self.strCopyrightOverlay)
#		self.strStatusInfo = xbmcgui.ControlLabel(25, 680, 1000, 50, '', 'font10', '0xFFFFFFFF')
#		self.addControl(self.strStatusInfo)
#	def setStatusInfo(self, Str):
#		self.strStatusInfo.setLabel(Str)
#	def setCopyrightOverlay(self, Str):
#		self.strCopyrightOverlay.setLabel(Str)


# ================================= Курящий плеер ================================== #
class WatchPlayer(xbmc.Player):

	def POSTAPI(self, post):
		req = urllib2.Request(self.api_url)
		req.add_header('User-Agent', UA)
		f = urllib2.urlopen(req, json.dumps(post))
		js = json.loads(f.read())
		f.close()
		try:
			e_m = js['error']
			showMessage('Ошибка %s сервера %s' % (e_m['code'], js['server_name'].encode('utf-8')), e_m['message'].encode('utf-8'), times = 15000, pics = addon_icon)
			return None
		except:
			print js
			return js

	def find_best(self, data, isAd):
		play_file = None
		if not play_file:
			for vcfl in data['files']:
				if vcfl['content_format'] == 'MP4-hi': play_file = vcfl['url']
		if not play_file:
			for vcfl in data['files']:
				if vcfl['content_format'] == 'FLV-hi': play_file = vcfl['url']
		if not play_file:
			for vcfl in data['files']:
				if vcfl['content_format'] == 'MP4-lo': play_file = vcfl['url']
		if not play_file:
			for vcfl in data['files']:
				if vcfl['content_format'] == 'FLV-lo': play_file = vcfl['url']
		return play_file

	def __init__(self):
		self.pd = xbmcgui.DialogProgress()
		self.pd.create('Digital Access', 'Выполняется инициализация плеера.', 'Это займет некоторое время.', 'Пожалуйста подождите...')
		self.sID = '5' # 's15'
		self.ad_bw = 2000
		self.api_url = 'http://partner.digitalaccess.ru/api/json/'
		self.PlayList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		self.PlayList.clear()
		xbmc.Player.__init__(self)

	#--------------------------------------------------------------------------------------------------------------------------------------#
	def OpenID(self, vID):
		self.vID = str(vID)
		self.TotalTime = 0.0
		self.Time = 0.0
		self.percent = 0
		self.preroll_params = []
		self.postroll_params = []
		self.midroll_params = []
		self.player_current_file = None  # Куррент-файл плеера
		self.player_total_time = None    # Время
		self.player_current_time = None  # Текущее время
		self.content_file = None
		self.content_percent_to_mark = 0
		self.content_title = None
		self.content_id = None
		self.content_midroll = None
		self.main_item = None

		self.midroll_return_time = None
		#self.ad_level = None # 0 - postroll/midroll/postroll, 1 - midroll/postroll ... 2 - postroll

		self.copyright_overlay = None # Авторская плашка
		self.PlayBackStarted = False
		self.infoLabels = None
		self.PosterImage = None


		##################

		#self.ad_level = 0

		self.preroll_params = [
			{'url': 'http://188.127.230.154/adv/1.flv', 'id': '-1', 'title': 'reklama1', 'px_audit': 'http://188.127.230.154/1', 'duration': 6, 'percent_to_mark': 50, 'save_show': True},
			{'url': 'http://188.127.230.154/adv/2.flv', 'id': '-2', 'title': 'reklama2', 'px_audit': 'http://188.127.230.154/2', 'duration': 14, 'percent_to_mark': 70, 'save_show': True}
		]

		self.postroll_params = [
			{'url': 'http://188.127.230.154/adv/3.flv', 'id': '-3', 'title': 'reklama3', 'px_audit': 'http://188.127.230.154/3', 'duration': 14, 'percent_to_mark': 30, 'save_show': True},
			{'url': 'http://188.127.230.154/adv/4.flv', 'id': '-4', 'title': 'reklama4', 'px_audit': 'http://188.127.230.154/4', 'duration': 15, 'percent_to_mark': 0, 'save_show': True}
		]

		self.midroll_params = [
			{'url': 'http://188.127.230.154/adv/5.flv', 'id': '-5', 'title': 'reklama5', 'px_audit': 'http://188.127.230.154/5', 'duration': 15, 'percent_to_mark': 50, 'save_show': True},
			{'url': 'http://188.127.230.154/adv/6.flv', 'id': '-6', 'title': 'reklama6', 'px_audit': 'http://188.127.230.154/6', 'duration': 8, 'percent_to_mark': 70, 'save_show': True}
		]
		self.copyright_overlay = 'Тестовове видео'

		self.infoLabels = {'title': 'Интеллигенция и политика'}
		self.PosterImage = 'http://img2.russia.ru/12816/big.jpg'

		self.content_file = 'http://83.222.2.211/12816/sd.mp4'

		self.content_percent_to_mark = 80
		self.content_title = 'TEST'
		self.content_id = 0
		self.content_midroll = [5, 16]
		##################


		self.pd.update(5)

		########self.getContent()

		if self.content_file:
			self.stop()
			self.PlayList.clear()

			self.pd.update(20)
			########self.getAds()
			if self.content_file:
				self.pd.update(60)
				self.main_item = xbmcgui.ListItem(self.infoLabels['title'], iconImage = self.PosterImage, thumbnailImage = self.PosterImage)
				self.main_item.setInfo(type = 'video', infoLabels = self.infoLabels)
				if self.preroll_params:
					if len(self.preroll_params):
						self.player_current_file = self.preroll_params[0]['url']
						self.play(self.player_current_file, self.main_item)
					else: self.play(self.content_file, self.main_item)
				else: self.play(self.content_file, self.main_item)
				self.pd.update(100)

	#--------------------------------------------------------------------------------------------------------------------------------------#
	def getContent(self):

		http = GET('http://www.ivi.ru/mobileapi/videoinfo/?id=%s' % self.vID)
		if http:
			data = get_metadata(json.loads(http))
			if data:
				self.infoLabels = data['infoLabels']
				self.PosterImage = data['image']

				json0 = self.POSTAPI({'method':'da.content.get', 'params':[self.vID, {'site':self.sID} ]})
				if json0:
					try:
						vc = json0['result']
						self.content_file = self.find_best(vc, False)
						if self.content_file:
							try:
								if vc['copyright_overlay']:
									if len(vc['copyright_overlay']):
										self.copyright_overlay = vc['copyright_overlay'].encode('utf-8')
							except: self.copyright_overlay = None

							try:    self.content_percent_to_mark = int(vc['percent_to_mark'])-1
							except: self.content_percent_to_mark = 0
							try:
								vc_midroll = vc['midroll']
								if type(vc_midroll) == 'NoneType':
									self.content_midroll = None
								elif type(vc_midroll) == 'int':
									self.content_midroll = [vc_midroll]
								elif type(vc_midroll) == 'str':
									self.content_midroll = [str(vc_midroll)]
								elif type(vc_midroll) == 'list':
									self.content_midroll = vc_midroll
							except: self.content_midroll = None
							self.content_id = vc['id']
							self.content_title = vc['title'].encode('utf-8')
					except: pass

	#--------------------------------------------------------------------------------------------------------------------------------------#
	def getAds(self):
		json1 = self.POSTAPI({'method':'da.content.get_adv','params':[self.vID,{'site':self.sID,'bandwidth':self.ad_bw,'previous_videos':{'day':{},'week':{},'month':{},'hour':{}},'previous_orders':{'day':{},'week':{},'month':{},'hour':{}}}]})
		if json1:
			try:
				for ad in json1['result']:
					ad_file = self.find_best(ad, True)
					if ad_file:
						adrow = {'url': ad_file, 'id': ad['id'], 'title': ad['title'].encode('utf-8'), 'px_audit': ad['px_audit'],
						'duration': ad['duration'], 'percent_to_mark': int(ad['percent_to_mark'])-1, 'save_show': ad['save_show']}
						if ad['type'] == 'preroll': self.preroll_params.append(adrow)
						elif ad['type'] == 'postroll': self.postroll_params.append(adrow)
						elif ad['type'] == 'midroll':self.midroll_params.append(adrow)
			except:
				print ' EXCEPT ********* НЕТ РЕКЛАМЫ ************ '
				showMessage('EXCEPT', 'НЕТ РЕКЛАМЫ', 3000)
	#--------------------------------------------------------------------------------------------------------------------------------------#
	def clean_ad_params(self, ad_params_list):
		if ad_params_list:
			if len(ad_params_list):
					x = 0
					for current_ad in ad_params_list:
						if str(current_ad['url']) == str(self.player_current_file):
							ad_params_list.pop(x)
						x += 1
			if len(ad_params_list) == 0: ad_params_list = None

	#--------------------------------------------------------------------------------------------------------------------------------------#
	def onPlayBackStarted(self): # Будет вызываться при XBMC начинает играть файл
		self.pd.close()
		print ' ****************************** onPlayBackStarted(self)'
		#self.PlayBackStarted = True
		#self.player_current_file = self.getPlayingFile(self)
		#print 'CURRENT PLAYER FILE = %s' % self.player_current_file

		if self.player_current_file == self.content_file:
			if self.copyright_overlay:
				showMessage('Авторская плашка', self.copyright_overlay, 5000)

		if self.midroll_return_time:
			#print
			self.seekTime(self.midroll_return_time)
			showMessage('Промотка на', str(self.midroll_return_time), 3000)
			self.midroll_return_time = None


		#self.PlayList.clear()
	#--------------------------------------------------------------------------------------------------------------------------------------#
	def onPlayBackEnded(self): # Будет вызываться при XBMC концов воспроизведении файла
		showMessage('onPlayBackEnded', 'onPlayBackEnded', 1000)

		self.stop()
		self.PlayList.clear()
		xbmc.sleep(300)


		print ' ****************************** onPlayBackEnded(self)'
		print 'CURRENT PLAYER FILE PLAY END= %s' % self.player_current_file
		print 'Play NEXT FIle....'

		self.clean_ad_params(self.preroll_params)

		if self.preroll_params:
			if len(self.preroll_params):
				self.player_current_file = self.preroll_params[0]['url']
				self.play(self.player_current_file, self.main_item)

		else:
			showMessage('Прероллов нет', 'Воспр. контент...', 1000)
			self.player_current_file = self.content_file
			self.play(self.player_current_file, self.main_item)

		print '====================== 50 ======================'

#		if len(self.midroll_params) > 0:
#			if self.player_current_file == self.midroll_params[0]['url']:
				#print 'START NEW PLAY.........'

				#print 'PL LEN', self.PlayList.__len__()
				#print 'PL POS', self.PlayList.getposition()
				#self.PlayList.clear()
				#xbmc.sleep(500)
#				self.midroll_params.pop([0])
				#self.content_file = self.midroll_params[0]['url']
				#self.play(self.content_file, self.main_item)
				#xbmc.sleep(500)
#				print 'Continue play....'
#				self.player_current_file = self.content_file
#				self.play(self.player_current_file, self.main_item)


#			else:
#				print '1'
#				if not self.preroll_params:
#					print '2'
#					if self.content_file:
#						print '3'
#						#self.PlayList.clear()
						#xbmc.sleep(500)
#						self.player_current_file = self.content_file
#						self.play(self.content_file, self.main_item)

#		else:
#			print '4'
#			if not self.preroll_params:
#				print '5'
#				if self.content_file:
#					print '6'
					#self.PlayList.clear()
					#xbmc.sleep(500)
#					self.player_current_file = self.content_file
#					self.play(self.content_file, self.main_item)
			#self.play(self.content_file)

			#self.clead_ad_params(self.midroll_params)
		#self.clead_ad_params(self.postroll_params)

		#self.clead_ad_params(self.midroll_params)

	#--------------------------------------------------------------------------------------------------------------------------------------#
	# Если пользователь нажал X
	def onPlayBackStopped(self): # Будет вызываться, когда пользователь прекращает XBMC воспроизведении файла
		print ' ****************************** onPlayBackStopped(self)'
		#self.content_file = False

	#--------------------------------------------------------------------------------------------------------------------------------------#
	def report_ad_params(self, ad_params_list, lock_percent):
		if ad_params_list:
			if len(ad_params_list):
					x = 0
					for current_ad in ad_params_list:
						if str(current_ad['url']) == str(self.player_current_file):
							if current_ad['percent_to_mark']:
								if self.percent > current_ad['percent_to_mark']:
									print '------- ОТПРАВКА ОТЧЕТА О ПРОСМОТРЕ РЕКЛАМЫ ------------'
									print 'AD', current_ad
									print 'CF', self.player_current_file
									print 'PC', self.percent
									#POSTAPI({'method':'da.content.adv_watched', 'params':[vID, adsID, {'site':sID}]})
									#PxAudit in PxAudits: GET(PxAudit)
									showMessage('REKLAMA', 'ОТПРАВКА ОТЧЕТА О ПРОСМОТРЕ РЕКЛАМЫ', 3000)
									if lock_percent:
										ad_params_list.pop(0)
										ad_params_list[x]['percent_to_mark'] = None

						x += 1



	#--------------------------------------------------------------------------------------------------------------------------------------#
	def start_loop(self):

		while self.content_file:

			#try: self.player_current_file = self.getPlayingFile()
			#except: self.player_current_file = None

			try:
				self.TotalTime = self.getTotalTime()
				self.Time = self.getTime()
				self.percent = (100 * self.Time) / self.TotalTime
				print 'PERCENT = [%s]' % self.percent
			except: self.percent = 0

			self.report_ad_params(self.preroll_params, True)
			self.report_ad_params(self.midroll_params, False)
			self.report_ad_params(self.postroll_params, True)

			if self.content_file == self.player_current_file:
				#print 'if self.content_file) == self.player_current_file:'
				if self.content_percent_to_mark:
					#print '... if self.content_percent_to_mark:'
					if self.percent > self.content_percent_to_mark:
						#print 'if self.percent > self.content_percent_to_mark:'
						print '------- ОТПРАВКА ОТЧЕТА О ПРОСМОТРЕ КОНТЕНТА ------------'
						print 'CF', self.player_current_file
						print 'PC', self.percent
						print 'ID', self.content_id
						self.content_percent_to_mark = None
						showMessage('Контент', 'отправлен отчет о просмотре')
						#	POSTAPI({'method':'da.content.content_watched', 'params':[vc_id, {'site':sID}]})


				# Нужны временные метки и наличие мидроллов
				if self.midroll_params and self.content_midroll:
					if len(self.midroll_params) and (len(self.content_midroll)):
						# Если попал в список меток и играет файл контента
						if (int(self.Time) in self.content_midroll) and (self.player_current_file == self.content_file):
							self.midroll_return_time = int(self.Time)
							self.player_current_file = self.midroll_params[0]['url']
							self.stop()
							self.PlayList.clear()
							xbmc.sleep(300)
							#xbmc.sleep(250)
							self.content_midroll.pop(0)
							self.play(self.player_current_file, self.main_item)



			xbmc.sleep(100)
		print 'loop END!'

#---------------------------------------------------------------------------------------------------------------------------------#

#	def pause(self):
#	def play(self, item = None, listItem = None):
#	def playnext(self):
#	def playprevious(self):
#	def playselected(self):
#	def seekTime(self, secs): # Ищет указанный промежуток времени, как на доли секунды. Исключение, если игрок не играет файл.
#	def stop(self):
#	def setStatusInfo(self, Str):
#		self.splash.setStatusInfo(Str)
#	def setCopyrightOverlay(self, Str):
#		self.splash.setCopyrightOverlay(Str)
#	def getPlayingFile(self):	# возвращает текущее проигрываемого файла в виде строки. Исключение, если игрок не играет файл.
#	def getTime(self): # Возвращает текущее время текущей игры СМИ, как на доли секунды. Исключение, если игрок не играет файл.
#	def getTotalTime(self): # Возвращает общее время текущей игры в средствах массовой информации. Исключение, если игрок не играет файл.
#	def getVideoInfoTag(self): # возвращает VideoInfoTag текущего фильме играет. Исключение, если игрок не играет файл.
#	def isPlaying(self): # Возвращает True, является XBMC играет файл.
#	def isPlayingAudio(self):
#	def isPlayingVideo(self):
#	def close(self):
#		self.splash.close()



def play(params):
	xbmc_player = WatchPlayer()
	xbmc_player.OpenID(params['id'])
	xbmc_player.start_loop()


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
		del params['func']
	except:
		func = None
		xbmc.log( '[%s]: Primary input' % addon_id, 1 )
		root(params)
	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
