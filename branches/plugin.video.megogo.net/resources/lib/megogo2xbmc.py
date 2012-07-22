#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) MEGOGO.NET. All rights reserved.
# Copyright (c) XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# Writer (c) 2012, Kostynoy S.A., E-mail: seppius2@gmail.com
# https://docs.google.com/document/d/1KSuN3WqpzxS1wioS8N435PlIAZYU-BJdz5ZifVyNpfw/edit

import urllib
import urllib2
import hashlib
import sys
import os
import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon

__addon__ = xbmcaddon.Addon( id = 'plugin.video.megogo.net' )
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
xbmcplugin.setContent(hos, 'movies')

UA = '%s/%s %s/%s/%s' % (addon_type, addon_id, urllib.quote_plus(addon_author), addon_version, urllib.quote_plus(addon_name))


def showMessage(heading, message, times = 3000, pics = addon_icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

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
			
			
def GET(mCmd, mParams):
	req_p1 = []
	req_p2 = []
	if mParams:
		if len(mParams):
			for mKey in mParams:
				req_p1.append('%s=%s' % (mKey, urllib.quote_plus(mParams[mKey])))
				req_p2.append('%s=%s' % (mKey, mParams[mKey]))
	req_params = '&'.join(req_p1)
	req_hash = ''.join(req_p2)
	m = hashlib.md5()
	m.update('%s%s'%(req_hash,'ced6ad86a33defca'[::-1]))
	target = 'http://megogo.net/p/%s?%s&sign=%s' % (mCmd, req_params, '%s%s' % (m.hexdigest(), '_xbmc'))
	print 'GET: TARGET: %s' % target
	req = urllib2.Request(url = target, data = None, headers = {'User-Agent':UA})
	resp = urllib2.urlopen(req)
	http = resp.read()
	resp.close()

	#print http

	try:
		return json.loads(http)
	except:
		return None
		
#	if data['result'] != 'ok':
#		showMessage('ОШИБКА', 'Подробности в журнале', 5000)
#		print data
#		data = None
	
	
	

def mainScreen(params):
	session = None
	data = GET('login', {'login': __addon__.getSetting('username'), 'pwd':__addon__.getSetting('password')})
	if data:
		if data['result'] == 'ok':
			session = data['session']
			user = data['user']
			if len(user['nickname']):
				username = user['nickname']
			else:
				username = user['email']
			usr_avatar = 'http://megogo.net%s' % user['avatar_url']
			i = xbmcgui.ListItem('%s - MEGOGO.NET приветствует Вас!' % username.encode('utf-8'), iconImage = usr_avatar, thumbnailImage = usr_avatar)
			xbmcplugin.addDirectoryItem(hos, '', i, True)
		else:
			i = xbmcgui.ListItem('Вы не авторизованы. Проверьте Ваши логин и пароль в настройках дополнения.')
			xbmcplugin.addDirectoryItem(hos, '', i, False)
	
	
	data = GET('categories', [])
	if data:
		for cat in data['category_list']:
			title = '%s (%s)' % (cat['title'], cat['total_num'])
			urip = {'func':'videos', 'category': cat['id'], 'offset': 0, 'limit': 100 }
			if session: urip['session'] = session
			uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
			i = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = addon_icon)
			i.setProperty('fanart_image', addon_fanart)
			i.setInfo(type = 'video', infoLabels = {'title':title})
			xbmcplugin.addDirectoryItem(hos, uri, i, True)
		xbmcplugin.endOfDirectory(hos)

		
		
def videos(params):
	try:    session = params['session']
	except: session = None
	data = GET('videos', params)
	if data:
		for video in data['video_list']:
			poster = u'http://megogo.net%s' % video['poster']
			i = xbmcgui.ListItem('%s (%s)' % (video['title'], video['title_orig']), iconImage = poster , thumbnailImage = poster)
			i.setProperty('fanart_image', video['poster'])
			urip = {'func':'play', 'video': video['id']}
			if session: urip['session'] = session
			uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
			i.setProperty('IsPlayable', 'true')
			i.setInfo(type = 'video', infoLabels = {'title':video['title']})
			xbmcplugin.addDirectoryItem(hos, uri, i, False)

		i = xbmcgui.ListItem('ЕЩЕ!', iconImage = addon_icon , thumbnailImage = addon_icon)
		i.setProperty('fanart_image', addon_fanart)
		
		params['func'] = 'videos'
		params['offset'] = int(params['offset']) + int(params['limit']) # TODO x3
		
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode(params))

		i.setInfo(type = 'video', infoLabels = {'title':'ЕЩЕ!'})

		xbmcplugin.addDirectoryItem(hos, uri, i, True)
			
			
		xbmcplugin.endOfDirectory(hos)

		
#def genres(params):
#	data = GET('genres', params)
#	if data:
#		for cat in data['category_list']:
#			i = xbmcgui.ListItem('%s (%s)' % (cat['title'], cat['total_num']), iconImage = addon_icon, thumbnailImage = addon_icon)
#			i.setProperty('fanart_image', addon_fanart)
#			uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'openCat', 'cat_id': cat['id']}))
#			xbmcplugin.addDirectoryItem(hos, uri, i, True)
#		xbmcplugin.endOfDirectory(hos)



def play(params):
	data = GET('info', params)
	i = xbmcgui.ListItem( path = data['src'] )
	xbmcplugin.setResolvedUrl(hos, True, i)


	
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
		mainScreen(params)
	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
