#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Writer (c) 23/06/2011, Khrysev D.A., E-mail: x86demon@gmail.com
#
#   This Program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2, or (at your option)
#   any later version.
#
#   This Program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; see the file COPYING.  If not, write to
#   the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#   http://www.gnu.org/licenses/gpl.html

import httplib
import urllib
import urllib2
import re
import sys
import os
import Cookie

import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import xbmcaddon




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

hos = int(sys.argv[1])
show_len=50


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


def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

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

def showMessage(heading, message, times = 3000, pics = addon_icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

headers  = {
	'User-Agent' : 'XBMC',
	'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
	'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
	'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
	'Accept-Encoding':'identity, *;q=0'
}

def GET(target, post=None):
	#print target
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

def mainScreen(params):
	#li = xbmcgui.ListItem('[Категории]')
	#uri = construct_request({
#		'href': httpSiteUrl,
	#	'mode': 'getCategories'
	#})
	#xbmcplugin.addDirectoryItem(hos, uri, li, True)

	#i = xbmcgui.ListItem('[Поиск]', iconImage = addon_icon, thumbnailImage = addon_icon)
	#uri = construct_request({

	#	'func': 'runSearch'
	#})
	#xbmcplugin.addDirectoryItem(hos, uri, i, True)
	readCat('gg')
	xbmcplugin.endOfDirectory(hos)

def runearch(params):
	kbd = xbmc.Keyboard()
	kbd.setDefault('')
	kbd.setHeading('Поиск по IVI')
	kbd.doModal()
	if kbd.isConfirmed():
		params['query'] = kbd.getText()
		params['url'] = 'http://www.ivi.ru/mobileapi/search/?%s'
		#print params['url']
		browse(params)
		
def get_sort():

	if __addon__.getSetting("sort_v") == '1': return 'pop'
	else: return 'new'
	
def readCat(params):
	try:
		categ = params['category']
		del params['category']
	except:	categ = None
	basep = {'from':0, 'to':50, 'sort':get_sort(), 'func':'readCat'}
	#showMessage('Internal debug', 'Function "%s"' % get_sort(), 2000)
	http = GET('http://www.ivi.ru/mobileapi/categories/')
	jsdata = json.loads(http)
	if categ:
		if jsdata:
			for categoryes in jsdata:
				if categoryes['id'] == int(categ):
					flist=categ
					#print flist
					for genre in categoryes['genres']:
						i = xbmcgui.ListItem(genre['title'], iconImage = addon_icon, thumbnailImage = addon_icon)
						basep['func'] = 'getlistcat'
						basep['genre'] = genre['id']
						uri = '%s?%s' % (sys.argv[0], urllib.urlencode(basep))
						#print uri
						del basep['genre']
						xbmcplugin.addDirectoryItem(hos, uri, i, True)
					basep['func'] = 'getlistcat'
					basep['category'] = categ
					getlistcat(basep)
	else:	
		if http:
			for categoryes in json.loads(http):
				i = xbmcgui.ListItem(categoryes['title'], iconImage = addon_icon, thumbnailImage = addon_icon)
				i.setProperty('fanart_image', addon_fanart)
				basep['category'] = categoryes['id']
				categ = categoryes['id']
				uri = '%s?%s' % (sys.argv[0], urllib.urlencode(basep))
				xbmcplugin.addDirectoryItem(hos, uri, i, True)
	xbmcplugin.endOfDirectory(hos)


def runSearch(params):
	kbd = xbmc.Keyboard()
	kbd.setDefault('')
	kbd.setHeading('Поиск по IVI')
	kbd.doModal()
	if kbd.isConfirmed():
		params['query'] = kbd.getText()
		params['url'] = 'http://www.ivi.ru/mobileapi/search/?%s'
		sts=kbd.getText();
		#print sts.encode('utf-8')
		params['url'] = 'http://www.ivi.ru/mobileapi/search/?query=' + sts
		browse(params)

def getlistcat(params):
	try:
		target = params['url']
		del params['url']
	except: target = 'http://www.ivi.ru/mobileapi/catalogue/?%s'
	params['sort'] = get_sort()
	http = GET(target % urllib.urlencode(params))
	if http == None: return False
	jsdata = json.loads(http)
	
	#showMessage('Internal debug', 'Function "%s"' % get_sort(), 2000)
	if jsdata:

		for video in jsdata:
			data = get_metadata(video)
			if data:
				#print data['id']
				i = xbmcgui.ListItem(data['infoLabels']['title'], iconImage = data['image'], thumbnailImage = data['image'])
				if data['tc'] or data['sc']:
					isFolder = True
					if data['sc'] > 1:
						osp = {'func':'seasons', 'id': data['id'], 'seasons_count': data['sc']}
						uri = '%s?%s' % (sys.argv[0], urllib.urlencode(osp))
					elif data['sc'] <= 1:
						osp = {'func':'getlistcat', 'id': data['id'], 'url': 'http://www.ivi.ru/mobileapi/videofromcompilation/?%s'}
						uri = '%s?%s' % (sys.argv[0], urllib.urlencode(osp))
					else: xbmc.log( '[%s]: unexpected value v_seasons_count=%s' % (addon_id, data['sc']), 2 )
				else:
					isFolder = False
					i.setProperty('IsPlayable', 'true')
					uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'play', 'id': data['id']}))
				i.setInfo(type = 'video', infoLabels = data['infoLabels'])
				i.setProperty('fanart_image', addon_fanart)
				xbmcplugin.addDirectoryItem(hos, uri, i, isFolder)
		if len(jsdata) == show_len:
			i = xbmcgui.ListItem('Еще [>>]', iconImage = addon_icon, thumbnailImage = addon_icon)
			i.setProperty('fanart_image', addon_fanart)
			params['func'] = 'getlistcat'
			params['from'] = int(params['to']) + 1
			params['to'] = params['from'] + show_len
			uri = '%s?%s' % (sys.argv[0], urllib.urlencode(params))
			xbmcplugin.addDirectoryItem(hos, uri, i, True)
		xbmcplugin.endOfDirectory(hos)


def seasons(params):
	v_seasons_count = int(params['seasons_count'])
	v_id = int(params['id'])
	while v_seasons_count > 0:
		i = xbmcgui.ListItem('Сезон %s' % v_seasons_count, iconImage = addon_icon, thumbnailImage = addon_icon)
		i.setProperty('fanart_image', addon_fanart)
		osp = {'func':'getlistcat', 'id': v_id, 'url': 'http://www.ivi.ru/mobileapi/videofromcompilation/?%s', 'season':v_seasons_count}
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode(osp))
		i.setInfo(type = 'video', infoLabels = {'season': v_seasons_count})
		#print uri
		xbmcplugin.addDirectoryItem(hos, uri, i, True)
		v_seasons_count -= 1
	xbmcplugin.endOfDirectory(hos)


def find_bst(dasta):

	play_file = None
	for vcfl in dasta['files']:
		if vcfl['content_format'] == 'MP4-hi': play_file = vcfl['url']
	if not play_file:
		for vcfl in dasta['files']:
			if vcfl['content_format'] == 'FLV-hi': play_file = vcfl['url']
	if not play_file:
		for vcfl in dasta['files']:
			if vcfl['content_format'] == 'MP4-lo': play_file = vcfl['url']
	if not play_file:
		for vcfl in dasta['files']:
			if vcfl['content_format'] == 'FLV-lo': play_file = vcfl['url']
	return play_file





def get_video_url(vid):

	#print 'getvurl'
	http = GET('http://www.ivi.ru/mobileapi/videofullinfo/?id=%s' % vid)
	if http:
		json0 = json.loads(http)
		if http:
			try:
				vc = json0['result']
				content_file = find_bst(vc)
				return content_file
			except:
				return None

def play(params):
	file = get_video_url(params['id'])
	http = GET('http://www.ivi.ru/mobileapi/videoinfo/?id=%s' % params['id'])
	if http:
		data = get_metadata(json.loads(http))
		infoLabels = data['infoLabels']
		PosterImage = data['image']
	mitem = xbmcgui.ListItem(infoLabels['title'], iconImage = PosterImage, thumbnailImage = PosterImage)
	i = xbmcgui.ListItem(path = file)
	xbmcplugin.setResolvedUrl(hos, True, i)



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
	xbmc.log( '[s]: play' , 2 )
	params = get_params(sys.argv[2])
	try:
		func = params['func']
		del params['func']
	except:
		func = None
		xbmc.log( '[%s]: Primary input' % addon_id, 1 )
		mainScreen(params)
	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
